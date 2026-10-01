CREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Baixar
    @Id_Item INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE dbo.APP_Item SET Des_Status = N'Baixado' WHERE Id_Item = @Id_Item;

    SELECT 'success' AS status, N'BAIXA_OK' AS description;
END
GO
