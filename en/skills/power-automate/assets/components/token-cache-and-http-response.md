# Token validation with cache and response by real status

> **File**: `token-cache-and-http-response.json` · **Frequency**: cache: rare; HTTP response: occasional · **Maturity**: unique (cache); stable (responses); credential in the header [unverified]
> **Depends on**: `inbound-config`; token validation connector; cache table; 2 `Initialize variable` actions at the root

## Purpose

`Escopo_Principal` with `Scope_Token` (reads the cache; validates for real when there is no token, the token differs, or the row is 1 h old or more; rewrites the cache), `Resposta_sucesso` (200 on `Succeeded`) and `Resposta_token_invalido` (401 on `Failed` or `TimedOut`).

## When to use / when not to use

**Use**

- Input from an external system through the flow's own HTTP trigger (C6).

**Do not use**

- Flow called by the app (the identity comes from the context).
- When validation is cheap: skip the cache.

## Where to paste

Flow root, after the two variables (`Inicializar_erros_lote`, `Inicializar_linhas_com_erro`). The data work hangs off `Resposta_sucesso`.

## Inputs and outputs

**Reads**

- The request's `Authorization` header, `CONFIG.origemToken`.

**Exposes**

- HTTP response 200 or 401; the status of `Scope_Token` (Failed = rejected).

## JSON

Destination: `Ctrl+V` at the designer's insertion point (scope clipboard envelope, `nodeId` `Escopo_Principal`; the same content is in `token-cache-and-http-response.json`). Fictitious GUIDs; connections: `<prefixo>_sharedcommondataserviceforapps`, `<prefixo>_sharedvalidadortoken`.


```json
{
  "nodeId": "Escopo_Principal",
  "serializedValue": {
    "type": "Scope",
    "actions": {
      "Scope_Token": {
        "type": "Scope",
        "description": "REUSABLE: first action inside the main scope. Failed = token rejected.",
        "actions": {
          "Token_recebido": {
            "type": "Compose",
            "description": "Credential in the header, never in the body. Secure inputs and outputs: it does not go into the run history.",
            "inputs": "@coalesce(triggerOutputs()?['headers']?['Authorization'],'')",
            "runtimeConfiguration": {
              "secureData": {
                "properties": [
                  "inputs",
                  "outputs"
                ]
              }
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000142"
            }
          },
          "Buscar_token_cache": {
            "type": "OpenApiConnection",
            "description": "modifiedon of the row = when the token was last validated.",
            "inputs": {
              "parameters": {
                "entityName": "<prefixo>_tokencaches",
                "$select": "<prefixo>_tokencacheid,<prefixo>_token,modifiedon",
                "$filter": "@concat('<prefixo>_name eq ''',outputs('CONFIG')?['origemToken'],'''')",
                "$orderby": "modifiedon desc",
                "$top": 1
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                "connection": "shared_commondataserviceforapps",
                "operationId": "ListRecords"
              }
            },
            "runAfter": {
              "Token_recebido": [
                "Succeeded"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000143"
            }
          },
          "Se_token_novo": {
            "type": "If",
            "description": "Yes = the cache is not valid (no token, different token, or last validated 1 h ago or more).",
            "expression": {
              "or": [
                {
                  "equals": [
                    "@empty(outputs('Token_recebido'))",
                    true
                  ]
                },
                {
                  "not": {
                    "equals": [
                      "@outputs('Token_recebido')",
                      "@first(coalesce(body('Buscar_token_cache')?['value'],json('[]')))?['<prefixo>_token']"
                    ]
                  }
                },
                {
                  "greaterOrEquals": [
                    "@sub(ticks(utcNow()),ticks(coalesce(first(coalesce(body('Buscar_token_cache')?['value'],json('[]')))?['modifiedon'],'2000-01-01T00:00:00Z')))",
                    36000000000
                  ]
                }
              ]
            },
            "actions": {
              "Validar_token": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "new_token": "@outputs('Token_recebido')"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_validadortoken",
                    "connection": "shared_validadortoken",
                    "operationId": "VerifyToken"
                  }
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000144"
                }
              },
              "Atualizar_token_cache": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "entityName": "<prefixo>_tokencaches",
                    "recordId": "@first(coalesce(body('Buscar_token_cache')?['value'],json('[]')))?['<prefixo>_tokencacheid']",
                    "item/<prefixo>_token": "@outputs('Token_recebido')"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                    "connection": "shared_commondataserviceforapps",
                    "operationId": "UpdateRecord"
                  }
                },
                "runAfter": {
                  "Validar_token": [
                    "Succeeded"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000145"
                }
              },
              "Criar_token_cache": {
                "type": "OpenApiConnection",
                "description": "Only runs if the Update failed: the cache row does not exist yet.",
                "inputs": {
                  "parameters": {
                    "entityName": "<prefixo>_tokencaches",
                    "item/<prefixo>_name": "@outputs('CONFIG')?['origemToken']",
                    "item/<prefixo>_token": "@outputs('Token_recebido')"
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                    "connection": "shared_commondataserviceforapps",
                    "operationId": "CreateRecord"
                  }
                },
                "runAfter": {
                  "Atualizar_token_cache": [
                    "Failed",
                    "TimedOut"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000146"
                }
              },
              "Ignorar_falha_cache": {
                "type": "Compose",
                "description": "Intentional absorption: a failure to write the cache must not bring down the inbound call (the token was already validated). Do NOT include Skipped in runAfter, or it masks a Validar_token failure.",
                "inputs": "Token cache not written: see Atualizar_token_cache and Criar_token_cache. The next call validates again.",
                "runAfter": {
                  "Criar_token_cache": [
                    "Failed",
                    "TimedOut"
                  ]
                },
                "metadata": {
                  "operationMetadataId": "00000000-0000-0000-0000-000000000147"
                }
              }
            },
            "else": {
              "actions": {}
            },
            "runAfter": {
              "Buscar_token_cache": [
                "Succeeded",
                "Failed",
                "TimedOut"
              ]
            },
            "metadata": {
              "operationMetadataId": "00000000-0000-0000-0000-000000000148"
            }
          }
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000149"
        }
      },
      "Resposta_sucesso": {
        "type": "Response",
        "kind": "Http",
        "inputs": {
          "statusCode": 200,
          "body": {
            "code": "Success",
            "message": "Received successfully."
          }
        },
        "runAfter": {
          "Scope_Token": [
            "Succeeded"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000150"
        }
      },
      "Resposta_token_invalido": {
        "type": "Response",
        "kind": "Http",
        "inputs": {
          "statusCode": 401,
          "body": {
            "error": {
              "code": "TokenInvalido",
              "message": "The token sent is not valid."
            }
          }
        },
        "runAfter": {
          "Scope_Token": [
            "Failed",
            "TimedOut"
          ]
        },
        "metadata": {
          "operationMetadataId": "00000000-0000-0000-0000-000000000151"
        }
      }
    },
    "runAfter": {
      "Inicializar_linhas_com_erro": [
        "Succeeded"
      ]
    },
    "metadata": {
      "operationMetadataId": "00000000-0000-0000-0000-000000000152"
    }
  },
  "allConnectionData": {
    "Buscar_token_cache": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    },
    "Validar_token": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_validadortoken"
        },
        "connection": {
          "id": "<prefixo>_sharedvalidadortoken"
        },
        "connectionName": "<prefixo>_sharedvalidadortoken"
      },
      "referenceKey": "shared_validadortoken"
    },
    "Atualizar_token_cache": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
    },
    "Criar_token_cache": {
      "connectionReference": {
        "api": {
          "id": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
        },
        "connection": {
          "id": "<prefixo>_sharedcommondataserviceforapps"
        },
        "connectionName": "<prefixo>_sharedcommondataserviceforapps",
        "impersonation": {}
      },
      "referenceKey": "shared_commondataserviceforapps"
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
| `<prefixo>_tokencaches` | cache table | AS-BUILT table with columns `name` (primary = origin) and `token` (text 4000) |
| connection `shared_validadortoken` | `<prefixo>_sharedvalidadortoken` | the token validation connector in your environment |
| `36000000000` | 1 h in ticks | the TTL you want in ticks (1 min = 600000000) |
| `Authorization` | header | the name of the header the caller sends |

## runAfter

`Resposta_sucesso` depends on `Scope_Token` on `Succeeded`; `Resposta_token_invalido` on `Failed` and `TimedOut`; the root scope depends on `Inicializar_linhas_com_erro`.

## Pitfalls

- In the reference project the `Condition` compared **constants** (`equals(200, 200)`): the invalid-token branch was dead code and the flow answered 200 while the validator failed. The response comes from the scope's real result (F016).
- A token in the body (`triggerBody()['headers']['token']`) shows up in payload logs; the header with secure inputs and outputs is the intended form, and the property name `triggerOutputs()?['headers']?['Authorization']` is `[unverified]`: check it in the run history.
- The cache stores the token in clear text in a table: restrict reads on the table with a Security Role. Alternative: compare a hash `[unverified]: a hash function is not in the list used in these flows`.
- `Ignorar_falha_cache` does **not** include `Skipped`: a failure to write the cache must not bring down the inbound call, but `Skipped` would mask a validator failure.
- Paste `Scope_Token` **inside** the main scope, not at the root: the `Log` reads `result('Escopo_Principal')` and must see the token failure there.
- Actions independent of the token (mapping) with no `runAfter` run in parallel with the token scope.
- An HTTP `Response` does not end the flow either; if there is an action after it, it is an asynchronous accept and must answer 202 (see the `http-external-inbound` reference).
- The 401 with a missing token and with a wrong token is a mandatory test.

## Variations

- Token in the body (as in the reference project): change the `Token_recebido` expression to `triggerBody()?['headers']?['token']` and wrap it with `Bearer ` when calling the validator.
- Asynchronous accept: change `Resposta_sucesso` to 202 with `workflow()?['run']?['name']` and let the `Log` mark the failure.

## Verification

Destination: terminal, from the plugin root.

```text
python skills/power-automate/scripts/verificar-fluxo.py skills/power-automate/assets/components/token-cache-and-http-response.json
```

Expected result: `0 error(s), 2 warning(s)`.

Warnings intrinsic to the isolated component:

- `F006` (reference to an action outside the pasted snippet): `CONFIG`. These are the block's **inputs**: they exist in the destination flow (see *Inputs and outputs*). In an assembled flow, the same snippet passes without this warning.
