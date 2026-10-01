# Autorização e escopo dentro do flow

Decisões A2, A3, F2, F3 e T8 de [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md).
O flow é o controle; a tela só esconde botão. A procedure (skill `sql-procedures`) e as tabelas
de perfil (skill `dataverse`) têm donos próprios -- aqui está só o que o flow faz.

## Sumário

1. [Quem é o chamador](#1-quem-é-o-chamador)
2. [Perfil: flag por ação](#2-perfil-flag-por-ação)
3. [Escopo por unidade](#3-escopo-por-unidade)
4. [Flags de segurança nascem ligadas](#4-flags-de-segurança-nascem-ligadas)
5. [A procedure também autoriza?](#5-a-procedure-também-autoriza)

---

## 1. Quem é o chamador

```json
{
  "Perfil_do_chamador": {
    "type": "OpenApiConnection",
    "inputs": {
      "parameters": { "$select": "mail,userPrincipalName,displayName" },
      "host": {
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users",
        "connection": "shared_office365users",
        "operationId": "MyProfile_V2"
      }
    },
    "runAfter": { "CONFIG": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000004" }
  },
  "Chamador": {
    "type": "Compose",
    "inputs": "@toLower(coalesce(outputs('Perfil_do_chamador')?['body/mail'],outputs('Perfil_do_chamador')?['body/userPrincipalName'],''))",
    "runAfter": { "Perfil_do_chamador": ["Succeeded"] },
    "metadata": { "operationMetadataId": "00000000-0000-0000-0000-000000000005" }
  }
}
```

Destino: dentro de `actions` do escopo raiz, depois de `CONFIG` (colado pelo designer; ver
[formato-clipboard.md](formato-clipboard.md)).

- **Identidade vem do contexto de execução** (`MyProfile_V2`), que o cliente não falsifica.
  Quem chamar o flow por fora da tela não escolhe quem é. [verificado: projeto de referência]
- O identificador do chamador liga em **um único nó** (`Ler_chamador`), sempre por
  `outputs('Chamador')`, nunca por `triggerBody()`.
- **A ordem `mail` x `userPrincipalName` depende de qual valor a coluna de identidade guarda.**
  Normalize a carga (`LOWER/TRIM`) e faça o teste de 1 minuto: rode o flow com um usuário de
  teste e compare `outputs('Chamador')` no histórico com a coluna de identidade. Divergência
  nega **todo mundo** sem erro. Em projetos de referência a ordem ficou invertida entre os flows
  (ver [licoes-de-campo.md](licoes-de-campo.md)).

## 2. Perfil: flag por ação

1. `Ler_chamador` lê **uma vez** a linha do usuário já unida ao perfil (usuário ativo, perfil
   ativo) e devolve todas as flags. **Zero linha = negar** (usuário desconhecido ou inativo).
2. Cada `Caso_<acao>` confere **a flag daquela ação** (`Autorizar_<acao>`), antes de qualquer
   escrita. Um portão único antes do `Switch` só pode cortar quem não tem **nenhuma** permissão
   do flow; ele não sabe qual ramo vai rodar. O defeito clássico: o perfil que cadastra também
   encerra de forma irreversível porque o portão conferia só "pode cadastrar".
3. Flag, nunca nome de perfil (T8). Sem perfil resolvido = sem acesso (fail-closed).
4. A negação é a mesma frase genérica em todos os casos ([contrato-app-flow.md](contrato-app-flow.md)).

Leitura de `bit` do SQL (o conector entrega `true`/`false`, não `1`) e comparação segura:

```text
@not(or(equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'1'),equals(toLower(string(coalesce(body('Ler_chamador')?['ResultSets']?['Table1']?[0]?['Flg_Gravar'],'0'))),'true')))
```

Destino: campo `expression` de um `If` (`equals` com `@true`) -- ver o molde. Ausente nega.
Detalhe da armadilha em [expressoes-wdl-armadilhas.md](expressoes-wdl-armadilhas.md).

## 3. Escopo por unidade

Permissão responde *o quê*; escopo responde *onde*. Regras:

| Regra | Por quê |
|---|---|
| Compare a unidade do **registro real** (lido de novo no `Estado_antes_x`), não a do parâmetro, nas ações que alteram registro existente | O parâmetro é ignorado fora do cadastro; conferi-lo deixaria o chamador escolher a própria autorização |
| No **cadastro**, compare o parâmetro (é o que será gravado) | O registro ainda não existe |
| Ação que escreve em **dois** registros confere os dois | Nada obriga os dois a serem da mesma unidade |
| Perfil "todas as unidades" é o **primeiro** termo do `or` que libera; os demais termos continuam válidos sozinhos (não conte com curto-circuito) | Quem vê tudo não precisa de linha de vínculo |
| Unidade vazia no registro **barra** quem não é global | Dado faltante virando curinga é o oposto do escopo |
| Conjunto de unidades permitidas vazio: teste `empty(trim(join(<lista>,'')))`, não `empty(<lista>)` | Sem lotação a lista chega como `['']`, um array de **um** item, que `empty()` considera cheio |
| Filtro opcional em que "todas" = `null`: ligue o `null` **cru**, sem `coalesce` nem `truncar` | `''` casa nada; uma "melhoria" genérica de `coalesce` já desfez essa decisão e o relatório saiu vazio para quem vê tudo |
| Mensagem de negação não diz a unidade do registro | Responderia a pergunta de quem sonda |

O escopo na galeria do app é UX (A3); só o flow barra. O molde traz a validação por unidade
dentro de `Validar_gravar`, ligada por `CONFIG.cfgEscopoUnidade`.

## 4. Flags de segurança nascem ligadas

`CONFIG` guarda os interruptores de comportamento (`cfgEscopoUnidade`, `cfgCampoObrigatorio`...).
Todo interruptor de **segurança** nasce `true`; desligar exige decisão registrada. Um projeto
entregou o escopo por unidade como flag desligada: por padrão qualquer perfil gravava em qualquer
unidade, e a decisão de produto nunca foi fechada. [verificado: projeto de referência]

Não confunda os dois tipos de flag: a **flag de permissão do perfil** (`Flg_PodeX`) nasce
**0/falso**, porque ninguém ganha permissão por omissão; o **interruptor de segurança no `CONFIG`**
nasce **ligado**, porque desligá-lo é que abre o acesso.

## 5. A procedure também autoriza?

Se a procedure só recebe valores "prontos" do flow e aceita o id do chamador por parâmetro, quem
tiver a connection reference chama a procedure e grava o que quiser, e a trilha de auditoria
prova o quê/quando, não quem. Duas saídas legítimas, as duas com custo:

- **Autorização também na procedure** (defesa em profundidade): mais código na procedure, uma
  regra em dois lugares.
- **`GRANT EXECUTE` como única trava**, risco aceito **por escrito**.

A decisão e o bloco defensivo são da skill `sql-procedures`; o flow não deixa de autorizar em
nenhum dos dois casos. Em Dataverse, a Security Role cumpre o papel do `GRANT` (skill `dataverse`).
