# Models: who thinks and who executes

The pipeline separates **the head** (each stage's session: talks to the user, defines the request,
judges what comes back) from **the hands** (the agents: write screens, flows, prototype and spec, and
prove what they did). Thinking, judging and holding the bar is the small slice of the work; writing,
running and fixing is the big slice. That is why the head can stay on the strongest model and the
hands on a faster, cheaper one, without losing quality, **as long as the judgment runs**
(`subagents.md`, "Judging the deliverable").

The profile is chosen in `/pp-en:new` and recorded by `scripts/modelos.py`.

## 1. Profiles

| Profile | Each stage's session | Architecture and QA | Mockups, prototype, screens, flows and SQL | Research | When |
|---|---|---|---|---|---|
| **Balanced** (recommended) | Opus | Opus | Sonnet | Sonnet | almost always: the strong one thinks and judges, the fast one executes |
| **Maximum** | `best` | Opus | Opus | Sonnet | critical app or a team with no patience for revisions; costs more |
| **Economical** | Sonnet | Sonnet | Sonnet | Haiku | throwaway prototype, tight quota; expect more revisions |
| **Inherit** | the model the session opens with | same | same | same | whoever already controls the model on their own |

`best` uses Fable if the account has access, otherwise Opus. It only applies to the session: an agent
accepts `fable`, `opus`, `sonnet` and `haiku`.

`python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" perfis` prints the profiles
in the format of the `/pp-en:new` preview.

## 2. How it is applied

| Where | How | What overrides it |
|---|---|---|
| Each stage's session | `"model"` in the project's `.claude/settings.local.json`: Claude Code reads it when it opens the session in the folder. Since each stage is a new session, the choice applies by itself | `/model` in the session, `--model` and the `ANTHROPIC_MODEL` variable |
| Each agent | the stage runs `modelos.py de <agent>` and passes the answer as `model` in the call; an empty line = do not pass `model` (inherits the session) | nothing: the call's `model` wins over the agent's frontmatter |
| Reasoning effort | `effort: high` in the frontmatter of `architecture-agent` and `qa-agent` (they plan and judge), `medium` on `research-agent`; the others inherit the session's | the session's `effort` does not win over the agent's |

The plugin **does not switch the model in the middle of a session**: a skill's `model:` only applies to
the turn. That is why "Next step" reminds you of the model and the right `/model`.

`settings.local.json` is personal (each person has their own account and access): `modelos.py` puts
the line in `.gitignore`. The team's choice stays in `power-platform.config.json` (`modelos`).

## 3. Changing later

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" aplicar equilibrado --execucao opus
python "${CLAUDE_PLUGIN_ROOT}/skills/power-platform/scripts/modelos.py" mostrar
```

`--sessao`, `--planejamento`, `--execucao` and `--pesquisa` override one role on top of the profile.
It applies from the next session (the current one stays on the model it opened with; `/model` switches
immediately).

## 4. Measuring: is the profile keeping up?

The **Verdict** column of `STATE.md` (and of `/pp-en:progress`) counts the verdicts per stage: `✓`
accepted, `↻` revision, `⚠` escalated.

| Signal | What to do |
|---|---|
| a build with more than one revision per wave, on average | `aplicar <profile> --execucao opus` |
| revisions for the same cause (e.g. a property Studio rejects) | the problem is the request or the skill, not the model: fix the request |
| frequent `⚠` in architecture | a decision is missing from the PRD: go back to the user, do not switch models |
| no revisions across several waves | the profile can step down (`economico`) if cost matters |

## 5. Cautions

- Screen YAML is the most fragile file in the kit: it is where a smaller model fails first. The
  validators catch the syntax; judgment and pasting into Studio catch the rest.
- A strong model in the hands does not replace judgment: the session judges on any profile.
- No profile changes what goes outside: the mockups' image API stays behind the "may generate" approval only.
