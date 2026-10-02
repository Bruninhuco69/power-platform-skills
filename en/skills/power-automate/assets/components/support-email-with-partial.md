# Support e-mail with partial-write handling

> **File**: `support-email-with-partial.json` · **Frequency**: occasional · **Maturity**: designed [unverified]: generated, never returned by the designer
> **Depends on**: `resolve-directory-id`; Office 365 e-mail and SQL connectors

## Purpose

`Try_email` sends the e-mail and logs the send. `Catch_email` finds out whether the e-mail **went out** (`result()` filtered by name and status) and answers `warning` 'do not click again' or `error` 'nothing was changed'. `Responder_email` answers success.

## When to use / when not to use

**Use**

- Access/provisioning request by e-mail followed by a record.

**Do not use**

- Informational e-mail with no write afterwards: a plain `Catch`.

## Where to paste

Inside `Try_pedido`, after `Bloco_resolver_id`. The envelope brings its own Try/Catch/Response.

## Inputs and outputs

**Reads**

- `CONFIG.mailSuporte`, `outputs('Chamador')`, `outputs('Id_diretorio_final')`, trigger parameters.

**Exposes**

- Response `success`, `warning` (partial) or `error`; the run ends on the last two.

## JSON

Destination: `Ctrl+V` at the designer insertion point (clipboard scope envelope, `nodeId` `Escopo_email_suporte`; the same content is in `support-email-with-partial.json`). Fictitious GUIDs; connections: `<prefixo>_sharedoffice365`, `<prefixo>_sharedsql`.


```json
{
  "nodeId": "Escopo_email_suporte",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Try_email": {
        "type": "Scope",
        "actions": {
          "Enviar_email_ao_suporte": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "emailMessage/To": "@outputs('CONFIG')?['mailSuporte']",
                "emailMessage/Subject": "@concat('Access request: ',toLower(trim(coalesce(triggerBody()['text_1'],''))))",
                "emailMessage/Body": "@concat('Action: ',toLower(trim(coalesce(triggerBody()['text'],''))),decodeUriComponent('%0D%0A'),'Target: ',toLower(trim(coalesce(triggerBody()['text_1'],''))),decodeUriComponent('%0D%0A'),'Directory ID: ',outputs('Id_diretorio_final'),decodeUriComponent('%0D%0A'),'Requested by: ',outputs('Chamador'),decodeUriComponent('%0D%0A'),'When: ',formatDateTime(utcNow(),'MM/dd/yyyy HH:mm'),' UTC')",
                "emailMessage/Importance": "Normal"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365",
                "connection": "shared_office365",
                "operationId": "SendEmail_V2"
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000102"
            }
          },
          "Registrar_envio": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "server": "default",
                "database": "default",
                "procedure": "[dbo].[<procedure_registrar_envio>]",
                "parameters/Id_Alvo": "@int(coalesce(first(body('Estado_antes_gravar')?['value'])?['Id_Pedido'],0))",
                "parameters/Id_DiretorioAlvo": "@if(equals(outputs('Id_diretorio_final'),'(unresolved)'),'',outputs('Id_diretorio_final'))"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_sql",
                "connection": "shared_sql",
                "operationId": "ExecuteProcedure_V2"
              }
            },
            "runAfter": {
              "Enviar_email_ao_suporte": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000103"
            }
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000104"
        }
      },
      "Catch_email": {
        "type": "Scope",
        "actions": {
          "Email_saiu": {
            "type": "Query",
            "inputs": {
              "from": "@result('Try_email')",
              "where": "@and(equals(item()?['name'],'Enviar_email_ao_suporte'),equals(item()?['status'],'Succeeded'))"
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000105"
            }
          },
          "Se_email_ja_saiu": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "greater": [
                    "@length(body('Email_saiu'))",
                    0
                  ]
                }
              ]
            },
            "actions": {
              "Avisa_parcial": {
                "type": "Response",
                "kind": "PowerApp",
                "inputs": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "status": {
                        "title": "status",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      },
                      "description": {
                        "title": "description",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      },
                      "id": {
                        "title": "id",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      },
                      "url": {
                        "title": "url",
                        "x-ms-dynamically-added": true,
                        "type": "string"
                      }
                    },
                    "additionalProperties": {}
                  },
                  "statusCode": 200,
                  "body": {
                    "status": "warning",
                    "description": "Request sent to support, but the record did not log the order. Do not click again: tell support.",
                    "id": "",
                    "url": ""
                  }
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000106"
                }
              },
              "Avisa_parcial_fim": {
                "type": "Terminate",
                "inputs": {
                  "runStatus": "Succeeded"
                },
                "runAfter": {
                  "Avisa_parcial": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000107"
                }
              }
            },
            "else": {
              "actions": {
                "Nega_email": {
                  "type": "Response",
                  "kind": "PowerApp",
                  "inputs": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "status": {
                          "title": "status",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        },
                        "description": {
                          "title": "description",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        },
                        "id": {
                          "title": "id",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        },
                        "url": {
                          "title": "url",
                          "x-ms-dynamically-added": true,
                          "type": "string"
                        }
                      },
                      "additionalProperties": {}
                    },
                    "statusCode": 200,
                    "body": {
                      "status": "error",
                      "description": "Could not open the ticket with support. Nothing was changed: try again.",
                      "id": "",
                      "url": ""
                    }
                  },
                  "metadata": {
                    "operationMetadataId": "00000000-0000-0000-0000-000000000108"
                  }
                },
                "Nega_email_fim": {
                  "type": "Terminate",
                  "inputs": {
                    "runStatus": "Succeeded"
                  },
                  "runAfter": {
                    "Nega_email": [
                      "Succeeded"
                    ]
                  },
                  "metadata": {
                    "operationMetadataId": "00000000-0000-0000-0000-000000000109"
                  }
                }
              }
            },
            "runAfter": {
              "Email_saiu": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000110"
            }
          }
        },
        "runAfter": {
          "Try_email": [
            "Failed",
            "TimedOut",
            "Skipped"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000111"
        }
      },
      "Responder_email": {
        "type": "Response",
        "kind": "PowerApp",
        "inputs": {
          "schema": {
            "type": "object",
            "properties": {
              "status": {
                "title": "status",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "description": {
                "title": "description",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "id": {
                "title": "id",
                "x-ms-dynamically-added": true,
                "type": "string"
              },
              "url": {
                "title": "url",
                "x-ms-dynamically-added": true,
                "type": "string"
              }
            },
            "additionalProperties": {}
          },
          "statusCode": 200,
          "body": {
            "status": "success",
            "description": "Request sent to support.",
            "id": "",
            "url": ""
          }
        },
        "runAfter": {
          "Try_email": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000112"
        }
      }
    },
    "runAfter": {
      "Bloco_resolver_id": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000113"
    }
  },
  "allConnectionData": {
    "Enviar_email_ao_suporte": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_office365"
        },
        "connection": {
          "id": "<prefixo>_sharedoffice365"
        },
        "connectionName": "<prefixo>_sharedoffice365"
      },
      "referenceKey": "shared_office365"
    },
    "Registrar_envio": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_sql"
        },
        "connection": {
          "id": "<prefixo>_sharedsql"
        },
        "connectionName": "<prefixo>_sharedsql"
      },
      "referenceKey": "shared_sql"
    }
  },
  "staticResults": {},
  "isScopeNode": true,
  "mslaNode": true
}
```

## Parameters to change

| Item | Value in the JSON | Change to |
|---|---|---|
| `<procedure_registrar_envio>` | procedure | AS-BUILT name |
| `emailMessage/To` | `CONFIG.mailSuporte` | keep it coming from `CONFIG` |
| subject and body | neutral text | the request text; no sensitive data beyond what is needed |

## runAfter

`Catch_email` depends on `Try_email` with `Failed`, `TimedOut`, `Skipped`; `Responder_email` with `Succeeded`.

## Pitfalls

- The reference project marked the send in a variable inside the `Try` and read it in the `Catch`; the `Catch` reads `outputs()` of a possibly unexecuted action. Here the `Catch` queries `result('Try_email')`, which lists every first-level action with its status.
- `warning` 'do not click again' is the only honest path: the e-mail went out and cannot be undone.
- Body with a line break: `decodeUriComponent('%0D%0A')`.
- Initialize variable only works at the flow root; inside a scope use `Compose`.
- Catch inside the flow's Try: it ends the run (`Terminate`), so the outer `Catch_pedido` does not run.

## Variations

- Two outer steps: one `Email_saiu` filter per step and one message per combination.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/support-email-with-partial.json
```

Expected result: `0 error(s), 5 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `CONFIG`, `Chamador`, `Estado_antes_gravar`, `Id_diretorio_final`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.
