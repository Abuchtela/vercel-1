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

# Minimum submission length to trigger structured quality scoring (heuristic evaluator)
_STRUCTURED_SUBMISSION_LENGTH = 600

from livebench.economic.tracker import EconomicTracker
from livebench.memory.memory import MemoryStore
from livebench.work.evaluator import WorkEvaluator
from clawmode_integration import (
    ClawWorkAgentLoop,
    ClawWorkState,
    create_agent_loop_with_tracking,
    TaskClassifier,
    TrackedProvider,
    create_clawwork_tools,
)


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


def test_work_evaluator():
    """Test WorkEvaluator heuristic evaluation."""
    print("Testing WorkEvaluator...")

    with tempfile.TemporaryDirectory() as tmpdir:
        evaluator = WorkEvaluator(
            signature="test-agent",
            data_path=Path(tmpdir),
            use_strict_eval=False,
        )

        task = {
            "task_id": "task_001",
            "instruction": "Write a short guide",
            "max_payment": 100.0,
        }

        result = evaluator.evaluate_work(task=task, submission="A" * _STRUCTURED_SUBMISSION_LENGTH + "\n\n## Section\n- Point 1")
        assert 0.0 <= result["quality_score"] <= 1.0, "Quality score should be between 0 and 1"
        assert result["actual_payment"] <= result["max_payment"], "Payment should not exceed max"

        evals = evaluator.get_evaluations()
        assert len(evals) == 1, "Should have one evaluation"

        print("✓ WorkEvaluator tests passed")


def test_clawwork_tools():
    """Test create_clawwork_tools and all four tools."""
    print("Testing ClawWork tools...")

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        tracker = EconomicTracker(
            signature="test-agent",
            data_path=path,
            initial_balance=500.0,
        )
        evaluator = WorkEvaluator(
            signature="test-agent",
            data_path=path,
            use_strict_eval=False,
        )
        memory = MemoryStore(signature="test-agent", data_path=path)
        state = ClawWorkState(
            tracker=tracker,
            evaluator=evaluator,
            memory=memory,
            classifier=None,
        )

        tools = create_clawwork_tools(state)
        assert len(tools) == 4, f"Expected 4 tools, got {len(tools)}"

        tool_names = [t["name"] for t in tools]
        assert "decide_activity" in tool_names
        assert "submit_work" in tool_names
        assert "learn" in tool_names
        assert "get_status" in tool_names

        # get_status tool
        get_status = next(t for t in tools if t["name"] == "get_status")
        status = get_status["function"]()
        assert status["balance"] == 500.0
        assert status["survival_status"] == "thriving"

        # decide_activity tool
        decide = next(t for t in tools if t["name"] == "decide_activity")
        decision = decide["function"](context="testing")
        assert decision["recommended_activity"] in ("work", "learn", "balanced")

        # learn tool
        learn = next(t for t in tools if t["name"] == "learn")
        result = learn["function"](insight="Test insight", category="technical")
        assert result["success"] is True

        # submit_work with unknown task
        submit = next(t for t in tools if t["name"] == "submit_work")
        result = submit["function"](task_id="nonexistent", submission="some work")
        assert result["success"] is False

        # submit_work with known task
        state.current_tasks["task_x"] = {
            "task_id": "task_x",
            "instruction": "Write something",
            "max_payment": 50.0,
        }
        result = submit["function"](task_id="task_x", submission="A" * _STRUCTURED_SUBMISSION_LENGTH)
        assert result["success"] is True
        assert 0.0 <= result["quality_score"] <= 1.0
        assert "task_x" not in state.current_tasks

        print("✓ ClawWork tools tests passed")


def test_tracked_provider():
    """Test TrackedProvider wraps provider and forwards token usage."""
    print("Testing TrackedProvider...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = EconomicTracker(
            signature="test-agent",
            data_path=Path(tmpdir),
            initial_balance=100.0,
        )

        class FakeUsage:
            prompt_tokens = 1000
            completion_tokens = 500

        class FakeResponse:
            usage = FakeUsage()

        class FakeProvider:
            def chat(self, messages, tools=None, **kwargs):
                return FakeResponse()

        provider = TrackedProvider(provider=FakeProvider(), tracker=tracker)
        response = provider.chat(messages=[{"role": "user", "content": "hi"}])

        # Token cost: (1000/1M * 2.5) + (500/1M * 10) = 0.0025 + 0.005 = 0.0075
        assert tracker.balance < 100.0, "Balance should have decreased"
        assert abs(tracker.balance - (100.0 - 0.0075)) < 0.0001

        # Proxy attribute access
        assert provider.tracker is tracker

        print("✓ TrackedProvider tests passed")


def test_data_directory():
    """Test that livebench/data/ directory exists for data storage."""
    print("Testing data directory...")

    data_dir = Path(__file__).parent.parent / "livebench" / "data"
    assert data_dir.exists(), "livebench/data/ directory should exist"

    print("✓ Data directory exists")


def test_package_exports():
    """Test that clawmode_integration exports the expected symbols."""
    print("Testing package exports...")

    from clawmode_integration import (
        ClawWorkAgentLoop,
        ClawWorkState,
        create_agent_loop_with_tracking,
        TaskClassifier,
        TrackedProvider,
        create_clawwork_tools,
    )

    assert ClawWorkAgentLoop is not None
    assert ClawWorkState is not None
    assert create_agent_loop_with_tracking is not None
    assert TaskClassifier is not None
    assert TrackedProvider is not None
    assert create_clawwork_tools is not None

    print("✓ Package exports tests passed")


def main():
    """Run all tests."""
    print("=" * 50)
    print("ClawWork Component Tests")
    print("=" * 50)
    print()
    
    try:
        test_economic_tracker()
        test_memory_store()
        test_work_evaluator()
        test_occupation_data()
        test_skill_file()
        test_clawwork_tools()
        test_tracked_provider()
        test_data_directory()
        test_package_exports()
        
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
