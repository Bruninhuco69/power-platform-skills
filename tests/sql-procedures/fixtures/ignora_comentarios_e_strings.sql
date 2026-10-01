-- Tudo abaixo e comentario ou texto: nenhum achado esperado.
CREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Listar
AS
BEGIN
    SET NOCOUNT ON;
    /* SELECT * FROM APP_Item WITH (NOLOCK); UPDATE x SET y = 1; EXEC (@sql + 'a') */
    -- SELECT * FROM APP_Item WITH (NOLOCK)
    SELECT N'SELECT * FROM APP_Item WITH (NOLOCK) -- UPDATE' AS Descricao,
           N'it''s a CAST(Dt AS INT) trap' AS Texto;
END
GO
