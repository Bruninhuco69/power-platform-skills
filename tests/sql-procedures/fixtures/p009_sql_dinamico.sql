CREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Buscar
    @Coluna NVARCHAR(50),
    @Valor  NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @sql NVARCHAR(MAX) = N'';
    SET @sql = N'SELECT Id_Item FROM dbo.APP_Item WHERE ' + @Coluna + N' = ''' + @Valor + N'''';
    EXEC (@sql);
END
GO
