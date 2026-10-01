-- =====================================================================
-- MOLDE · leitura com filtros em JSON + escopo de unidade
--
-- Depende das tabelas de procedure-escrita-molde.sql (dbo.APP_Pedido).
-- Requer COMPATIBILITY_LEVEL >= 130 (OPENJSON). Rode antes:
--   SELECT compatibility_level FROM sys.databases WHERE name = DB_NAME();
--
-- Desenho:
--   * UMA funcao inline (tvf) concentra os predicados; as procedures de
--     listar e contar consomem a mesma definicao (nunca duas copias).
--   * @Filtros chega como JSON cru, montado pela tela e VALIDADO pelo flow.
--     Chave ausente, null ou escalar no lugar de array = predicado nao aplicado.
--     Sem filtro, mande '{}' (as datas leem @Filtros com JSON_VALUE; vazio nao testado nelas).
--   * @Unidade_Escopo e a permissao do perfil, resolvida pelo flow:
--       NULL   = perfil que ve tudo (sem restricao)
--       'AAA'  = so a propria unidade
--       ''     = terceiro estado: casa unidade nenhuma, de proposito (fail-closed)
--                (so vale se a coluna for NOT NULL com CHECK (LEN(LTRIM(RTRIM(<coluna>))) > 0))
--     A funcao so obedece; quem decide o valor e o flow.
--   * Escopo em AND com a lista de unidades do filtro: o filtro nunca amplia o escopo.
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
    -- chaves multivalor abertas UMA vez e etiquetadas pela chave.
    -- r.[type] = 4 : so array. Qualquer outra forma vira ausencia de linha.
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
        -- escopo: permissao, nao filtro do usuario
       AND (@Unidade_Escopo IS NULL OR s.Nom_Abvd_Unidade = @Unidade_Escopo)
        -- unidades: o CONVERT fica do lado da lista para a coluna VARCHAR(3)
        -- nao ser promovida a NVARCHAR e perder o seek
       AND (NOT EXISTS (SELECT 1 FROM Lista AS f WHERE f.Chave = N'unidades')
            OR s.Nom_Abvd_Unidade IN (SELECT CONVERT(VARCHAR(3), f.Valor)
                                        FROM Lista AS f WHERE f.Chave = N'unidades'))
        -- status
       AND (NOT EXISTS (SELECT 1 FROM Lista AS t WHERE t.Chave = N'status')
            OR s.Des_Status IN (SELECT t.Valor FROM Lista AS t WHERE t.Chave = N'status'))
        -- data_de: coluna sozinha de um lado (sargavel); a expressao repete de proposito
       AND (TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_de'))), N''), 23) IS NULL
            OR s.Dt_Inclusao >= TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_de'))), N''), 23))
        -- data_ate: meia-noite do dia seguinte, EXCLUSIVA. Nunca CONVERT(DATE, coluna).
       AND (TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_ate'))), N''), 23) IS NULL
            OR s.Dt_Inclusao < DATEADD(day, 1, TRY_CONVERT(DATE, NULLIF(LTRIM(RTRIM(JSON_VALUE(@Filtros, N'$.data_ate'))), N''), 23)))
);
GO

-- Indice de apoio: escopo + ordenacao. E DDL: vai no pedido ao DBA, nao no deploy da procedure.
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = N'IX_APP_Pedido_Unidade_Inclusao'
                 AND object_id = OBJECT_ID(N'dbo.APP_Pedido'))
    CREATE NONCLUSTERED INDEX IX_APP_Pedido_Unidade_Inclusao
        ON dbo.APP_Pedido (Nom_Abvd_Unidade, Dt_Inclusao DESC)
        INCLUDE (Des_Status);
GO

-- ---------------------------------------------------------------------
-- Contar: chamar ANTES de listar. COUNT_BIG sem GROUP BY devolve SEMPRE 1 linha,
-- inclusive sobre 0 registros. id sai como texto, sem separador de milhar.
-- OPTION (RECOMPILE) e requisito: OPENJSON sem WITH e estimado em 50 linhas fixas;
-- com RECOMPILE o otimizador ve o valor real e elimina o ramo da lista vazia.
-- Sem XACT_ABORT/transacao: nao ha escrita para proteger.
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.usp_APP_Pedido_Contar
    @Filtros          NVARCHAR(4000),
    @Unidade_Escopo   VARCHAR(3)         -- NULL = sem restricao. Resolvido pelo flow.
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
-- Listar: aqui o result set E o dado (nao devolve o contrato de 4 colunas).
-- Teto explicito: leitura sem limite estoura o corpo de resposta do conector
-- (8 MB atras de gateway) e o tempo da acao (110 s).
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
