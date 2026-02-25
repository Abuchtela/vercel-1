# ClawWork - Economic Agents on Nanobot

> Transform AI agents into economically-aware systems with survival mechanics, task valuation, and work evaluation.

This repository contains the **ClawMode Integration** for [nanobot](https://github.com/HKUDS/nanobot), enabling:

- 💰 **Token cost tracking** for every LLM call
- 📊 **Economic survival mechanics** (balance, status, payments)
- 🎯 **Task classification** using BLS occupation wage data
- ✅ **Work evaluation** via LLM-based quality scoring
- 🧠 **Learning and memory** systems for long-term improvement

## Quick Start

```bash
# 1. Set up Python environment
python3.11 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize nanobot
pip install nanobot-ai
nanobot onboard

# 4. Configure ClawWork
# Edit ~/.nanobot/config.json - see config.example.json

# 5. Install the skill
mkdir -p ~/.nanobot/workspace/skills/clawmode
cp clawmode_integration/skill/SKILL.md ~/.nanobot/workspace/skills/clawmode/SKILL.md

# 6. Set PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 7. Run the gateway
python -m clawmode_integration.cli gateway
```

## What is ClawWork?

ClawWork adds an **economic layer** to AI agents:

1. **Every message costs money** (based on token usage)
2. **Agents earn money** by completing tasks (evaluated for quality)
3. **Balance determines survival status** (thriving → depleted)
4. **Agents make strategic decisions** (work vs. learn vs. idle)

### The `/clawwork` Command

Users can assign paid tasks via `/clawwork`:

```
/clawwork Write a technical guide for Docker setup
```

The system:
1. **Classifies** the task (e.g., "Technical Writers" at $39.93/hr)
2. **Estimates time** (e.g., 2.5 hours)
3. **Calculates value** (2.5 × $39.93 = $99.83)
4. **Assigns to agent** with full context
5. **Evaluates submission** and pays based on quality

## Architecture

```
clawmode_integration/          # Integration layer
├── cli.py                     # Typer CLI
├── agent_loop.py              # Message processing + tracking
├── task_classifier.py         # Occupation classification
├── provider_wrapper.py        # Token cost tracking
├── tools.py                   # 4 economic tools
└── skill/SKILL.md             # Agent instructions

livebench/                     # Economic engine
├── economic/tracker.py        # Balance + cost tracking
├── work/evaluator.py          # Quality evaluation
└── memory/memory.py           # Learning storage

scripts/
└── task_value_estimates/
    └── occupation_to_wage_mapping.json  # BLS wage data (40 occupations)
```

## Key Components

### EconomicTracker
Tracks token costs and balance:
- Deducts cost per message (input + output tokens)
- Adds payment for completed work
- Calculates survival status
- Persists to `balance.jsonl` and `token_costs.jsonl`

### TaskClassifier
Classifies tasks into occupations:
- Uses LLM to match instruction → occupation
- Estimates professional hours
- Computes max payment (hours × wage)
- Fuzzy matching fallback

### WorkEvaluator
Evaluates work submissions:
- LLM-based quality scoring (0-1)
- Heuristic fallback if LLM unavailable
- Payment = quality × max_payment
- Stores evaluations in `evaluations.jsonl`

### TrackedProvider
Wraps nanobot's LLM provider:
- Intercepts every `chat()` call
- Extracts token usage from response
- Feeds to `EconomicTracker`

### ClawWorkAgentLoop
Extends nanobot's message loop:
- Intercepts `/clawwork` commands
- Wraps messages with `start_task()` / `end_task()`
- Appends cost footer to responses

## Economic Tools

Agents get 4 new tools:

| Tool | Purpose |
|------|---------|
| `decide_activity` | Choose work/learn/idle based on balance |
| `submit_work` | Submit completed work for payment |
| `learn` | Store insights in long-term memory |
| `get_status` | Check balance and survival metrics |

## Configuration

All config lives in `~/.nanobot/config.json`:

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-..."
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    },
    "clawwork": {
      "enabled": true,
      "signature": "my-agent",
      "initialBalance": 1000.0,
      "tokenPricing": {
        "inputPrice": 2.5,
        "outputPrice": 10.0
      }
    }
  }
}
```

See `config.example.json` for a complete template.

## Documentation

- **Setup Guide**: [`clawmode_integration/README.md`](clawmode_integration/README.md) - Complete walkthrough from scratch
- **Skill File**: [`clawmode_integration/skill/SKILL.md`](clawmode_integration/skill/SKILL.md) - Agent instructions
- **Example Config**: [`config.example.json`](config.example.json) - Template configuration

## Data Storage

Agent data is saved to `livebench/data/agent_data/{signature}/`:

```
my-agent/
├── economic/
│   ├── balance.jsonl       # Daily balance snapshots
│   ├── token_costs.jsonl   # Per-message costs
│   └── payments.jsonl      # Work payments
├── work/
│   ├── evaluations.jsonl   # Evaluation results
│   └── *.txt               # Work artifacts
└── memory/
    └── memory.jsonl        # Learning entries
```

## Requirements

- Python 3.11+
- nanobot-ai
- See `requirements.txt` for full list

## Development

```bash
# Clone the repo
git clone <your-repo-url>
cd ClawWork

# Install in development mode
pip install -e .

# Run the CLI
python -m clawmode_integration.cli --help
```

## License

See LICENSE file for details.

## Credits

Built on top of [nanobot](https://github.com/HKUDS/nanobot) by HKUDS.

Uses BLS (Bureau of Labor Statistics) wage data for task valuation.

---

**Status**: Alpha - Core functionality implemented, testing in progress.
