# Image mockups (`/pp-en:mockups`) — OpenAI image API

After the design system, `pp-en:mockups-agent` lists the app's pages and frame and writes
a spec. The `scripts/desenhar-mockups.py` script turns that spec into one image per screen, with the
project palette, for the process owner to approve **before** any YAML.

## Contents

1. [What the mockup is and is not](#1-what-the-mockup-is-and-is-not)
2. [Prerequisites: key, approval, Python](#2-prerequisites-key-approval-python)
3. [Model, size and quality are variables](#3-model-size-and-quality-are-variables)
4. [The `mockups.json` spec](#4-the-mockupsjson-spec)
5. [Step by step](#5-step-by-step)
6. [Common errors](#6-common-errors)
7. [Sources](#7-sources)

---

## 1. What the mockup is and is not

- It **is** a visual reference to validate with the people who will use the app:
  - which screens exist;
  - what each one shows;
  - where each action is;
  - how pop-ups and notifications look;
  - whether the palette works.
- It **is not** a source. The real screen comes from the component catalog and the `fx*` tokens (skill
  `powerapps-canvas`). Nobody measures pixels from the mockup or copies a color from the image: color comes from the design system.
- The image model still gets text position and sharpness wrong (OpenAI says so itself). A crooked label
  is not a design defect: judge structure, hierarchy and flow.

## 2. Prerequisites: key, approval, Python

| Item | Detail |
|---|---|
| `OPENAI_API_KEY` key | an OpenAI account with credit. Some GPT Image models require the organization's *Organization Verification* (without it, HTTP 403) |
| Security approval | the spec text (descriptions, palette, role names) goes out to OpenAI. Question 7.9 of `brainstorm.md`. Without approval, the phase continues without a mockup and this is recorded |
| Python 3.10+ | the script uses only the standard library |

**Set the key outside the chat**, in the terminal from which Claude Code will be opened:

```powershell
# PowerShell — this session only
$env:OPENAI_API_KEY = "<your-key>"
# PowerShell — permanent (open a new terminal afterwards)
setx OPENAI_API_KEY "<your-key>"
```

```bash
# bash/zsh — put it in ~/.bashrc or ~/.zshrc to make it permanent
export OPENAI_API_KEY="<your-key>"
```

Then reopen Claude Code from that terminal. The key **never** goes:

- into `power-platform.config.json`;
- into a versioned `.env`;
- into the git history;
- into the conversation.

To check that it is set, without showing it:

```bash
python -c "import os; print('OPENAI_API_KEY set' if os.environ.get('OPENAI_API_KEY') else 'OPENAI_API_KEY missing')"
```

## 3. Model, size and quality are variables

| Parameter | 1st `--option` | 2nd environment | 3rd `power-platform.config.json` | Default |
|---|---|---|---|---|
| model | `--modelo` | `OPENAI_IMAGE_MODEL` | `mockups.modelo` | `gpt-image-2` |
| size | `--tamanho` | — | `mockups.tamanho` | `1536x1024` |
| quality | `--qualidade` | — | `mockups.qualidade` | `high` |
| image folder | `--saida` | — | `mockups.pasta` | the spec folder |
| endpoint | — | `OPENAI_BASE_URL` | — | `https://api.openai.com/v1` |

`OPENAI_BASE_URL` is for a corporate proxy compatible with the OpenAI API.
- It must be `https`. `http` is only valid for `localhost`, because the key goes in the header.
- A redirect is not followed: it would take the key to another host.
- Azure OpenAI uses another URL and another authentication header, and this script does not support it.

**Models** (OpenAI documentation, checked on 2026-10):

| Model | Status |
|---|---|
| `gpt-image-2` | current (snapshot `gpt-image-2-2026-04-21`); it is the kit default |
| `gpt-image-2.5-sunburst` | newest, the most capable for generating and editing |
| `gpt-image-2.5-flare` | newest, fast |
| `gpt-image-1` | shut down on 2026-10-23 |
| `gpt-image-1.5`, `gpt-image-1-mini` | shut down on 2026-12-01 |

Switching models is just changing the variable. Check OpenAI's models page before fixing a
name in the config.

**Size:**
- The safe ones, accepted by all GPT Image models, are `1024x1024`, `1536x1024` and `1024x1536`.
- The default `1536x1024` is landscape, the closest to the 16:9 canvas.
- The 2.5 models accept a custom `WIDTHxHEIGHT`, for example `1920x1088`, with these rules:
  - width and height multiples of 16;
  - aspect ratio up to 3:1;
  - edge up to 3840.
- The script validates these rules and gives `WARNING M005` on a custom size, because not every model
  accepts it.

**Quality:**
- Values: `low`, `medium`, `high` and `auto`. `xhigh` and `max` exist only on the 2.5 models.
- Legible text on screen calls for `high`; `low` works for a cheap first draft.
- The cost per image depends on the model, the size and the quality. Check OpenAI's pricing
  page, do not estimate from memory.

## 4. The `mockups.json` spec

Template: `assets/mockups-template.json` (entity `Orders`, unit `AAA`). Location in the project:
`docs/planning/mockups/mockups.json`. The spec keys stay as the script validates them.

| Field | Required | Content |
|---|---|---|
| `app` | yes | app name |
| `idioma` | no (`en-US`) | language of all text visible in the image |
| `canvas` | no (`1920x1080`) | canvas resolution (T1); goes in the prompt as a reference |
| `design_system.paleta` | yes | `name (token)` → `#RRGGBB`, copied from section 3 of `ux-design-system.md` |
| `design_system.fonte`, `raio`, `estilo` | no | font, corner radius in px, style in one sentence |
| `moldura.header` | yes | the header, the same on all screens |
| `moldura.navegacao`, `notificacoes`, `popups`, `carregando`, `estados`, `rodape` | no | the rest of the frame |
| `telas[].id` | yes | `tl-NN-...`, lowercase, digits and hyphen; becomes the `.png` name |
| `telas[].nome`, `descricao` | yes | screen name and what appears on it |
| `telas[].inventario`, `objetivo`, `perfil`, `componentes`, `estado` | no | link to the inventory, logged-in role, catalog components, state shown (open modal, toast, empty...) |

The script rejects (ERROR) the following:
- a color outside `#RRGGBB`;
- a repeated id;
- a missing required field;
- **an e-mail that is not from a fictitious domain** (`@contoso.com`, `@example.com`), because the text goes
  to an external service.

## 5. Step by step

1. **The agent writes the spec.** `/pp-en:mockups` calls `pp-en:mockups-agent` with the project root and the
   plugin folder. The agent writes `screen-inventory.md` and `mockups.json`; it **has no
   Bash**, so the stage checks the spec:
   `python <skills>/power-platform/scripts/desenhar-mockups.py docs/planning/mockups/mockups.json --simular`
   `--simular` validates, shows each prompt and counts the images, with no key and no network.
2. **The user accepts.** The orchestrator shows the user:
   - how many images will be generated;
   - the model, the size and the quality;
   - that the prompt text goes to OpenAI.
   Without the user's "go ahead and generate", do not call the API.
3. **Check the key** with the command in section 2. If it is missing, the task is 🔴: tell the
   user how to set the key (section 2) and wait. Do not ask for the key in the conversation.
4. **Generate:** `python <skills>/power-platform/scripts/desenhar-mockups.py docs/planning/mockups/mockups.json`.
   - An image that already exists is skipped.
   - The default cap is 20 new images per run (`--max-imagens`).
   - It outputs one `.png` per screen and the `mockups.md` gallery, marked "generated — do not edit".
   - Each image is written to a `.tmp` and only then renamed: an interruption leaves no truncated PNG.
   - `429` and `5xx` retry twice, respecting `Retry-After`.
   - An error that would repeat on every screen stops the run: `3xx`, `400`, `401`, `403`,
     `404`, network or write. The gallery is still produced, with what already exists.
   - A prompt rejected by moderation (`moderation_blocked`) only skips that screen.
5. **Approve with the process owner** from the gallery. Record the acceptance (sentence and date) in the
   screen inventory.
6. **Adjust through the spec, never through the image.**
   - The frame or the palette changed: regenerate everything with `--sobrescrever`.
   - One screen changed: `--telas tl-02-new-order --sobrescrever`.

## 6. Common errors

| Output | Cause | What to do |
|---|---|---|
| exit 2 "set OPENAI_API_KEY in the environment before generating" | key missing from the Claude Code environment | section 2; reopen Claude Code from the terminal that has the variable |
| `M101 HTTP 401` | wrong or revoked key | create another in the OpenAI dashboard and set it again |
| `M101 HTTP 403` | organization without *Organization Verification* for GPT Image | complete the verification in the dashboard; or switch models |
| `M101 HTTP 404` or `400` mentioning the model | model name does not exist for the account | check `OPENAI_IMAGE_MODEL`, `--modelo` and `mockups.modelo` |
| `M101 HTTP 400` mentioning `size` or `quality` | a size or quality the model does not accept | go back to `1536x1024` and `high` |
| `M101 HTTP 429` | rate limit or credit | wait, or check billing |
| `M101 no connection` | network or proxy | `OPENAI_BASE_URL` for the proxy, or run from another network |
| `M101 HTTP 3xx` | the endpoint redirected (the key does not follow to another host) | point `OPENAI_BASE_URL` at the final address |
| exit 2 "OPENAI_BASE_URL must be https" | `OPENAI_BASE_URL` on `http` outside `localhost` | use `https` |
| exit 2 "space or control character" | key pasted with a line break or space in the middle | set the key again |
| `M102` | response without a PNG: not JSON, no `b64_json` (model outside the GPT Image family), invalid base64 | run only that screen again (`--telas`); check the model |
| `M103` | could not write the file (blocked by sync, antivirus, full disk) | free the folder or use `--saida` on another one |
| exit 2 "new images exceed --max-imagens" | spec too large for one run | generate in parts with `--telas` or raise the cap, on purpose |

## 7. Sources

- Image generation (parameters, sizes, quality, organization verification):
  <https://developers.openai.com/api/docs/guides/image-generation>
- Model `gpt-image-2`: <https://developers.openai.com/api/docs/models/gpt-image-2>
- Models and deprecations: <https://developers.openai.com/api/docs/models>,
  <https://developers.openai.com/api/docs/deprecations>
