CREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Listar
    @Dia INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT i.Id_Item
      FROM dbo.APP_Item AS i
     WHERE CAST(i.Dt_Inclusao AS INT) = @Dia;
END
GO
