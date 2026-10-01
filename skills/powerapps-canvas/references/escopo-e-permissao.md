# Escopo e permissão do lado do app

Flags por perfil, fail-closed, `""` = "todas" com guarda e a unidade de gravação que vem do
registro. **Tudo aqui é UX**: o que decide é o flow (skill `power-automate`) e, no Dataverse, a
Security Role (skill `dataverse`). Este arquivo diz como a tela se comporta para ajudar o
usuário e para **não vazar** dado por descuido.

## Sumário

1. [O que a tela é e o que não é](#1-o-que-a-tela-é-e-o-que-não-é)
2. [Perfil por flags](#2-perfil-por-flags)
3. [Sem acesso: fail-closed](#3-sem-acesso-fail-closed)
4. [Escopo por unidade: três papéis, três variáveis](#4-escopo-por-unidade-três-papéis-três-variáveis)
5. [O predicado vai em todo `Filter`](#5-o-predicado-vai-em-todo-filter)
6. [Unidade de gravação](#6-unidade-de-gravação)
7. [Testes de ouro](#7-testes-de-ouro)
8. [Decisões que o projeto precisa tomar cedo](#8-decisões-que-o-projeto-precisa-tomar-cedo)

---

## 1. O que a tela é e o que não é

Decisão A3 de [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md): **o escopo
na tela é UX, não controle de acesso.** O filtro por unidade ajuda a navegar; quem barra é o flow.
Motivos: a conta do conector é compartilhada (a leitura **não é isolada** no banco), e o cliente
pode ser manipulado. Por isso:

- esconder botão ou item de menu por flag não é autorização;
- toda escrita passa por flow que **revalida** perfil, flag da ação e escopo do chamador;
- o app não envia identidade como parâmetro: o flow lê o chamador do contexto
  (`Office 365 Users — MyProfile_V2`): ver [chamada-flow.md](chamada-flow.md).

O filtro de leitura sem isolamento no banco é **risco aceito e declarado** do projeto, não um
detalhe: a decisão entre isolamento real (RLS no SQL, business unit ou owner team no Dataverse)
e "toda leitura sensível via flow" é do §8.

## 2. Perfil por flags

**Decisão T8**: permissão por **flag** do perfil (`Flg_PodeX`, `pode_x`), nunca por nome de
perfil. Comparar `varPerfil.Nome = "Supervisor"` quebra no dia em que o perfil é renomeado ou
um novo perfil nasce.

- `varPerfil` é um **registro** lido por `LookUp` explícito, por **chave estrangeira** do usuário
  (`Id_Perfil`) e com o predicado de situação (`Flg_Situacao = true`) no **mesmo argumento**, com
  `&&`: o terceiro argumento do `LookUp` é a coluna de resultado, não um segundo predicado.
  Sem o predicado de situação, perfil desativado montava o menu inteiro e o flow negava toda
  escrita sem explicação. `[verificado: projeto de referência]`
- O conector SQL **não expande FK**: `varUsuario.Id_Perfil.Flg_Encerrar` não existe; use
  `varPerfil.Flg_Encerrar`.
- Perfil resolvido por **rótulo de Choice** (Dataverse) é frágil: acento ou espaço diferente e
  `varPerfil` fica `Blank()`, todo botão some, sem mensagem. FK elimina essa classe de falha.
- Flag é booleano puro (`Flg_* BIT NOT NULL DEFAULT 0`). Com `NULL`, `<> true` e `= true` se
  comportam diferente no servidor e no cliente (pedido ao dono do banco).
- Uso na tela:

Destino: YAML colado (`,` e `;`).

```yaml
# xx-btn-gal-encerrar
Visible: =varPerfil.Flg_Encerrar
DisplayMode: =If(varShowLoading || ThisItem.Status = "encerrado", DisplayMode.Disabled, DisplayMode.Edit)
```

Não amarre o menu a uma flag de **consulta** que alguns perfis legítimos não têm (o usuário cairia
numa tela vazia, sem saber por quê): amarre ao `!varSemAcesso`.

## 3. Sem acesso: fail-closed

Sem perfil resolvido = **sem acesso**. O `OnStart` calcula `varSemAcesso` **depois** de
`varPerfil` e do escopo (ordem em [app-onstart-molde.md](../assets/app-onstart-molde.md)) e a
começa em `true`:

Destino: barra de fórmulas do objeto App, propriedade `OnStart` (pt-BR: `;` e `;;`).

```powerfx
Set(
    varSemAcesso;
    IsBlank(varUsuario)
    || varUsuario.Flg_Situacao <> true
    || IsBlank(varPerfil)
    || (!varTodasUnidades && IsBlank(varUnidadeLotacao))
)
```

- `IsBlank(varPerfil)`: sem perfil, todo `Visible` de menu vira falso e o app abriria vazio, sem
  erro; é para isso que existe o painel de "sem acesso".
- `(!varTodasUnidades && IsBlank(varUnidadeLotacao))`: `""` deixou de ser "ausência de valor" e
  passou a **significar "todas"**. Cadastro com unidade vazia daria `varUnidadeFiltro = ""` e o
  usuário leria a rede inteira. Quem não tem unidade não entra.
- Declarada **antes** de `varPerfil`, `IsBlank(varPerfil)` é sempre verdadeiro e todo mundo cai
  em "sem acesso": falha fechada, mas total.
- Todo container de conteúdo tem `Visible: =!varSemAcesso`, **inclusive o menu**. Painel de "sem
  acesso" em cada tela, com `fxMsgSemAcessoTitulo` e `fxMsgSemAcessoHint` (bloco no
  [tela-molde.md](../assets/tela-molde.md)).

## 4. Escopo por unidade: três papéis, três variáveis

Unidade é a loja, a agência, a região ou o que o projeto chamar. **Três papéis distintos, três
variáveis; não volte a fundi-los.**

| Variável | Papel | Regra |
|---|---|---|
| `varUnidadeLotacao` | unidade do cadastro do usuário | nunca muda e **nunca vazia** (garantido pelo fail-closed) |
| `varTodasUnidades` | o perfil enxerga a rede inteira | vem da flag do perfil |
| `varUnidadeFiltro` | escopo de **leitura** | **`""` significa "todas"** e só é alcançável com `varTodasUnidades`; `If(varTodasUnidades, "", varUnidadeLotacao)` (YAML) |

- `""` é estado da **tela** e nunca viaja como escopo: o flow resolve o escopo pelo perfil do
  chamador (`NULL` = todas, para perfil global; senão a unidade do chamador). A escolha do usuário
  vai no filtro (`@Filtros.unidades`), e `""` vira chave **ausente** — nunca `''`, que no banco
  significa *nenhuma*. Ver `sql-procedures/references/escopo-por-unidade.md` §2.
- Perfil global abre em "todas" e filtra depois, se quiser. Os demais abrem na lotação. Sem
  persistência entre sessões: todo login recomeça aqui.
- **Esvaziar o combo do cabeçalho volta à lotação, nunca à base inteira**:

Destino: YAML colado (`,` e `;`).

```yaml
# xx-cbo-header-unidade
OnChange: |-
  =Set(
    varUnidadeFiltro,
    If(
      IsBlank(Self.Selected),
      If(varTodasUnidades, "", varUnidadeLotacao),
      Self.Selected.Sigla
    )
  )
```

- `colUnidadesEscopo` (o que o usuário **pode escolher**) é chaveada pela **lotação**, não pelo
  filtro: se dependesse do filtro, escolher uma unidade esvaziaria a lista e prenderia o
  usuário nela. Visibilidade do combo: `varTodasUnidades || CountRows(colUnidadesEscopo) > 1`.
- **Coleção de registros não tem `.Value`**: `Self.Selected.Sigla`, não `Self.Selected.Value`
  (devolve vazio e a galeria abre vazia ao trocar a unidade).
- `Trim()` na carga de qualquer `CHAR(n)` com preenchimento (`'AAA    '` x `'AAA'`): no SQL o
  `=` ignora o espaço à direita, no Power Fx não casa. Uma vez, no `OnStart`.
- Combo com dezenas de itens precisa de `IsSearchable` ligado; desligado fica inutilizável.

## 5. O predicado vai em todo `Filter`

**Todo `Filter` sobre fonte com escopo organizacional leva o predicado de escopo.** Filtro sem
escopo **delega perfeitamente e nunca emite aviso de delegação**: o vazamento passa por todos
os portões. Já aconteceu: um total e uma prévia de relatório sem o predicado de unidade
deixaram o supervisor ver a rede inteira com o combo vazio.
`[verificado: projeto de referência]`

Destino: YAML colado (`,` e `;`).

```yaml
# Items de qualquer galeria, e a contagem do card, com o MESMO token
Items: =Filter(Pedido, StartsWith(Unidade, varUnidadeFiltro))
```

Um token único (`StartsWith(coluna, varUnidadeFiltro)`) cobre os dois modos e delega (vira
`LIKE 'x%'`): com sigla é igualdade; com `""` casa tudo. Card e galeria leem a mesma fonte com o
mesmo predicado e concordam **por construção**.

**Três condições que autorizam o `StartsWith` e que o banco precisa garantir** (exija-as ao dono do
banco; não herde "siglas de 3 letras" como se fosse regra):

1. o código da unidade é **de tamanho fixo e prefix-free** (nenhum é prefixo de outro): senão
   `StartsWith` vira prefixo de verdade e **vaza entre unidades**;
2. a coluna de escopo é **`NOT NULL`**: `LIKE '%'` (o que `StartsWith(col, "")` vira) **não casa
   `NULL`**, e no modo "todas" a linha sem unidade some calada;
3. a invariante é **conferida por constraint ou teste automatizado**, não por inspeção de um CSV.

## 6. Unidade de gravação

A unidade de **gravação** não mora no estado global: é **campo do formulário** (`xx-cbo-form-unidade`).
No cadastro vem do combo; na edição e no encerramento vem **do próprio registro**
(`varPedidoSel.Unidade`). Editar nunca transfere de unidade; a unidade é propriedade do
registro. Quando o flow pode derivar a unidade do registro pai, a tela nem a envia.
Mandar "a unidade que estou olhando" (`varUnidadeFiltro`) como unidade de gravação grava no lugar
errado quando o perfil global está filtrando outra unidade.

## 7. Testes de ouro

1. **Esvaziar o combo volta à lotação** (e perfil global volta a "todas").
2. **Card bate com galeria** nos dois modos (lotação e todas).
3. Usuário **sem perfil**, com **perfil desativado**, **sem unidade** (e sem flag de "todas"):
   só o painel de "sem acesso" aparece, menu incluído.
4. Duas contas, duas unidades: nenhuma enxerga a outra com o combo vazio.
5. Unidade com padding (`CHAR`): o filtro casa depois do `Trim` da carga.
6. Linha com unidade `NULL`: aparece onde deveria (e o §5 registra se o banco não impede).
7. Grep dos `Filter` e `CountRows(Filter` da tela: **todos** têm o predicado de escopo.

## 8. Decisões que o projeto precisa tomar cedo

- **Isolamento real de leitura** (SESSION_CONTEXT/RLS no SQL; business unit e owner team no
  Dataverse) **ou** "toda leitura sensível via flow ou procedure". Sem decidir, o projeto
  herda o risco do §1 sem saber.
- **Multi-unidade por usuário** ("3 de dezenas"): uma flag "tudo ou uma" não representa isso. Se for
  requisito, a tabela de vínculo e o objeto de leitura entram no desenho desde o início.
- **Chave de identidade única** (UPN do Entra) com índice `UNIQUE` e carga preenchida: sem
  unicidade o `LookUp` devolve a linha que o SQL entregar, sem `ORDER BY`, e perfil e unidade
  viram sorteio por sessão.
- Fuso e corte do dia (UTC no banco, conversão num só lugar).
