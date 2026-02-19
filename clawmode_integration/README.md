# ClawMode + Nanobot: Setup Guide

This guide walks you through setting up ClawMode from scratch on a fresh
machine. By the end you'll have nanobot running as a gateway with ClawWork
economic tracking — every chat message costs tokens, and the agent can check
its balance.

**All configuration lives in `~/.nanobot/config.json`** — no separate config
files needed.

---

## What You're Building

```
You (Telegram / Discord / CLI / ...)
  │
  ▼
nanobot gateway
  │
  ├── nanobot tools (file, shell, web, message, spawn, cron)
  ├── clawwork tools (get_status, decide_activity, submit_work, learn)
  ├── /clawwork command → TaskClassifier → paid task assignment
  └── TrackedProvider → every LLM call deducts from agent's balance
```

The agent gets all of nanobot's built-in capabilities **plus** 4 economic
tools. Every response includes a cost footer showing how much the message
cost and the remaining balance.

### The `/clawwork` Command

Send `/clawwork <instruction>` from any connected channel to assign a paid
task. The system will:

1. **Classify** the instruction — pick the best-fit occupation from 40
   categories (using BLS wage data) and estimate professional hours
2. **Compute task value** — `hours × hourly_wage` (e.g. 2h × $44.96/hr = $89.92)
3. **Assign the task** to the agent with full context
4. **Evaluate** the submitted work and pay proportional to quality

Example:

```
/clawwork Write a market analysis for electric vehicles
```

→ Classified as "Market Research Analysts and Marketing Specialists" at $38.71/hr,
  estimated 3 hours = $116.13 max payment.

Regular (non-`/clawwork`) messages are cost-tracked but don't trigger task
assignment or evaluation.

---

## Architecture

```
clawmode_integration/
├── __init__.py             # Package exports
├── cli.py                  # Typer CLI — gateway command, reads from nanobot config
├── agent_loop.py           # ClawWorkAgentLoop — /clawwork interception + economic tracking
├── task_classifier.py      # TaskClassifier — occupation classification via LLM
├── provider_wrapper.py     # TrackedProvider — token cost tracking wrapper
├── tools.py                # ClawWork tools (decide_activity, submit_work, learn, get_status)
├── skill/
│   └── SKILL.md            # Nanobot skill file (agent instructions)
└── README.md               # This file
```

### Key Components

**`ClawWorkAgentLoop`** (`agent_loop.py`): Subclasses nanobot's `AgentLoop`.
- Intercepts `/clawwork` commands in `_process_message()`
- Wraps every message with `start_task()` / `end_task()` for cost tracking
- Appends cost footer to responses
- Creates a `TaskClassifier` using the same tracked provider

**`TaskClassifier`** (`task_classifier.py`): Classifies free-form instructions.
- Loads 40 occupations + hourly wages from `scripts/task_value_estimates/occupation_to_wage_mapping.json`
- Sends one LLM call (temp=0.3, JSON output) to pick occupation + estimate hours
- Fuzzy-match fallback (case-insensitive, substring) for robustness
- Falls back to "General and Operations Managers" at $64/hr if classification fails entirely

**`TrackedProvider`** (`provider_wrapper.py`): Wraps nanobot's LLM provider.
- Intercepts every `chat()` call and feeds token usage into `EconomicTracker`
- Uses actual token counts from litellm (not estimation)

**`cli.py`**: Gateway entry point.
- Reads all config from `~/.nanobot/config.json` under `agents.clawwork`
- `_inject_evaluation_credentials()` — sets `EVALUATION_API_KEY`, `EVALUATION_API_BASE`,
  `EVALUATION_MODEL` env vars from nanobot's provider config so the `LLMEvaluator` works
  without a separate `OPENAI_API_KEY`
- `_build_state()` — constructs `ClawWorkState` from nanobot config
- `gateway()` — wires up nanobot infra + ClawWork state + agent loop

### Provider Unification

The `LLMEvaluator` (in `livebench/work/llm_evaluator.py`) needs API credentials to
evaluate submitted work. Instead of requiring a separate `OPENAI_API_KEY` env var,
`cli.py` automatically injects credentials from nanobot's `~/.nanobot/config.json`:

```
nanobot config.json
  └── provider.api_key       → EVALUATION_API_KEY
  └── api_base               → EVALUATION_API_BASE
  └── agents.defaults.model  → EVALUATION_MODEL
```

This means **one API key configuration** (in nanobot) drives both the agent LLM
calls and work evaluation. No livebench code changes required.

---

## Step 1: Create a Python Environment

Nanobot requires Python 3.11+.

```bash
# With conda
conda create -n clawmode python=3.11 -y
conda activate clawmode

# Or with venv
python3.11 -m venv .venv
source .venv/bin/activate
```

## Step 2: Clone the Repo

```bash
git clone <your-repo-url> ClawWork
cd ClawWork
```

The repo contains two relevant directories:

```
ClawWork/
├── livebench/                # ClawWork economic engine (Python package)
└── clawmode_integration/     # The glue (this package)
```

## Step 3: Install Dependencies

**Install nanobot** (pick one):

```bash
# From source (latest features, recommended for development)
git clone https://github.com/HKUDS/nanobot.git
cd nanobot && pip install -e . && cd ..

# With uv (stable, fast)
uv tool install nanobot-ai

# From PyPI (stable)
pip install nanobot-ai
```

**Install ClawWork dependencies:**

```bash
pip install -r requirements.txt
```

Verify the install:

```bash
nanobot --version
```

## Step 4: Initialize Nanobot

Run the onboard command to create config and workspace directories:

```bash
nanobot onboard
```

This creates:

```
~/.nanobot/
├── config.json       # LLM provider keys, model, channels, clawwork config
└── workspace/
    ├── AGENTS.md     # Agent personality/instructions
    ├── SOUL.md       # Agent values
    ├── USER.md       # Info about you
    ├── HEARTBEAT.md  # Periodic tasks
    ├── memory/
    │   └── MEMORY.md # Long-term memory
    └── skills/       # Custom skills (we'll add one here)
```

## Step 5: Configure `~/.nanobot/config.json`

Open `~/.nanobot/config.json` and configure three things:

### 5a. Add your API key

Add at least one provider API key under `providers`:

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-YOUR_KEY_HERE"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    }
  }
}
```

Other providers work too — OpenAI, Anthropic, DeepSeek, Gemini, Groq, etc.
Just add the key under the right name and set the model.

### 5b. Enable ClawWork

Add the `clawwork` section under `agents`:

```json
{
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    },
    "clawwork": {
      "enabled": true,
      "signature": "my-agent",
      "initialBalance": 1000.0,
      "tokenPricing": {
        "inputPrice": 2.50,
        "outputPrice": 10.00
      }
    }
  }
}
```

### ClawWork config fields

| Field | What it does | Default |
|-------|-------------|---------|
| `enabled` | Enable ClawWork economic tracking | `false` |
| `signature` | Agent name (data saved under this directory) | Derived from model name |
| `initialBalance` | Starting dollars | `1000.0` |
| `tokenPricing.inputPrice` | Cost per 1M input tokens | `2.5` |
| `tokenPricing.outputPrice` | Cost per 1M output tokens | `10.0` |
| `taskValuesPath` | Path to task value estimates JSONL (optional) | `""` |
| `metaPromptsDir` | Path to evaluation meta-prompts | `"./eval/meta_prompts"` |
| `dataPath` | Root directory for agent data | `"./livebench/data/agent_data"` |

> **Set `tokenPricing` to match your actual model costs.**

### 5c. Full example config

Here's a minimal complete `~/.nanobot/config.json`:

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-YOUR_KEY_HERE"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    },
    "clawwork": {
      "enabled": true,
      "signature": "gpt-4o-agent",
      "initialBalance": 1000.0,
      "tokenPricing": {
        "inputPrice": 2.50,
        "outputPrice": 10.00
      }
    }
  }
}
```

### Quick test that nanobot works on its own

```bash
nanobot agent -m "Hello, what can you do?"
```

You should get a response. If you see an API key error, double-check your
`~/.nanobot/config.json`.

## Step 6: Install the ClawMode Skill

Copy the skill file into nanobot's workspace so the agent always knows
about the economic protocol:

```bash
mkdir -p ~/.nanobot/workspace/skills/clawmode
cp clawmode_integration/skill/SKILL.md ~/.nanobot/workspace/skills/clawmode/SKILL.md
```

This teaches the agent about the balance system, survival statuses, and the
4 economic tools. The `always: true` frontmatter means it's loaded into
every conversation.

## Step 7: Set PYTHONPATH

The gateway needs to find `clawmode_integration` and `livebench` (ClawWork engine) as
importable packages. Add the repo root to your Python path:

```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

Add this to your shell profile (`~/.bashrc` or `~/.zshrc`) to make it
permanent.

## Step 8: Start Chatting

There are two ways to run ClawMode:

### Option A: Local CLI (recommended for quick testing)

```bash
# Interactive mode
python -m clawmode_integration.cli agent

# Single message
python -m clawmode_integration.cli agent -m "What tools do you have?"

# Assign a paid task
python -m clawmode_integration.cli agent -m "/clawwork Write a market analysis for EVs"
```

This works exactly like `nanobot agent` but with full ClawWork economic
tracking — every message is cost-tracked, `/clawwork` is available, and
you see a balance footer on each response.

### Option B: Channel gateway (Telegram, Discord, Slack, etc.)

```bash
python -m clawmode_integration.cli gateway
```

This listens for messages on all enabled channels (configured in Step 9).

### What happens on startup

```
🔧 Evaluation using separate API key (EVALUATION_API_KEY)
🔧 Evaluation model: openai/gpt-4o
✅ LLM-based evaluation enabled (strict mode - no fallback)
✅ Initialized economic tracker for gpt-4o-agent
   Starting balance: $1000.00
```

The gateway automatically injects your nanobot provider credentials for the
work evaluator — no separate `OPENAI_API_KEY` env var needed.

---

## Step 9 (Optional): Connect a Chat Channel

Edit `~/.nanobot/config.json` to enable one or more channels, then restart
the gateway.

### Telegram (easiest)

1. Message [@BotFather](https://t.me/BotFather) on Telegram → `/newbot` → get a token
2. Message [@userinfobot](https://t.me/userinfobot) → get your numeric user ID
3. Add to config:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "123456789:ABCdef...",
      "allowFrom": ["your_user_id"]
    }
  }
}
```

4. Restart the gateway. Message your bot on Telegram.

### Discord

1. Create an app at https://discord.com/developers/applications
2. Bot tab → create bot → copy token
3. Enable **MESSAGE CONTENT INTENT** under Privileged Gateway Intents
4. Add to config:

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "your_bot_token",
      "allowFrom": ["your_user_id"]
    }
  }
}
```

### Slack

1. Create app at https://api.slack.com/apps → Socket Mode → enable
2. Get bot token (`xoxb-...`) and app-level token (`xapp-...`)
3. Add to config:

```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "botToken": "xoxb-...",
      "appToken": "xapp-..."
    }
  }
}
```

### Other channels

Nanobot supports 9 channels total: Telegram, Discord, Slack, WhatsApp,
Email, Feishu, DingTalk, MoChat, QQ. See the
[nanobot README](https://github.com/HKUDS/nanobot#-chat-apps) for setup details on each.

---

## How It Works

### Regular Messages

Every message goes through this flow:

```
1. User sends message (via Telegram / Discord / etc.)
2. nanobot routes it to ClawWorkAgentLoop._process_message()
3. EconomicTracker.start_task()
4. LLM call → TrackedProvider intercepts → tracker.track_tokens()
5. Agent may call tools (nanobot built-ins + clawwork economic tools)
6. Loop back to step 4 if more tool calls needed
7. Final response + cost footer sent back to user
8. EconomicTracker.end_task() → writes to token_costs.jsonl
```

### `/clawwork` Messages

```
1. User sends "/clawwork Write a market analysis for EVs"
2. ClawWorkAgentLoop intercepts the /clawwork prefix
3. TaskClassifier.classify(instruction)
   → LLM call picks occupation + estimates hours
   → Computes task_value = hours × hourly_wage
4. Synthetic task dict created (task_id, occupation, max_payment, etc.)
5. Message rewritten with task context and sent to agent loop
6. Agent works on the task, calls submit_work when done
7. WorkEvaluator scores the submission (using nanobot's provider credentials)
8. Payment = quality_score × task_value added to balance
9. Response + cost footer sent back to user
```

### Tools

The agent has 14 tools available:

| Source | Tools |
|--------|-------|
| nanobot | `read_file`, `write_file`, `edit_file`, `list_dir`, `exec`, `web_search`, `web_fetch`, `message`, `spawn`, `cron` |
| clawwork | `decide_activity`, `submit_work`, `learn`, `get_status` |

Every response gets a footer like:

```
---
Cost: $0.0075 | Balance: $999.99 | Status: thriving
```

### Where data is saved

Agent economic data goes to `{dataPath}/{signature}/`:

```
livebench/data/agent_data/my-agent/
├── economic/
│   ├── balance.jsonl       # One line per day
│   └── token_costs.jsonl   # One line per message (detailed costs)
├── work/
│   ├── evaluations.jsonl   # Work evaluation results
│   └── *.txt               # Work artifacts
└── memory/
    └── memory.jsonl        # Learning entries
```

---

## Troubleshooting

**`nanobot: command not found`**
→ Did you install nanobot (`pip install nanobot-ai`)? Make sure your venv is activated.

**`ModuleNotFoundError: No module named 'clawmode_integration'`**
→ Set `PYTHONPATH` to include the repo root: `export PYTHONPATH="$(pwd):$PYTHONPATH"`

**`ClawWork is not enabled`**
→ Set `agents.clawwork.enabled` to `true` in `~/.nanobot/config.json`.

**`No API key configured`**
→ Check `~/.nanobot/config.json`. Make sure the key is under the right
provider name and the model matches.

**`Neither EVALUATION_API_KEY nor OPENAI_API_KEY found`**
→ The gateway should inject credentials automatically from nanobot's config.
If you see this error, check that `~/.nanobot/config.json` has a valid
provider with an `apiKey` set.

**`Warning: No channels enabled`**
→ Normal if you haven't configured any channels yet. Add one in Step 9.

**Gateway starts but no messages arrive**
→ Check `allowFrom` in your channel config. An empty list means "allow
everyone". A non-empty list is a whitelist — make sure your user ID is in it.

**Balance not decreasing**
→ The balance only tracks costs through the ClawMode gateway. Direct
`nanobot agent` commands bypass the economic tracker.

**`/clawwork` not working**
→ Make sure the message starts with `/clawwork` (case-insensitive) followed
by a space and an instruction. The classifier needs at least a few words to
pick an occupation. Check logs for classification output.

**Classification always returns fallback**
→ Verify `scripts/task_value_estimates/occupation_to_wage_mapping.json` exists.
The classifier loads occupations from this file at startup.

---

## Quick Reference

```bash
# One-time setup
conda create -n clawmode python=3.11 -y && conda activate clawmode
pip install nanobot-ai && pip install -r requirements.txt
nanobot onboard
# Edit ~/.nanobot/config.json → add API key + agents.clawwork.enabled = true
cp clawmode_integration/skill/SKILL.md ~/.nanobot/workspace/skills/clawmode/SKILL.md
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Chat locally (like `nanobot agent` but with economic tracking)
python -m clawmode_integration.cli agent

# Single message
python -m clawmode_integration.cli agent -m "Hello"

# Assign a paid task
python -m clawmode_integration.cli agent -m "/clawwork Write a market analysis for EVs"

# Channel gateway (Telegram, Discord, etc.)
python -m clawmode_integration.cli gateway
```
