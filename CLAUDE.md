# power-platform-skills

Kit mantido em pt-BR (`pp`, raiz) e en-US (`pp-en`, pasta `en/`).

- **A vitrine é em inglês:** `README.md` e a raiz do site (`docs/index.html`) são en-US; o pt-BR fica em
  `README.pt-BR.md` e `docs/pt-br/`. O diagrama abre em inglês e `?lang=pt` mostra o pt-BR. As skills
  continuam com o pt-BR como fonte (o mapa vai do pt-BR para o en-US).

- **Toda alteração entra em pt-BR e en-US no mesmo commit.** Mudança numa língua só não entra.
- **Atualize `i18n/mapa.json`:** arquivo novo ganha entrada (`en` + `situacao`); par traduzido vira
  `"feito"`; arquivo renomeado ou removido sai do mapa. O lint confere (L014).
- **Scripts são um código só:** edite o pt-BR (`skills/*/scripts/`), com o texto novo em
  `tr("pt", "en")`, e rode `python tools/sincronizar_en.py` para copiar para `en/`. Nomes em
  `i18n/glossario.md`.
- **Power Fx por idioma:** pt-BR `;` separa argumento e `;;` encadeia, `,` decimal; en-US `,` separa,
  `;` encadeia, `.` decimal. YAML colado (`.pa.yaml`) é igual nos dois.
- **Antes de commitar**, as três saídas limpas:

  ```bash
  python tools/lint_skills.py      # 0 erro(s)
  python -m pytest tests -q        # sem falha
  claude plugin validate .         # e claude plugin validate ./en
  ```
