CREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Listar
AS
BEGIN
    SET NOCOUNT ON;

    SELECT * FROM dbo.APP_Item; -- lint-ok P007
    SELECT i.Id_Item FROM dbo.APP_Item AS i WITH (NOLOCK); -- lint-ok
END
GO
