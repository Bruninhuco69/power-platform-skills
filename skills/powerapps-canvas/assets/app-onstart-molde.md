# Molde: `App.OnStart` em ordem de dependência

`OnStart` só tem o que é **mutável** e o que depende de identidade. Constante, tema e valor
derivado vão para `App.Formulas` ([app-formulas-tokens.md](app-formulas-tokens.md)).

**Como aplicar.** Selecione `App` no Studio, propriedade `OnStart`, e digite ou cole o bloco na
barra de fórmulas. O objeto App não tem Code view. Destino: **barra de fórmulas, locale pt-BR
(`;` entre argumentos, `;;` encadeia, `,` decimal)**.

## Sumário

1. [Regras](#regras)
2. [O bloco](#o-bloco)
3. [Por que esta ordem](#por-que-esta-ordem)
4. [O que fica de fora do OnStart](#o-que-fica-de-fora-do-onstart)

## Regras

1. **Toda global usada em qualquer tela nasce aqui**, com valor neutro. Variável não
   inicializada é `Blank()`, e `Blank() = 0` é falso: filtro comparado a 0 deixa a galeria
   vazia, sem erro. `[verificado: projeto de referência]`
2. **Ordem de dependência.** Quem lê `varPerfil` vem depois de `varPerfil`. Inverter faz
   `IsBlank(varPerfil)` valer sempre verdadeiro e todo usuário cai em "sem acesso".
3. **Fail-closed desde a primeira linha.** O `OnStart` não é bloqueante por padrão: uma tela pode
   renderizar e ficar interativa antes de ele terminar
   ([App object](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)).
   Por isso `varSemAcesso` começa em `true` e só vira `false` depois de provar acesso.
   `[não verificado: instante exato do primeiro render no seu app]`
4. **Sem `Navigate`.** Tela inicial é a propriedade `StartScreen` (só enxerga named formulas,
   não globais).
5. **Contador de tela** (`varPedidoTotal`) nasce aqui com 0 e é **recalculado** no `OnVisible` e
   depois de cada flow que grava; contador calculado só no `OnStart` congela e passa o dia
   divergindo da galeria.
6. Mude os nomes `Usuario`, `Perfil`, `Unidade` para as fontes reais do ambiente
   (`NOMES-AS-BUILT`, skill `dataverse`).

## O bloco

Destino: barra de fórmulas do objeto App, propriedade `OnStart` (pt-BR: `;` e `;;`).

```powerfx
// ---------- 0. fail-closed enquanto o OnStart roda ----------
Set(varSemAcesso; true);;

// ---------- 1. identidade (chave unica: UPN do Entra) ----------
Set(varUsuario; LookUp(Usuario; Upn_Entra = Lower(User().Email)));;

// ---------- 2. perfil: por FK, registro inteiro, so perfil ativo ----------
// As duas condicoes vao com && no MESMO argumento: o 3o argumento do LookUp
// e a coluna de resultado, nao um segundo predicado.
Set(varPerfil; LookUp(Perfil; Id_Perfil = varUsuario.Id_Perfil && Flg_Situacao = true));;

// ---------- 3. escopo: tres papeis, tres variaveis ----------
// lotacao: a unidade do cadastro (nunca muda); todas: o perfil ve a rede inteira;
// filtro: escopo de LEITURA ("" significa todas, so para quem tem varTodasUnidades).
Set(varTodasUnidades; varPerfil.Flg_TodasUnidades = true);;
Set(varUnidadeLotacao; Trim(varUsuario.Cod_Unidade));;
Set(varUnidadeFiltro; If(varTodasUnidades; ""; varUnidadeLotacao));;

// ---------- 4. sem acesso: so depois de perfil e escopo ----------
Set(
    varSemAcesso;
    IsBlank(varUsuario)
    || varUsuario.Flg_Situacao <> true
    || IsBlank(varPerfil)
    || (!varTodasUnidades && IsBlank(varUnidadeLotacao))
);;

// ---------- 5. dominios pequenos em colecao (evita LookUp por linha da galeria) ----------
Concurrent(
    ClearCollect(
        colUnidades;
        Sort(
            AddColumns(Filter(Unidade; Flg_Situacao = true); "Sigla"; Trim(Cod_Unidade); "Nome"; Trim(Nom_Unidade));
            Sigla
        )
    );
    ClearCollect(colPerfis; Sort(Filter(Perfil; Flg_Situacao = true); Nv_Perfil))
);;

// o que o usuario PODE escolher: chaveada pela lotacao, nao pelo filtro
ClearCollect(
    colUnidadesEscopo;
    If(varTodasUnidades; colUnidades; Filter(colUnidades; Sigla = varUnidadeLotacao))
);;

// ---------- 6. navegacao ----------
Set(varTelaAtiva; "pedidos");;

// ---------- 7. feedback (contrato dos blocos canonicos) ----------
Set(varShowLoading; false);;
Set(varLoadingMessage; "");;
Set(varShowToast; false);;
Set(varToastType; "success");;
Set(varToastMessage; "");;
Set(varRet; Blank());;

// ---------- 8. selecao, modais e contadores de tela (valor neutro) ----------
Set(varPedidoSel; Blank());;
Set(varMostrarConfirmar; false);;
Set(varPedidoTotal; 0)
```

Troque `Concurrent` por chamadas em sequência se uma coleção passar a depender de outra:
`Concurrent` roda só ramos independentes, em ordem imprevisível
([Concurrent](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-concurrent)).

## Por que esta ordem

```text
varUsuario
  |-> varPerfil --> varTodasUnidades --+
  |-> varUnidadeLotacao ---------------+--> varSemAcesso
  |                                    +--> varUnidadeFiltro
  +-- colUnidades (independente) -----------> colUnidadesEscopo
```

- `AddColumns` + `Sort` não delegam (ver [delegacao.md](../references/delegacao.md)); aqui é
  proposital: o `Filter` interno delega, devolve poucas linhas e o resto roda uma vez só, abaixo
  do teto de 500/2.000 linhas.
- `Trim()` na carga, uma vez, de todo `CHAR(n)` com preenchimento: o SQL ignora o espaço à
  direita no `=`, o Power Fx não. Nunca espalhe `Trim` pelas telas.
- `varPerfil` é **registro**, lido com `LookUp` explícito. O conector SQL não expande a FK
  (`varUsuario.Id_Perfil.Flg_Encerrar` não existe).
- Permissão é sempre **flag** do perfil (`varPerfil.Flg_Encerrar`), nunca comparação com o nome do
  perfil. Detalhe em [escopo-e-permissao.md](../references/escopo-e-permissao.md).

## O que fica de fora do OnStart

| O valor... | Vai para |
|---|---|
| nunca muda (cor, medida, texto, `fxLimiteLinhas`) | `App.Formulas` |
| depende de uma ação do usuário e só existe numa tela | `UpdateContext` ou `Set` no `OnVisible` da tela |
| é janela de data de filtro (`varXDe`, `varXAte`) | `OnVisible` da tela (e o botão Limpar reescreve junto com o `Reset`) |
| é carga pesada usada em uma tela só | `OnVisible` dessa tela ou carga sob demanda (ver [performance.md](../references/performance.md)) |
