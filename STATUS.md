# STATUS.md — system-prompt-builder

## What was built

A Python CLI (`system-prompt-builder`) to **build, preview, save, and live-test system prompts** with variables and mock data, plus optional live testing against a configurable OpenAI-compatible endpoint (default: local Ollama).

### Package structure
```
src/system_prompt_builder/
├── __init__.py         # version 0.1.0
├── __main__.py         # python -m entry point
├── cli.py              # argparse CLI (new/build/preview/save/test/list)
├── models.py           # PromptTemplate dataclass (variables, mock data, rendering)
├── store.py            # TemplateStore (JSON persistence + config)
└── endpoint.py         # EndpointClient (Ollama/OpenAI-compatible) + MockEndpoint
tests/
├── test_models.py      # PromptTemplate, TemplateStore, MockEndpoint tests
└── test_cli.py         # Full CLI workflow tests
README.md
LICENSE
pyproject.toml
```

### Commands implemented
| Command | Description |
|---------|-------------|
| `new <name>` | Create a template with `--template`, `--mock`, `--variable`, `--description` |
| `build <name>` | Render template using mock defaults + `--variable` overrides |
| `preview <name>` | Show template, variables, mock data, description |
| `save <name> <file>` | Export template to portable JSON |
| `test <name>` | Send rendered prompt to endpoint; supports `--mock-endpoint`, `--endpoint`, `--model`, `--api-key` |
| `list` | List saved templates |

### Key features
- **Variables**: `{name}` placeholders in templates
- **Mock data**: Defaults so prompts render without manual input
- **Local-first**: Stores templates in `~/.local/share/system-prompt-builder/templates/`
- **Zero deps**: Stdlib only (`argparse`, `json`, `urllib`, `dataclasses`, `pathlib`, `re`, `tempfile`, `unittest`)
- **Mock endpoint**: `--mock-endpoint` runs a zero-network, zero-key fake reply for CI/demos
- **Default endpoint**: `http://localhost:11434/v1` (Ollama OpenAI-compatible), model `llama3.2`

---

## How to run

```bash
# Install (requires Python 3.9+)
pip install -e . --break-system-packages

# Or run directly without install
PYTHONPATH=src python3 -m system_prompt_builder --help

# Quick demo
system-prompt-builder new demo --template "You are a {role}. Hello {name}." --mock role=assistant --mock name=Dylan
system-prompt-builder list
system-prompt-builder preview demo
system-prompt-builder build demo
system-prompt-builder build demo --variable name=Ada
system-prompt-builder save demo /tmp/demo.json
system-prompt-builder test demo --mock-endpoint

# Run tests
python3 -m unittest discover -s tests -v
```

---

## Verification results

| Check | Result |
|-------|--------|
| Package builds (`pip install -e .`) | ✅ Success |
| CLI entry point works (`system-prompt-builder --help`) | ✅ Success |
| Module entry works (`python3 -m system_prompt_builder`) | ✅ Success |
| All 18 unit tests pass | ✅ Success |
| Template create/render/override works | ✅ Verified |
| Save/load round-trip works | ✅ Verified |
| Mock endpoint returns canned response | ✅ Verified |
| Live test command handles network error gracefully | ✅ Verified |
| README.md exists and credits Asdale Dynamics, LLC | ✅ Verified |
| LICENSE exists with exact copyright line | ✅ Verified |
| No external dependencies (stdlib only) | ✅ Verified |
| No secrets/API keys in any file | ✅ Verified |
| No `.github/workflows` files | ✅ Verified |

---

## Known gaps / future improvements

1. **No interactive prompts** — `new` requires all args via flags; an interactive mode could help beginners.
2. **Single user message in `test`** — Currently sends a fixed "Ping" user message; could add `--user` flag.
3. **No streaming support** — `stream: false` hardcoded; could add `--stream` for real-time output.
4. **Config file not auto-created** — User must manually create `config.json` or use flags.
5. **No template validation on load** — Malformed JSON could crash; could add try/except with friendly message.
6. **No bash/zsh completion** — Could generate completion scripts.
7. **No Windows path testing** — Only tested on Linux; `Path.home()` behavior may differ.
8. **No version command** — Could add `--version` flag.
9. **No `delete` command** — Templates can only be removed by deleting the JSON file manually.
10. **No `edit` command** — Updating a template requires re-creating with `new`.

---

## License & attribution

- **License**: MIT — Copyright (c) 2026 Asdale Dynamics, LLC
- **README** credits Asdale Dynamics, LLC per requirements
- **No Co-authored-by trailers** in commits
- **No secrets, API keys, or personal data** in any file