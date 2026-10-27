# system-prompt-builder

A Python CLI to **build, preview, save, and live-test system prompts** with variables and mock data.  
Optional live testing against a configurable OpenAI-compatible endpoint (default: local **Ollama**).

No API keys required. Local-first. No secrets. Built for beginners and power users alike.

---

## Why this tool?

Dylan Asdale (founder of **Asdale Dynamics, LLC**) explains AI "like a friend would": plain English, step by step, never condescending.  
This tool is part of the LLC's focus on **beginner-friendly AI education**, **open-source apps and templates**, and **practical local-first utilities**.

---

## Features

- **Variables** — Use `{variable}` placeholders in your system prompt.
- **Mock data** — Provide defaults so prompts render instantly without typing values every time.
- **Preview** — See the template and its variables before rendering.
- **Save / Load** — Templates stored as JSON in `~/.local/share/system-prompt-builder/templates/`.
- **Export** — Save any template to a portable `.json` file.
- **Live test** — Send the rendered prompt to a local Ollama (or any OpenAI-compatible `/v1/chat/completions` endpoint) and see the model's reply.
- **Mock endpoint** — `--mock-endpoint` runs a zero-network, zero-key fake reply for demos and CI.
- **Configurable** — Set default endpoint URL and model via `--endpoint` / `--model` flags or a config file.

---

## Install

```bash
pip install -e .
```

Requires Python 3.9+. No external dependencies (stdlib only).

---

## Quick start

```bash
# Create a template with variables and mock defaults
system-prompt-builder new nurse-bot \
  --template "You are a {role}. Help {name} with {task}." \
  --mock role=nurse --mock name=Dylan --mock task=charting \
  --description "Nursing assistant prompt"

# List templates
system-prompt-builder list

# Preview template (shows variables and raw template)
system-prompt-builder preview nurse-bot

# Build (render with mock defaults)
system-prompt-builder build nurse-bot
# Output: You are a nurse. Help Dylan with charting.

# Build with overrides
system-prompt-builder build nurse-bot --variable name=Ada --variable task=meds
# Output: You are a nurse. Help Ada with meds.

# Save template to a portable file
system-prompt-builder save nurse-bot ./nurse-bot.json

# Live test against local Ollama (default http://localhost:11434/v1, model llama3.2)
system-prompt-builder test nurse-bot

# Or use the built-in mock endpoint (no network, no keys)
system-prompt-builder test nurse-bot --mock-endpoint
```

---

## Commands

| Command | Description |
|---------|-------------|
| `new <name> --template "..." [--mock KEY=VAL]... [--variable KEY=DESC]... [--description "..."]` | Create and save a new template |
| `build <name> [--variable KEY=VAL]...` | Render template and print the prompt |
| `preview <name>` | Show template, variables, and mock data |
| `save <name> <file.json>` | Export a stored template to a JSON file |
| `test <name> [--variable KEY=VAL]... [--endpoint URL] [--model NAME] [--api-key KEY] [--mock-endpoint]` | Send rendered prompt to an endpoint and print the reply |
| `list` | List all saved templates |

---

## Configuration

The tool stores templates and config in `~/.local/share/system-prompt-builder/` by default.  
Override with `--data-dir PATH` or set `SPB_DATA_DIR` environment variable.

Config file (`config.json` in the data dir) can hold:

```json
{
  "endpoint": "http://localhost:11434/v1",
  "model": "llama3.2"
}
```

---

## Live testing details

The `test` command sends the **rendered system prompt** plus a minimal user message (`"Ping"`) to the endpoint's `/v1/chat/completions` (OpenAI-compatible).  
Ollama exposes this at `http://localhost:11434/v1` by default.

```bash
# With Ollama running locally:
system-prompt-builder test my-template

# Custom endpoint & model:
system-prompt-builder test my-template \
  --endpoint http://my-server:8000/v1 \
  --model mistral
```

---

## Mock endpoint (for CI, demos, offline work)

```bash
system-prompt-builder test my-template --mock-endpoint
```

Returns a canned response instantly — no network, no keys, no server required.

---

## Template JSON format

```json
{
  "name": "nurse-bot",
  "template": "You are a {role}. Help {name} with {task}.",
  "variables": {
    "role": "The assistant's role",
    "name": "User's name",
    "task": "What to help with"
  },
  "mock_data": {
    "role": "nurse",
    "name": "Dylan",
    "task": "charting"
  },
  "description": "Nursing assistant prompt"
}
```

---

## Development

```bash
# Run tests (stdlib unittest, no pytest required)
PYTHONPATH=src python3 -m unittest discover -s tests -v

# Or run the module directly
python3 -m system_prompt_builder --help
```

---

## License

MIT License — Copyright (c) 2026 **Asdale Dynamics, LLC**  
See [LICENSE](LICENSE) for full text.

---

## About Asdale Dynamics, LLC

Founded October 2026 in Indiana by **Dylan Asdale** — registered nurse turned AI author.  
His book *The Massive AI Manual* and hub site [dylanasdale.github.io](https://dylanasdale.github.io) explain AI "like a friend would": plain English, step by step, never condescending.

**LLC focus areas:**
- Beginner-friendly AI education, books, and guides
- Open-source apps and templates: prompt tools, local-LLM utilities, MCP servers, agent skills
- Small-business and author tools: KDP/book publishing, marketing, reselling, bookkeeping
- Accessible life-admin helpers: paperwork organizers, budgeting, low-energy productivity (ADHD-friendly)
- Healthcare-worker AI aids (education only, never medical advice)
- Fun extras: gaming (FFXIV) and chess tools

Style: **clear, warm, polished, tested, local-first, no secrets or personal data.**