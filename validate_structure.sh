#!/bin/bash

# Validation script for ClawWork structure
set -e

echo "🔍 Validating ClawWork structure..."
echo ""

# Check directories
echo "Checking directories..."
for dir in clawmode_integration livebench/economic livebench/work livebench/memory scripts/task_value_estimates; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir MISSING"
        exit 1
    fi
done

echo ""
echo "Checking key files..."

# Check key files
files=(
    "clawmode_integration/__init__.py"
    "clawmode_integration/cli.py"
    "clawmode_integration/agent_loop.py"
    "clawmode_integration/task_classifier.py"
    "clawmode_integration/provider_wrapper.py"
    "clawmode_integration/tools.py"
    "clawmode_integration/skill/SKILL.md"
    "clawmode_integration/README.md"
    "livebench/__init__.py"
    "livebench/economic/tracker.py"
    "livebench/work/evaluator.py"
    "livebench/memory/memory.py"
    "scripts/task_value_estimates/occupation_to_wage_mapping.json"
    "requirements.txt"
    "setup.py"
    "config.example.json"
    "CLAWWORK_README.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        exit 1
    fi
done

echo ""
echo "Checking occupation data..."
occupation_count=$(python3 -c "import json; data = json.load(open('scripts/task_value_estimates/occupation_to_wage_mapping.json')); print(len(data))")
echo "  ✓ Loaded $occupation_count occupations"

echo ""
echo "Checking skill file structure..."
if grep -q "always: true" clawmode_integration/skill/SKILL.md; then
    echo "  ✓ Skill marked as always active"
else
    echo "  ✗ Skill missing 'always: true' frontmatter"
    exit 1
fi

echo ""
echo "✅ All structure checks passed!"
echo ""
echo "📦 Package structure:"
find clawmode_integration livebench -name "*.py" | sort | sed 's/^/  /'

echo ""
echo "📝 Documentation files:"
find . -maxdepth 2 -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*" | sort | sed 's/^/  /'

echo ""
echo "✨ ClawWork structure is complete and valid!"
