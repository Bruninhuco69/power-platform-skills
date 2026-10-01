-- =====================================================================
-- MOLDE · procedure de escrita (variante declarativa)
--
-- Dominio de exemplo: "pedido" com trilha de eventos. Troque APP pela
-- sigla do projeto e os nomes de tabela/coluna pelos do AMBIENTE REAL
-- (o nome vem do ambiente, nao deste molde).
--
-- Requer SQL Server 2016 SP1+ (CREATE OR ALTER). Destino: banco de DEV.
-- Em producao, o DDL da secao 0 vai ao DBA (assets/pedido-ddl-dba-molde.md).
--
-- Contrato de retorno: 1 result set, 1 linha, 4 colunas
--   status (success|warning|error) · description (CODIGO ASCII) · id (texto) · url ('')
-- Quem traduz o codigo em frase para o usuario e o flow.
-- Comentarios dentro de bloco SQL: ASCII sem acento.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. DDL de exemplo (DEV)
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
        -- numero do dia: filtro de data que delega atras de gateway (ver colunas-calculadas-delegacao.md)
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

-- Protocolo vivo e unico. Sustenta o UPDLOCK/HOLDLOCK da procedure Criar
-- (sem indice de apoio o HOLDLOCK escala para lock de tabela).
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = N'UX_APP_Pedido_Protocolo'
                 AND object_id = OBJECT_ID(N'dbo.APP_Pedido'))
    CREATE UNIQUE NONCLUSTERED INDEX UX_APP_Pedido_Protocolo
        ON dbo.APP_Pedido (Nr_Protocolo)
        WHERE Flg_Situacao = 1;
GO

-- Dt_Alteracao vem do trigger, nunca de procedure. NOCOUNT tambem no trigger:
-- sem ele o rowcount do UPDATE interno vira result set da procedure.
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
-- 1. UPDATE de estado + trilha
--    O predicado de estado no WHERE faz o papel do IF (concorrencia otimista):
--    zero linha alterada = a pre-condicao nao valia = os statements seguintes
--    ficam sem fonte e nao gravam nada.
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Encerrar
    @Id_Pedido      INT,             -- (a) PK do alvo
    @Des_Status          NVARCHAR(20),    -- (b) valor gravado, ja validado pelo flow
    @Tp_Evento           NVARCHAR(30),    -- (d) linha de trilha, montada pelo flow
    @Des_Resumo          NVARCHAR(400),   -- (d)
    @Id_UsuarioChamador  INT              -- (c) resolvido pelo flow, por PK
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- sink do OUTPUT: guarda o resultado do statement anterior para o seguinte
    DECLARE @Alterado TABLE (
        Id_Pedido    INT          NOT NULL,
        Des_Status_Antes  NVARCHAR(20) NULL,
        Dt_Evento         DATETIME2(3) NOT NULL
    );

    BEGIN TRANSACTION;

    -- literal de estado fica AQUI, nunca em parametro: como parametro, o
    -- chamador desligaria a trava mandando outra string
    UPDATE s
       SET s.Des_Status = @Des_Status
    OUTPUT INSERTED.Id_Pedido,
           DELETED.Des_Status,            -- valor anterior lido atomicamente
           SYSUTCDATETIME()               -- relogio do banco, unico no lote
      INTO @Alterado (Id_Pedido, Des_Status_Antes, Dt_Evento)
      FROM dbo.APP_Pedido AS s
     WHERE s.Id_Pedido = @Id_Pedido
       AND s.Flg_Situacao   = 1
       AND s.Des_Status     = N'aberto';

    -- trilha na MESMA transacao; sink vazio = zero linha
    INSERT dbo.APP_PedidoTrilha
          (Id_Pedido, Tp_Evento, Des_Resumo, Des_ValorAnterior, Des_ValorNovo,
           Id_UsuarioChamador, Dt_Inclusao)
    SELECT a.Id_Pedido, @Tp_Evento, @Des_Resumo, a.Des_Status_Antes, @Des_Status,
           @Id_UsuarioChamador, a.Dt_Evento
      FROM @Alterado AS a;

    COMMIT TRANSACTION;

    -- retorno: uma linha por desfecho possivel, o WHERE casa exatamente uma
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
-- 2. INSERT com guarda de duplicidade
--    Guarda e INSERT formam UMA operacao: NOT EXISTS sob UPDLOCK, HOLDLOCK dentro
--    do proprio INSERT ... SELECT. Nao ha janela entre checar e gravar.
--    Retorno com OUTER APPLY (nao CROSS APPLY): no ramo de recusa o sink esta
--    vazio e CROSS APPLY zeraria o result set; ISNULL garante id = ''.
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Criar
    @Nr_Protocolo        VARCHAR(12),     -- (b) ja normalizado pelo flow
    @Nom_Abvd_Unidade    VARCHAR(3),      -- (b) unidade DO REGISTRO, nunca a visualizada na tela
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
