# ClawWork Files Index

Quick reference guide to all ClawWork files and their purposes.

## �� Documentation (Start Here!)

| File | Purpose | Size |
|------|---------|------|
| **[QUICKSTART.md](QUICKSTART.md)** | ⭐ 5-minute setup guide | Short |
| [clawmode_integration/README.md](clawmode_integration/README.md) | Complete setup walkthrough | Long |
| [CLAWWORK_README.md](CLAWWORK_README.md) | Project overview & architecture | Medium |
| [CLAWWORK_SUMMARY.md](CLAWWORK_SUMMARY.md) | Implementation details | Medium |
| [CLAWWORK_CONTRIBUTING.md](CLAWWORK_CONTRIBUTING.md) | Developer guide | Medium |
| [clawmode_integration/skill/SKILL.md](clawmode_integration/skill/SKILL.md) | Agent instructions | Medium |

## 🐍 Python Packages

### ClawMode Integration (`clawmode_integration/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package exports |
| `cli.py` | Typer CLI commands (gateway, agent, status) |
| `agent_loop.py` | ClawWorkAgentLoop - message processing |
| `task_classifier.py` | TaskClassifier - task valuation |
| `provider_wrapper.py` | TrackedProvider - token tracking |
| `tools.py` | Economic tools (decide_activity, submit_work, etc.) |

### Livebench Engine (`livebench/`)

| File | Purpose |
|------|---------|
| `economic/tracker.py` | EconomicTracker - balance management |
| `work/evaluator.py` | WorkEvaluator - quality scoring |
| `memory/memory.py` | MemoryStore - learning storage |

## 🔧 Configuration

| File | Purpose |
|------|---------|
| [config.example.json](config.example.json) | Configuration template |
| [requirements.txt](requirements.txt) | Python dependencies |
| [setup.py](setup.py) | Package installation |

## 📊 Data

| File | Purpose |
|------|---------|
| [scripts/task_value_estimates/occupation_to_wage_mapping.json](scripts/task_value_estimates/occupation_to_wage_mapping.json) | 40 occupations with BLS wages |

## 🧪 Testing

| File | Purpose |
|------|---------|
| [validate_structure.sh](validate_structure.sh) | Structure validation script |
| [clawwork_tests/test_basic.py](clawwork_tests/test_basic.py) | Component tests |

## 📋 Quick Command Reference

```bash
# Validation
./validate_structure.sh

# Testing
python clawwork_tests/test_basic.py

# CLI Commands
python -m clawmode_integration.cli status
python -m clawmode_integration.cli agent
python -m clawmode_integration.cli gateway
```

## 🗂️ File Categories

### For Users
1. Start with [QUICKSTART.md](QUICKSTART.md)
2. Read [clawmode_integration/README.md](clawmode_integration/README.md) for details
3. Use [config.example.json](config.example.json) as template

### For Developers
1. Read [CLAWWORK_CONTRIBUTING.md](CLAWWORK_CONTRIBUTING.md)
2. Review [CLAWWORK_SUMMARY.md](CLAWWORK_SUMMARY.md)
3. Check [CLAWWORK_README.md](CLAWWORK_README.md) for architecture

### For Integration
1. Core logic in `clawmode_integration/` package
2. Economic engine in `livebench/` package
3. Agent instructions in `clawmode_integration/skill/SKILL.md`

## 📈 Statistics

- **Total Files**: 26
- **Python Modules**: 13
- **Documentation**: 6
- **Configuration**: 3
- **Data**: 1
- **Tests**: 2
- **Scripts**: 1

## 🔍 Finding What You Need

**Want to...**
- **Get started quickly?** → [QUICKSTART.md](QUICKSTART.md)
- **Understand architecture?** → [CLAWWORK_README.md](CLAWWORK_README.md)
- **See implementation details?** → [CLAWWORK_SUMMARY.md](CLAWWORK_SUMMARY.md)
- **Configure the system?** → [config.example.json](config.example.json)
- **Contribute code?** → [CLAWWORK_CONTRIBUTING.md](CLAWWORK_CONTRIBUTING.md)
- **Add new occupations?** → `scripts/task_value_estimates/occupation_to_wage_mapping.json`
- **Customize agent behavior?** → `clawmode_integration/skill/SKILL.md`
- **Modify economic rules?** → `livebench/economic/tracker.py`
- **Change evaluation logic?** → `livebench/work/evaluator.py`
- **Add CLI commands?** → `clawmode_integration/cli.py`

---

**Created**: February 2026  
**Version**: 0.1.0 (Alpha)
