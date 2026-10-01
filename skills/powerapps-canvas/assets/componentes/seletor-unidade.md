# Seletor de unidade

Maturidade: **estável** · Frequência: **comum** (no cabeçalho ou como filtro).

## Propósito

Combo que muda o **escopo de leitura** da tela (`varUnidadeFiltro`). Só aparece para quem pode escolher: perfil global ou mais de uma unidade. O vazio volta ao escopo de origem do usuário, nunca à base inteira.

## Quando usar / quando não usar

**Use quando**

- o usuário pode ver mais de uma unidade;
- contadores e galeria precisam obedecer ao mesmo escopo.

**Não use quando**

- o usuário só tem uma unidade (o combo fica invisível por `Visible`, não por remoção);
- escopo como regra de acesso: a barreira é do flow, o combo é só conveniência de navegação.

## Anatomia

Árvore do bloco principal (a ordem de `Children` é o z-index):

```text
xx-lbl-unidade-escopo  (Label)
xx-cbo-unidade  (ComboBox)
```

## Dependências

- **Tokens `fx*` já existentes** em `assets/app-formulas-tokens.md`: `fxColorTextSecondary`, `fxFont`, `fxFontSizeFilter`, `fxLayoutMargin`, `fxFilterHeight`, `fxColorBorderInteractive`, `fxColorTextPrimary`, `fxColorPrimary`.
- **Tokens do bloco `COMPONENTES`** (já em `assets/app-formulas-tokens.md`): `fxHeaderHeight`.
- **Variáveis globais** (nascem no `OnStart`, `assets/app-onstart-molde.md`): `varUnidadeFiltro`, `varTodasUnidades`, `varUnidadeLotacao`, `varPedidoTotal`.
- **Coleções**: `colUnidadesEscopo`.
- **Flows**: nenhum.

## YAML

Destino: YAML colado no Studio (`,` entre argumentos, `;` encadeia, `.` decimal). Cole em Code view > Paste code, com a tela (ou um contêiner) como pai; troque o prefixo `xx` antes de colar, porque nome de controle é único no app inteiro.

```yaml
- xx-lbl-unidade-escopo:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Right
      Color: =fxColorTextSecondary
      Font: =fxFont
      Height: =fxFilterHeight
      Size: =fxFontSizeFilter
      Text: |-
        ="Escopo: " & If(IsBlank(varUnidadeFiltro), "todas as unidades", varUnidadeFiltro)
      VerticalAlign: =VerticalAlign.Middle
      Width: =260
      X: =Parent.Width - fxLayoutMargin - 180 - 8 - 260
      Y: =(fxHeaderHeight - fxFilterHeight) / 2
- xx-cbo-unidade:
    Control: Classic/ComboBox@2.4.0
    Properties:
      BorderColor: =fxColorBorderInteractive
      Color: =fxColorTextPrimary
      DisplayFields: =["Sigla"]
      FocusedBorderColor: =fxColorPrimary
      Height: =fxFilterHeight
      InputTextPlaceholder: =If(varTodasUnidades, "(Todas as unidades)", "Localizar unidade")
      Items: =colUnidadesEscopo
      OnChange: |-
        =Set(
          varUnidadeFiltro,
          If(
            IsBlank(Self.Selected),
            If(varTodasUnidades, "", varUnidadeLotacao),
            Self.Selected.Sigla
          )
        );
        Set(
          varPedidoTotal,
          CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
        )
      SearchFields: =["Sigla"]
      SelectMultiple: =false
      Visible: =varTodasUnidades || CountRows(colUnidadesEscopo) > 1
      Width: =180
      X: =Parent.Width - fxLayoutMargin - Self.Width
      Y: =(fxHeaderHeight - fxFilterHeight) / 2
```

### Variação: região e unidade em cascata

O segundo combo lista só as unidades da região escolhida; `Reset()` no `OnChange` do primeiro limpa a seleção do segundo.

```yaml
- xx-cbo-regiao:
    Control: Classic/ComboBox@2.4.0
    Properties:
      BorderColor: =fxColorBorderInteractive
      Color: =fxColorTextPrimary
      DisplayFields: =["Result"]
      FocusedBorderColor: =fxColorPrimary
      Height: =fxFilterHeight
      InputTextPlaceholder: ="Região"
      IsSearchable: =false
      Items: =Distinct(colUnidadesEscopo, Regiao)
      OnChange: =Reset('xx-cbo-unidade-filtrada')
      SearchFields: =["Result"]
      SelectMultiple: =false
      Width: =160
      X: =20
      Y: =44
- xx-cbo-unidade-filtrada:
    Control: Classic/ComboBox@2.4.0
    Properties:
      BorderColor: =fxColorBorderInteractive
      Color: =fxColorTextPrimary
      DisplayFields: =["Sigla"]
      FocusedBorderColor: =fxColorPrimary
      Height: =fxFilterHeight
      InputTextPlaceholder: ="Unidade"
      Items: =Filter(colUnidadesEscopo, IsBlank('xx-cbo-regiao'.Selected) || Regiao = 'xx-cbo-regiao'.Selected.Result)
      OnChange: =Set(varUnidadeFiltro, Coalesce(Self.Selected.Sigla, If(varTodasUnidades, "", varUnidadeLotacao)))
      SearchFields: =["Sigla"]
      SelectMultiple: =false
      Width: =160
      X: =196
      Y: =44
```

## Parâmetros a trocar

| No bloco | Troque por | Observação |
|---|---|---|
| `'<fonte>'`, `<col-unidade>` | tabela e coluna reais | `StartsWith` delega e cobre os dois modos (igualdade e vazio = todas) |
| `colUnidadesEscopo` | coleção carregada no `OnStart` | o que o usuário **pode** escolher (chaveada pela lotação, não pelo filtro) |
| `Sigla`, `Regiao` | colunas reais da coleção | `Trim()` na carga, uma vez |
| `varPedidoTotal` | contador(es) da tela | recontar no mesmo `OnChange` |

## Comportamento

Destino das fórmulas abaixo: o mesmo do YAML (`,` entre argumentos, `;` encadeia).

**`xx-cbo-unidade`.OnChange**: vazio volta à lotação (ou a todas, no perfil global); depois recontam-se os contadores

```powerfx
Set(
  varUnidadeFiltro,
  If(
    IsBlank(Self.Selected),
    If(varTodasUnidades, "", varUnidadeLotacao),
    Self.Selected.Sigla
  )
);
Set(
  varPedidoTotal,
  CountRows(Filter('<fonte>', StartsWith(<col-unidade>, varUnidadeFiltro)))
)
```

**`xx-cbo-unidade`.Visible**: só quem pode escolher vê o seletor

```powerfx
varTodasUnidades || CountRows(colUnidadesEscopo) > 1
```

## Acessibilidade

- O rótulo "Escopo: ..." mostra em texto o que o combo aplica, útil para quem lê só por leitor de tela.
- Combo clássico é navegável por teclado; garanta `TabIndex` coerente com o cabeçalho.

## Armadilhas

- `Visible` com só `CountRows(...) > 1` esconde o combo de quem tem perfil global e uma coleção de uma linha: o primeiro ramo (`varTodasUnidades`) resolve.
- Escrever o escopo de leitura em `varUnidadeLotacao` apaga a unidade de origem do usuário: são variáveis distintas.
- Mandar `varUnidadeFiltro` como unidade de gravação grava no lugar errado: o flow deriva a unidade do registro.
- `SearchFields: =[""]` herda o conceito de primary name do Dataverse e rende linha em branco; use a coluna real.

## Variações

- Chip de escopo fixo (sem combo) para usuário de unidade única: só o rótulo `xx-lbl-unidade-escopo`.
- Cascata (acima).
