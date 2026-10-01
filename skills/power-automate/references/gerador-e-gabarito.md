# Gerador seguro e gabarito imutável

Decisão F6 de [decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md): a entrega
é por colagem no designer; o arquivo colado é o **gabarito**; gerador nunca escreve sobre ele.
Este arquivo explica por quê e como montar o pipeline sem repetir o acidente que o motivou
([licoes-de-campo.md](licoes-de-campo.md)).

## Sumário

1. [Quando vale ter gerador](#1-quando-vale-ter-gerador)
2. [O acidente](#2-o-acidente)
3. [Pastas e direção](#3-pastas-e-direção)
4. [Trava de escrita](#4-trava-de-escrita)
5. [Round-trip](#5-round-trip)
6. [Portões](#6-portões)

---

## 1. Quando vale ter gerador

Um flow se escreve à mão no designer ou se cola de um JSON escrito à mão. Um gerador compensa
quando **várias** ações repetem a mesma regra e a regra já divergiu entre cópias (uma regra de
validação em vários flows, com duas grafias). "Cada regra de negócio vira UMA expressão em UMA função"
elimina a divergência. Com um flow só, escreva o escopo à mão (use `assets/flow-gravar-molde.json`)
e **não** monte gerador (YAGNI).

## 2. O acidente

1. O gerador emitiu o escopo; o designer devolveu diferente (as regras R1-R13 de
   [gabarito-designer.md](gabarito-designer.md)); o arquivo devolvido foi corrigido à mão e virou
   o gabarito no disco.
2. O gerador **nunca absorveu** as regras do designer.
3. O portão "fonte x disco" (regera em memória e compara com o disco) passou a acusar o gabarito
   como "velho" e mandou **regerar**. Regerar abre o arquivo em modo escrita e **apaga o
   gabarito**, devolvendo-o ao estado de antes do designer.
4. Na mesma semana, uma reforma de escopo reescreveu o gerador e apagou a correção de trilha que
   só existia no arquivo colado (a tarefa estava marcada "feita" sem evidência).

O portão estava certo sobre o fato (fonte != disco) e errado sobre a **direção**: depois da
colagem real, o disco está certo e a fonte está velha. [verificado: projeto de referência]

Lição: **depois da primeira colagem real, traga cada diferença para o gerador antes de gerar o
segundo flow.** Enquanto o gerador não reproduzir o gabarito, não rode o gerador.

## 3. Pastas e direção

```
flows/
  fonte/        nomes.json (único lugar de nomes, mensagens, gates), regras em módulos
  gerar.py      lê fonte/, escreve SÓ em dist/
  dist/         saída do gerador. Marcada "gerado - não editar". Pode ser apagada à vontade
  gabarito/     o que o designer devolveu. IMUTÁVEL (somente leitura por convenção e por trava)
  verificar     scripts/verificar-fluxo.py roda sobre gabarito/ E dist/
```

Direção do fluxo de informação: **ambiente -> gabarito -> fonte do gerador -> dist**. Nunca
`dist -> gabarito`. Correção manual vai para a **entrada** do gerador (P3 em
[decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md)), não para o arquivo gerado.

## 4. Trava de escrita

Um gerador escreve em `dist/` e **recusa** qualquer outro destino:

```python
from pathlib import Path

PASTAS_PROTEGIDAS = ("gabarito", "clipboard")


def destino_seguro(destino: Path, raiz_dist: Path) -> Path:
    """Aceita só caminho dentro de dist/ e nunca dentro de pasta protegida."""
    destino = destino.resolve()
    raiz = raiz_dist.resolve()
    if raiz not in destino.parents:
        raise PermissionError(f"gerador só escreve em {raiz}: recusado {destino}")
    if any(parte in PASTAS_PROTEGIDAS for parte in destino.parts):
        raise PermissionError(f"pasta protegida: {destino}")
    return destino
```

Destino: função no início do gerador; toda escrita passa por ela. Complemente com uma segunda
trava fora do código: marcar `gabarito/` como somente leitura no sistema de arquivos e ter o
Git desde o dia 0 (P1), para que qualquer apagamento seja um `git checkout`.

## 5. Round-trip

Para provar que o gerador reproduz o designer:

1. Gere o flow já colado em `dist/`.
2. **Normalize** os dois (ordem de chaves R7, `runAfter` vazio R3, `else` R8) e compare com o
   gabarito nó a nó.
3. Divergência = a regra que falta no gerador **ou** edição manual deliberada no designer. Edição
   manual deve ser **declarada** (lista de nós que divergem de propósito, com motivo); divergência
   sem explicação é erro.
4. Só com divergência zero sem explicação o gerador está "alinhado" e pode gerar o próximo flow.

Num projeto isso foi feito com um pós-processador que aplicava R1-R9/R11-R13 sobre a saída crua e
comparava com o gabarito: a maior parte dos nós em comum batia só com as regras, o restante divergia por edição
manual declarada, e nenhum divergia sem explicação. O pós-processador é **ponte**; o destino é as regras viverem
no gerador e o pós-processador virar teste de regressão.

## 6. Portões

| Portão | Direção correta |
|---|---|
| Fonte x `dist/` | Regera em memória e compara com `dist/`. **Nunca** com `gabarito/` |
| Gerador x gabarito | Round-trip da §5 |
| Gerador x assinatura da procedure | Parâmetros emitidos == assinatura lida do `CREATE PROCEDURE` (falta/sobra = erro). Sem este portão, dezenas de especificações foram reescritas sem que nada acusasse |
| `verificar-fluxo.py` | Sobre o **artefato realmente colado** (`gabarito/`), não só sobre a saída do gerador: num projeto os portões de expressão só rodavam sobre `dist/`, e o gabarito carregou dois defeitos que nenhum portão pegou |
| Prova de que acusa | Fixture que falha por regra ([decisoes-padrao.md](../../power-platform/references/decisoes-padrao.md) P4) |
| Toolchain versionada | `.gitignore` de `__pycache__`; o `.py` no repositório. Um projeto ficou com o gerador "sumido" (só `.pyc` no disco) |
| Contrato | Gerado do artefato ([contrato-app-flow.md](contrato-app-flow.md) §7) |

Quando o gerador existe, a **mensagem de erro de todo portão** diz o arquivo e a ação
(`arquivo.json:Acao_X:`), porque um erro sem lugar custa mais que o defeito.
