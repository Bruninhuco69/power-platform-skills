CREATE OR ALTER PROCEDURE dbo.baixar_item
    @Id_Item INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE dbo.APP_Item SET Des_Status = N'Baixado' WHERE Id_Item = @Id_Item;

    SELECT TOP (1) 'success' AS status, N'BAIXA_OK' AS description, N'' AS id, N'' AS url;
END
GO
