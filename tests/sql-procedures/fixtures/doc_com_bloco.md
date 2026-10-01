# Documento de contrato

Texto fora de bloco: CREATE PROCEDURE dbo.usp_APP_Fora_Do_Bloco sem nocount nao conta.

```sql
CREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Baixar
    @Id_Item INT
AS
BEGIN
    SET XACT_ABORT ON;
    UPDATE dbo.APP_Item SET Des_Status = N'Baixado' WHERE Id_Item = @Id_Item;
    SELECT TOP (1) 'success' AS status, N'OK' AS description, N'' AS id, N'' AS url;
END
```

```text
CREATE PROCEDURE dbo.usp_APP_Bloco_Texto AS UPDATE dbo.APP_Item SET x = 1;
```
