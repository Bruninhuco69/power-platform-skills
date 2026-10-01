# Propriedades que o Studio recusa (PA2108)

Colar um bloco com **uma** propriedade que o tipo de controle não tem derruba o bloco **inteiro**
(`PA2108`), sem apontar bem qual. O schema `pa.yaml` não valida nome de propriedade; quem recusa
é o Studio, na colagem. Esta tabela é o que o `validar-telas.py` aplica (T008).

## Sumário

1. [Tabela de recusas confirmadas](#1-tabela-de-recusas-confirmadas)
2. [Como verificar no Studio](#2-como-verificar-no-studio)
3. [Alternativas](#3-alternativas)
4. [Como estender](#4-como-estender)

---

## 1. Tabela de recusas confirmadas

`[verificado: projeto de referência]`: a versão do controle importa.

| Propriedade | Recusada em | O que usar |
|---|---|---|
| `AccessibleLabel` | `Classic/Button@2.2.0`, `Button@0.0.45` | o `Text` do botão; botão de ícone: `Tooltip` |
| `FocusedBorderThickness` | todos os tipos de controle testados no app de referência | só `FocusedBorderColor`, e apenas em `Classic/TextInput`, `Classic/ComboBox`, `Classic/DatePicker` |
| `Live` | `Label@2.5.1` | texto de erro por campo; ver [acessibilidade.md](acessibilidade.md) |
| `Size` | `Classic/ComboBox@2.4.0`, `Classic/DatePicker@2.6.0` | a fonte do controle não se altera; altura por `Height` |
| `RadiusTopLeft`, `RadiusTopRight`, `RadiusBottomLeft`, `RadiusBottomRight` | `Rectangle@2.3.0`, `Classic/ComboBox@2.4.0`, `Classic/DatePicker@2.6.0`, `NumberInput@2.9.12`, `ModernTextInput@1.1.1`, `TextInput@0.0.54` | canto arredondado decorativo: `Classic/Button@2.2.0` com `DisplayMode: =DisplayMode.Disabled` e `DisabledFill` |

Aceitas (atestadas) em `Classic/TextInput@2.3.2`: `Radius*` e `FocusedBorderColor`.

**Não atestadas** (nenhuma tela do app de referência as usa nesse tipo; **teste num bloco
pequeno** antes de espalhar): `Role` em `Label`, `ItemAccessibleLabel`, `Selectable`,
`ShowScrollbar`, `DelayItemLoading` e `LoadingSpinner` em `Gallery`, `AutoStart`, `AutoPause` e
`OnTimerStart` em `Timer`, `PaddingTop` e `PaddingRight` em `Label`.

O Learn lista algumas dessas propriedades (por exemplo `FocusedBorderThickness` e `AutoPause`
constam na página do controle Timer). **A documentação diz que existe; o Studio, com aquele
`Control@versão` no YAML, recusa.** Em conflito, vale o Studio.

## 2. Como verificar no Studio

1. **Procure no próprio app**: a propriedade já aparece naquele **tipo e versão** de controle
   num arquivo de tela? Se sim, está atestada. Se não, não assuma.

Destino: terminal (Bash), não é Power Fx.

```bash
grep -rn "AccessibleLabel" Frontend/
```

2. **Cole um bloco mínimo** (um controle só, com a propriedade) numa tela de teste. `PA2108` na
   colagem = recusada.
3. **Code view de um controle existente** (botão direito > View code): as propriedades que
   aparecem ali são as aceitas por aquele `Control@versão`.
4. Opcional (preview): o MCP server oficial (`describe_control`) lista as propriedades do
   controle ([yaml-pa-formato.md](yaml-pa-formato.md) §11).
5. Achou uma recusa nova? Anote tipo, versão e data aqui e em `RECUSADAS` no
   `scripts/validar-telas.py`, com um teste.

## 3. Alternativas

| Queria | Faça |
|---|---|
| nome acessível de botão de ícone | `Tooltip` mais `Text` descritivo quando houver espaço |
| espessura de foco | confie no padrão do controle e confira no Accessibility checker |
| região que o leitor anuncie | sem `Live`: mensagem fechável, duração longa, erro em modal |
| canto arredondado em retângulo | `Classic/Button` desabilitado |
| tamanho de fonte em combo ou datepicker | não há; ajuste `Height` e o controle |

## 4. Como estender

A tabela do validador está em `RECUSADAS` e `RECUSADA_EM_TODOS` no `scripts/validar-telas.py`.
Recusa exata (tipo e versão) vira **ERRO** T008; a mesma propriedade em outra versão do tipo vira
**AVISO** T008 ("confirme no Studio"). Todo item novo ganha um teste em
`tests/powerapps-canvas/`.
