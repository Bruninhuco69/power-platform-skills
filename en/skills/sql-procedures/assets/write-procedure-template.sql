-- =====================================================================
-- TEMPLATE · write procedure (declarative variant)
--
-- Sample domain: "order" with an event trail. Replace APP with the
-- project acronym and the table/column names with those of the REAL
-- ENVIRONMENT (the name comes from the environment, not from this template).
--
-- Requires SQL Server 2016 SP1+ (CREATE OR ALTER). Target: DEV database.
-- In production, the DDL of section 0 goes to the DBA (assets/dba-ddl-request-template.md).
--
-- Return contract: 1 result set, 1 row, 4 columns
--   status (success|warning|error) · description (ASCII CODE) · id (text) · url ('')
-- The flow turns the code into a sentence for the user.
-- Comments inside a SQL block: plain ASCII, no accents.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. Sample DDL (DEV)
-- ---------------------------------------------------------------------
IF OBJECT_ID(N'dbo.APP_Pedido', N'U') IS NULL
    CREATE TABLE dbo.APP_Pedido (
        Id_Pedido    INT IDENTITY(1, 1) NOT NULL
                          CONSTRAINT PK_APP_Pedido PRIMARY KEY,
        Nr_Protocolo      VARCHAR(12)  NOT NULL,
        Des_Status        NVARCHAR(20) NOT NULL
                          CONSTRAINT DF_APP_Pedido_Status DEFAULT N'aberto',
        Nom_Abvd_Unidade  VARCHAR(3)   NOT NULL,
        Flg_Situacao      BIT          NOT NULL
                          CONSTRAINT DF_APP_Pedido_Situacao DEFAULT 1,
        Dt_Inclusao       DATETIME2(3) NOT NULL,
        Dt_Alteracao      DATETIME2(3) NULL,
        -- day number: date filter that delegates behind a gateway (see computed-columns-delegation.md)
        Ref_DtInclusao    AS (DATEDIFF(day, 0, Dt_Inclusao)) PERSISTED
    );
GO

IF OBJECT_ID(N'dbo.APP_PedidoTrilha', N'U') IS NULL
    CREATE TABLE dbo.APP_PedidoTrilha (
        Id_Trilha          INT IDENTITY(1, 1) NOT NULL
                           CONSTRAINT PK_APP_PedidoTrilha PRIMARY KEY,
        Id_Pedido     INT           NOT NULL
                           CONSTRAINT FK_APP_PedidoTrilha_Pedido
                           FOREIGN KEY REFERENCES dbo.APP_Pedido (Id_Pedido),
        Tp_Evento          NVARCHAR(30)  NOT NULL,
        Des_Resumo         NVARCHAR(400) NOT NULL,
        Des_ValorAnterior  NVARCHAR(200) NULL,
        Des_ValorNovo      NVARCHAR(200) NULL,
        Id_UsuarioChamador INT           NOT NULL,
        Dt_Inclusao        DATETIME2(3)  NOT NULL
    );
GO

-- Live, unique protocol. Backs the UPDLOCK/HOLDLOCK of the Create procedure
-- (without a supporting index, HOLDLOCK escalates to a table lock).
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = N'UX_APP_Pedido_Protocolo'
                 AND object_id = OBJECT_ID(N'dbo.APP_Pedido'))
    CREATE UNIQUE NONCLUSTERED INDEX UX_APP_Pedido_Protocolo
        ON dbo.APP_Pedido (Nr_Protocolo)
        WHERE Flg_Situacao = 1;
GO

-- Dt_Alteracao comes from the trigger, never from a procedure. NOCOUNT in the trigger too:
-- without it, the inner UPDATE's rowcount becomes a result set of the procedure.
CREATE OR ALTER TRIGGER dbo.TR_APP_Pedido_Dt_Alteracao
ON dbo.APP_Pedido AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM inserted) RETURN;

    UPDATE s
       SET Dt_Alteracao = SYSUTCDATETIME()
      FROM dbo.APP_Pedido AS s
      JOIN inserted AS i ON i.Id_Pedido = s.Id_Pedido;
END
GO

-- ---------------------------------------------------------------------
-- 1. State UPDATE + trail
--    The state predicate in the WHERE plays the role of the IF (optimistic concurrency):
--    zero rows changed = the precondition did not hold = the following statements
--    have no source and write nothing.
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Encerrar
    @Id_Pedido      INT,             -- (a) target PK
    @Des_Status          NVARCHAR(20),    -- (b) value written, already validated by the flow
    @Tp_Evento           NVARCHAR(30),    -- (d) trail row, built by the flow
    @Des_Resumo          NVARCHAR(400),   -- (d)
    @Id_UsuarioChamador  INT              -- (c) resolved by the flow, by PK
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- OUTPUT sink: holds the result of the previous statement for the next one
    DECLARE @Alterado TABLE (
        Id_Pedido    INT          NOT NULL,
        Des_Status_Antes  NVARCHAR(20) NULL,
        Dt_Evento         DATETIME2(3) NOT NULL
    );

    BEGIN TRANSACTION;

    -- the state literal stays HERE, never in a parameter: as a parameter, the
    -- caller would switch the lock off by sending another string
    UPDATE s
       SET s.Des_Status = @Des_Status
    OUTPUT INSERTED.Id_Pedido,
           DELETED.Des_Status,            -- previous value, read atomically
           SYSUTCDATETIME()               -- database clock, single for the batch
      INTO @Alterado (Id_Pedido, Des_Status_Antes, Dt_Evento)
      FROM dbo.APP_Pedido AS s
     WHERE s.Id_Pedido = @Id_Pedido
       AND s.Flg_Situacao   = 1
       AND s.Des_Status     = N'aberto';

    -- trail in the SAME transaction; empty sink = zero rows
    INSERT dbo.APP_PedidoTrilha
          (Id_Pedido, Tp_Evento, Des_Resumo, Des_ValorAnterior, Des_ValorNovo,
           Id_UsuarioChamador, Dt_Inclusao)
    SELECT a.Id_Pedido, @Tp_Evento, @Des_Resumo, a.Des_Status_Antes, @Des_Status,
           @Id_UsuarioChamador, a.Dt_Evento
      FROM @Alterado AS a;

    COMMIT TRANSACTION;

    -- return: one row per possible outcome, the WHERE matches exactly one
    SELECT TOP (1)
           v.status       AS status,
           v.description  AS description,
           v.id           AS id,
           N''            AS url
      FROM (VALUES (1, 'success', N'ENCERRADO',     CONVERT(NVARCHAR(20), @Id_Pedido)),
                   (0, 'warning', N'NAO_APLICADO', N'')
           ) AS v (Gravou, status, description, id)
     WHERE v.Gravou = (SELECT COUNT(*) FROM @Alterado);
END
GO

-- ---------------------------------------------------------------------
-- 2. INSERT with duplicate guard
--    Guard and INSERT form ONE operation: NOT EXISTS under UPDLOCK, HOLDLOCK inside
--    the INSERT ... SELECT itself. There is no window between checking and writing.
--    Return with OUTER APPLY (not CROSS APPLY): in the refusal branch the sink is
--    empty and CROSS APPLY would zero out the result set; ISNULL guarantees id = ''.
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Criar
    @Nr_Protocolo        VARCHAR(12),     -- (b) already normalized by the flow
    @Nom_Abvd_Unidade    VARCHAR(3),      -- (b) the RECORD's unit, never the one viewed on screen
    @Tp_Evento           NVARCHAR(30),    -- (d)
    @Des_Resumo          NVARCHAR(400),   -- (d)
    @Id_UsuarioChamador  INT              -- (c)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @Criado TABLE (
        Id_Pedido  INT          NOT NULL,
        Dt_Evento       DATETIME2(3) NOT NULL
    );

    BEGIN TRANSACTION;

    INSERT dbo.APP_Pedido
          (Nr_Protocolo, Des_Status, Nom_Abvd_Unidade, Flg_Situacao, Dt_Inclusao)
    OUTPUT INSERTED.Id_Pedido, INSERTED.Dt_Inclusao
      INTO @Criado (Id_Pedido, Dt_Evento)
    SELECT @Nr_Protocolo, N'aberto', @Nom_Abvd_Unidade, 1, SYSUTCDATETIME()
     WHERE NOT EXISTS (SELECT 1
                         FROM dbo.APP_Pedido WITH (UPDLOCK, HOLDLOCK)
                        WHERE Nr_Protocolo = @Nr_Protocolo
                          AND Flg_Situacao = 1);

    INSERT dbo.APP_PedidoTrilha
          (Id_Pedido, Tp_Evento, Des_Resumo, Des_ValorAnterior, Des_ValorNovo,
           Id_UsuarioChamador, Dt_Inclusao)
    SELECT c.Id_Pedido, @Tp_Evento, @Des_Resumo, NULL, N'aberto',
           @Id_UsuarioChamador, c.Dt_Evento
      FROM @Criado AS c;

    COMMIT TRANSACTION;

    SELECT TOP (1)
           v.status             AS status,
           v.description        AS description,
           ISNULL(w.id, N'')    AS id,
           N''                  AS url
      FROM (VALUES (1, 'success', N'CRIADA'),
                   (0, 'error',   N'PROTOCOLO_DUPLICADO')
           ) AS v (Gravou, status, description)
     OUTER APPLY (SELECT CONVERT(NVARCHAR(20), c.Id_Pedido) AS id FROM @Criado AS c) AS w
     WHERE v.Gravou = (SELECT COUNT(*) FROM @Criado);
END
GO
