-- =====================================================================
-- TEMPLATE · read with JSON filters + unit scope
--
-- Depends on the tables of write-procedure-template.sql (dbo.APP_Pedido).
-- Requires COMPATIBILITY_LEVEL >= 130 (OPENJSON). Run first:
--   SELECT compatibility_level FROM sys.databases WHERE name = DB_NAME();
--
-- Design:
--   * ONE inline function (tvf) holds the predicates; the list and count
--     procedures consume the same definition (never two copies).
--   * @Filtros arrives as raw JSON, built by the screen and VALIDATED by the flow.
--     Missing key, null or a scalar instead of an array = predicate not applied.
--     With no filter, send '{}' (the dates read @Filtros with JSON_VALUE; empty is not tested there).
--   * @Unidade_Escopo is the role's permission, resolved by the flow:
--       NULL   = role that sees everything (no restriction)
--       'AAA'  = only its own unit
--       ''     = third state: matches no unit, on purpose (fail-closed)
--                (only valid if the column is NOT NULL with CHECK (LEN(LTRIM(RTRIM(<coluna>))) > 0))
--     The function only obeys; the flow decides the value.
--   * Scope is ANDed with the filter's unit list: the filter never widens the scope.
-- =====================================================================

CREATE OR ALTER FUNCTION dbo.tvf_APP_Pedido_Filtrar
(
    @Filtros          NVARCHAR(4000),
    @Unidade_Escopo   VARCHAR(3)
)
RETURNS TABLE
AS
RETURN
(
    -- multi-value keys opened ONCE and tagged by key.
    -- r.[type] = 4 : array only. Any other shape becomes no row.
    WITH Lista AS
    (
        SELECT r.[key]               AS Chave,
               LTRIM(RTRIM(j.value)) AS Valor
          FROM OPENJSON(ISNULL(NULLIF(@Filtros, N''), N'{}')) AS r
         CROSS APPLY OPENJSON(CASE WHEN r.[type] = 4 THEN r.value ELSE N'[]' END) AS j
         WHERE r.[type] = 4
           AND LTRIM(RTRIM(j.value)) <> N''
    )
    SELECT s.Id_Pedido,
           s.Nr_Protocolo,
           s.Des_Status,
           s.Nom_Abvd_Unidade,
           s.Dt_Inclusao,
           s.Dt_Alteracao
      FROM dbo.APP_Pedido AS s
     WHERE s.Flg_Situacao = 1
        -- scope: permission, not a user filter
       AND (@Unidade_Escopo IS NULL OR s.Nom_Abvd_Unidade = @Unidade_Escopo)
        -- units: the CONVERT goes on the list side so the VARCHAR(3) column
        -- is not promoted to NVARCHAR and loses the seek
       AND (NOT EXISTS (SELECT 1 FROM Lista AS f WHERE f.Chave = N'unidades')
            OR s.Nom_Abvd_Unidade IN (SELECT CONVERT(VARCHAR(3), f.Valor)
                                        FROM Lista AS f WHERE f.Chave = N'unidades'))
        -- status
       AND (NOT EXISTS (SELECT 1 FROM Lista AS t WHERE t.Chave = N'status')
            OR s.Des_Status IN (SELECT t.Valor FROM Lista AS t WHERE t.Chave = N'status'))
        -- data_de: bare column on one side (sargable); the expression repeats on purpose
       AND (TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_de'))), N''), 23) IS NULL
            OR s.Dt_Inclusao >= TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_de'))), N''), 23))
        -- data_ate: midnight of the next day, EXCLUSIVE. Never CONVERT(DATE, column).
       AND (TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_ate'))), N''), 23) IS NULL
            OR s.Dt_Inclusao < DATEADD(day, 1, TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_ate'))), N''), 23)))
);
GO

-- Supporting index: scope + ordering. It is DDL: it goes in the DBA request, not in the procedure deploy.
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = N'IX_APP_Pedido_Unidade_Inclusao'
                 AND object_id = OBJECT_ID(N'dbo.APP_Pedido'))
    CREATE NONCLUSTERED INDEX IX_APP_Pedido_Unidade_Inclusao
        ON dbo.APP_Pedido (Nom_Abvd_Unidade, Dt_Inclusao DESC)
        INCLUDE (Des_Status);
GO

-- ---------------------------------------------------------------------
-- Count: call BEFORE list. COUNT_BIG without GROUP BY ALWAYS returns 1 row,
-- even over 0 records. id comes out as text, with no thousands separator.
-- OPTION (RECOMPILE) is a requirement: OPENJSON without WITH is estimated at a fixed 50 rows;
-- with RECOMPILE the optimizer sees the real value and eliminates the empty-list branch.
-- No XACT_ABORT/transaction: there is no write to protect.
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Contar
    @Filtros          NVARCHAR(4000),
    @Unidade_Escopo   VARCHAR(3)         -- NULL = no restriction. Resolved by the flow.
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 'success'                            AS status,
           N'CONTAGEM_OK'                       AS description,
           CONVERT(NVARCHAR(20), COUNT_BIG(*))  AS id,
           N''                                  AS url
      FROM dbo.tvf_APP_Pedido_Filtrar(@Filtros, @Unidade_Escopo)
    OPTION (RECOMPILE);
END
GO

-- ---------------------------------------------------------------------
-- List: here the result set IS the data (it does not return the 4-column contract).
-- Explicit cap: an unbounded read blows the connector response body
-- (8 MB behind a gateway) and the action time limit (110 s).
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Listar
    @Filtros          NVARCHAR(4000),
    @Unidade_Escopo   VARCHAR(3),
    @Limite           INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP (@Limite)
           f.Id_Pedido,
           f.Nr_Protocolo,
           f.Des_Status,
           f.Nom_Abvd_Unidade,
           f.Dt_Inclusao
      FROM dbo.tvf_APP_Pedido_Filtrar(@Filtros, @Unidade_Escopo) AS f
     ORDER BY f.Dt_Inclusao DESC, f.Id_Pedido DESC
    OPTION (RECOMPILE);
END
GO
