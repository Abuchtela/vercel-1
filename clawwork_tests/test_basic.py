"""
Test basic functionality of ClawWork components.

This test verifies that the core components can be instantiated
and perform basic operations without external dependencies.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from livebench.economic.tracker import EconomicTracker
from livebench.memory.memory import MemoryStore


def test_economic_tracker():
    """Test EconomicTracker basic operations."""
    print("Testing EconomicTracker...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = EconomicTracker(
            signature="test-agent",
            data_path=Path(tmpdir),
            initial_balance=1000.0,
            input_price_per_million=2.5,
            output_price_per_million=10.0,
        )
        
        # Check initial state
        assert tracker.balance == 1000.0, "Initial balance should be 1000.0"
        assert tracker.get_survival_status() == "thriving", "Initial status should be thriving"
        
        # Track some tokens
        tracker.start_task("task1")
        cost = tracker.track_tokens(input_tokens=1000, output_tokens=500)
        
        # Cost should be (1000/1M * 2.5) + (500/1M * 10) = 0.0025 + 0.005 = 0.0075
        expected_cost = 0.0075
        assert abs(cost - expected_cost) < 0.0001, f"Cost should be {expected_cost}, got {cost}"
        
        # Balance should decrease
        assert tracker.balance < 1000.0, "Balance should decrease after tracking tokens"
        
        # End task
        tracker.end_task(metadata={"test": "data"})
        
        # Check that cost file was created
        costs_file = Path(tmpdir) / "test-agent" / "economic" / "token_costs.jsonl"
        assert costs_file.exists(), "Token costs file should be created"
        
        # Add payment
        tracker.add_payment(50.0, reason="test_payment")
        assert tracker.balance > 1000.0 - 0.01, "Balance should increase after payment"
        
        print("✓ EconomicTracker tests passed")


def test_memory_store():
    """Test MemoryStore basic operations."""
    print("Testing MemoryStore...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryStore(
            signature="test-agent",
            data_path=Path(tmpdir),
        )
        
        # Add an entry
        entry = memory.add_entry(
            content="Test insight",
            category="technical",
            metadata={"confidence": 0.9},
        )
        
        assert entry["content"] == "Test insight", "Entry content should match"
        assert entry["category"] == "technical", "Entry category should match"
        
        # Retrieve entries
        entries = memory.get_entries(category="technical")
        assert len(entries) == 1, "Should retrieve 1 entry"
        assert entries[0]["content"] == "Test insight", "Retrieved entry should match"
        
        # Search entries
        results = memory.search_entries("insight")
        assert len(results) == 1, "Should find 1 result"
        
        print("✓ MemoryStore tests passed")


def test_occupation_data():
    """Test that occupation wage mapping exists and is valid."""
    print("Testing occupation data...")
    
    data_file = Path(__file__).parent.parent / "scripts" / "task_value_estimates" / "occupation_to_wage_mapping.json"
    
    assert data_file.exists(), "Occupation data file should exist"
    
    with open(data_file) as f:
        data = json.load(f)
    
    assert isinstance(data, dict), "Occupation data should be a dictionary"
    assert len(data) > 0, "Occupation data should not be empty"
    
    # Check structure of first occupation
    first_occupation = next(iter(data.values()))
    assert "hourly_wage" in first_occupation, "Occupation should have hourly_wage"
    assert isinstance(first_occupation["hourly_wage"], (int, float)), "Wage should be numeric"
    
    print(f"✓ Loaded {len(data)} occupations")


def test_skill_file():
    """Test that skill file exists and has correct frontmatter."""
    print("Testing skill file...")
    
    skill_file = Path(__file__).parent.parent / "clawmode_integration" / "skill" / "SKILL.md"
    
    assert skill_file.exists(), "Skill file should exist"
    
    content = skill_file.read_text()
    
    # Check for frontmatter
    assert content.startswith("---"), "Skill file should have frontmatter"
    assert "always: true" in content, "Skill should be marked as always active"
    
    # Check for key sections
    assert "Economic Metrics" in content, "Should have Economic Metrics section"
    assert "decide_activity" in content, "Should document decide_activity tool"
    assert "submit_work" in content, "Should document submit_work tool"
    assert "learn" in content, "Should document learn tool"
    assert "get_status" in content, "Should document get_status tool"
    
    print("✓ Skill file is valid")


def main():
    """Run all tests."""
    print("=" * 50)
    print("ClawWork Component Tests")
    print("=" * 50)
    print()
    
    try:
        test_economic_tracker()
        test_memory_store()
        test_occupation_data()
        test_skill_file()
        
        print()
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        return 0
    
    except AssertionError as e:
        print()
        print("=" * 50)
        print(f"Test failed: {e}")
        print("=" * 50)
        return 1
    
    except Exception as e:
        print()
        print("=" * 50)
        print(f"Error during tests: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(main())
