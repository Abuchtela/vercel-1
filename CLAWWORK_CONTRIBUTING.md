# Contributing to ClawWork

Thank you for your interest in contributing to ClawWork! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- A code editor (VS Code recommended)

### Setup Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ClawWork

# 2. Create a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install in development mode
pip install -e .

# 5. Set PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 6. Run validation
./validate_structure.sh
```

## Project Structure

```
clawmode_integration/          # Main integration package
├── __init__.py                # Package exports
├── cli.py                     # Typer CLI commands
├── agent_loop.py              # ClawWorkAgentLoop class
├── task_classifier.py         # TaskClassifier class
├── provider_wrapper.py        # TrackedProvider wrapper
├── tools.py                   # Economic tool definitions
└── skill/SKILL.md             # Agent skill file

livebench/                     # Economic engine package
├── __init__.py
├── economic/
│   ├── __init__.py
│   └── tracker.py             # EconomicTracker class
├── work/
│   ├── __init__.py
│   └── evaluator.py           # WorkEvaluator class
└── memory/
    ├── __init__.py
    └── memory.py              # MemoryStore class

scripts/
└── task_value_estimates/
    └── occupation_to_wage_mapping.json  # BLS wage data

clawwork_tests/                # Test suite
└── test_basic.py              # Basic component tests
```

## Development Workflow

### Making Changes

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** in the appropriate module

3. **Run tests**:
   ```bash
   python clawwork_tests/test_basic.py
   ```

4. **Validate structure**:
   ```bash
   ./validate_structure.sh
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

6. **Push and create a pull request**

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to all public functions and classes
- Keep functions focused and small
- Use descriptive variable names

### Testing

Add tests for new features in `clawwork_tests/`:

```python
def test_your_feature():
    """Test description."""
    # Setup
    # Action
    # Assert
    print("✓ Test passed")
```

Run tests before committing:
```bash
python clawwork_tests/test_basic.py
```

## Areas to Contribute

### 1. Core Functionality

- **Economic Tracker**: Enhance balance tracking and survival mechanics
- **Task Classifier**: Improve classification accuracy and add more occupations
- **Work Evaluator**: Enhance evaluation prompts and criteria
- **Tools**: Add new economic tools or improve existing ones

### 2. Integration

- **Nanobot Integration**: Improve the agent loop and provider wrapper
- **Channel Support**: Test and document channel integrations
- **CLI Commands**: Add new CLI commands or enhance existing ones

### 3. Documentation

- **Guides**: Improve setup guides and troubleshooting
- **Examples**: Add usage examples and case studies
- **API Docs**: Document function signatures and behavior

### 4. Testing

- **Unit Tests**: Add tests for individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test full workflow scenarios

### 5. Data

- **Occupation Data**: Update BLS wage data with new occupations
- **Evaluation Prompts**: Improve evaluation prompt quality
- **Example Tasks**: Add example task definitions

## Specific Contributions Needed

### High Priority

- [ ] Complete nanobot integration (requires nanobot API familiarity)
- [ ] Add comprehensive test suite
- [ ] Create Docker deployment guide
- [ ] Add CI/CD pipeline configuration

### Medium Priority

- [ ] Add more evaluation prompt templates
- [ ] Create visualization dashboard for economic data
- [ ] Add export/import functionality for agent data
- [ ] Improve error handling and logging

### Low Priority

- [ ] Add support for custom occupation lists
- [ ] Create web interface for configuration
- [ ] Add metrics and analytics features
- [ ] Create migration tools for data formats

## Code Review Process

1. **Submit PR** with clear description of changes
2. **Automated checks** run (when CI/CD is set up)
3. **Maintainer review** provides feedback
4. **Address feedback** and update PR
5. **Merge** once approved

## Adding New Occupations

To add occupations to the wage mapping:

1. Edit `scripts/task_value_estimates/occupation_to_wage_mapping.json`
2. Add entry with this structure:
   ```json
   "Occupation Title": {
     "hourly_wage": 45.00,
     "description": "Brief description of occupation"
   }
   ```
3. Source wage data from [BLS Occupational Employment Statistics](https://www.bls.gov/oes/)
4. Update count in validation script if needed
5. Test classification with the new occupation

## Modifying Economic Mechanics

When changing economic behavior:

1. Update `livebench/economic/tracker.py` for tracking logic
2. Update `clawmode_integration/skill/SKILL.md` to reflect changes
3. Update `clawmode_integration/README.md` documentation
4. Add tests for new behavior
5. Consider backward compatibility with existing data

## Documentation Standards

### Code Comments

```python
def function_name(param: str) -> dict:
    """
    Brief one-line description.
    
    More detailed explanation if needed. Can span multiple
    lines and include examples.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
    """
```

### README Structure

- Start with brief description
- Include quick start section
- Document all features clearly
- Provide troubleshooting section
- Link to related documentation

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Feature Requests**: Open a GitHub Issue with use case description
- **Security**: Email maintainers directly (do not open public issue)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- CONTRIBUTORS.md file (if created)

Thank you for contributing to ClawWork! 🎉
