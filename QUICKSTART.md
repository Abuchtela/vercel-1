# ClawWork Quick Start Guide

This is a condensed version of the full setup guide. For detailed instructions, see [`clawmode_integration/README.md`](clawmode_integration/README.md).

## 5-Minute Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install nanobot
pip install nanobot-ai

# 3. Initialize nanobot
nanobot onboard

# 4. Configure ClawWork
# Copy config.example.json to ~/.nanobot/config.json and edit:
# - Add your API key under providers
# - Set agents.clawwork.enabled = true

# 5. Install the skill
mkdir -p ~/.nanobot/workspace/skills/clawmode
cp clawmode_integration/skill/SKILL.md ~/.nanobot/workspace/skills/clawmode/SKILL.md

# 6. Set Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 7. Check status
python -m clawmode_integration.cli status
```

## Test Commands

```bash
# Start the gateway (listens on all enabled channels)
python -m clawmode_integration.cli gateway

# Start local agent CLI
python -m clawmode_integration.cli agent

# Send a single message
python -m clawmode_integration.cli agent -m "What can you do?"

# Assign a paid task
python -m clawmode_integration.cli agent -m "/clawwork Write a guide for Docker"
```

## Key Features

- ✅ **Token cost tracking** - Every LLM call deducts from balance
- ✅ **Task classification** - 40 occupations with BLS wage data
- ✅ **Work evaluation** - LLM-based quality scoring
- ✅ **Economic tools** - decide_activity, submit_work, learn, get_status
- ✅ **Survival mechanics** - Balance determines status (thriving → depleted)

## Configuration Example

Minimal `~/.nanobot/config.json`:

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

## Project Structure

```
clawmode_integration/      # Integration layer
├── cli.py                 # Typer CLI commands
├── agent_loop.py          # Economic message loop
├── task_classifier.py     # Task valuation
├── provider_wrapper.py    # Token tracking
├── tools.py               # Economic tools
├── skill/SKILL.md         # Agent instructions
└── README.md              # Full setup guide

livebench/                 # Economic engine
├── economic/tracker.py    # Balance tracking
├── work/evaluator.py      # Quality evaluation
└── memory/memory.py       # Learning storage

scripts/task_value_estimates/
└── occupation_to_wage_mapping.json  # 40 occupations + wages
```

## Next Steps

1. **Read the full guide**: [`clawmode_integration/README.md`](clawmode_integration/README.md)
2. **Configure a channel**: Add Telegram, Discord, or Slack in `~/.nanobot/config.json`
3. **Customize pricing**: Adjust `tokenPricing` to match your model costs
4. **Test locally**: Run `python -m clawmode_integration.cli agent` first
5. **Deploy gateway**: Run `python -m clawmode_integration.cli gateway` for production

## Troubleshooting

**Module not found errors?**
→ Set `PYTHONPATH`: `export PYTHONPATH="$(pwd):$PYTHONPATH"`

**ClawWork not enabled?**
→ Check `~/.nanobot/config.json` has `agents.clawwork.enabled = true`

**No API key?**
→ Add provider credentials under `providers` in config

**Gateway doesn't start?**
→ Install dependencies: `pip install -r requirements.txt`

## Documentation

- 📖 [Full Setup Guide](clawmode_integration/README.md) - Complete walkthrough
- 📦 [Project README](CLAWWORK_README.md) - Architecture and features
- 🎓 [Skill File](clawmode_integration/skill/SKILL.md) - Agent instructions
- ⚙️ [Example Config](config.example.json) - Configuration template

## Support

For issues or questions, see the troubleshooting section in [`clawmode_integration/README.md`](clawmode_integration/README.md).
