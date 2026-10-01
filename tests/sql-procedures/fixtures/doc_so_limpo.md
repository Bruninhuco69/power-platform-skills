```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Ler
AS
BEGIN
    SET NOCOUNT ON;
    SELECT i.Id_Item FROM dbo.APP_Item AS i;
END
```
