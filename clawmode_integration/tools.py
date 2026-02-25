"""
ClawWork Tools - Economic tools for agents.

Provides 4 tools:
- decide_activity: Choose between work, learn, idle based on economic state
- submit_work: Submit completed work for evaluation and payment
- learn: Store insights and patterns in long-term memory
- get_status: Check economic status and survival metrics
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from clawmode_integration.agent_loop import ClawWorkState


def create_clawwork_tools(state: Any) -> list:
    """
    Create ClawWork tool definitions for the agent.
    
    Args:
        state: ClawWorkState object with tracker, evaluator, memory, etc.
        
    Returns:
        List of tool definitions compatible with nanobot
    """
    
    def decide_activity_tool(context: str = "") -> Dict[str, Any]:
        """
        Decide what activity to pursue based on economic state.
        
        Use this tool to make strategic decisions about how to spend time:
        - Work on paid tasks when balance is low
        - Learn and improve skills when balance is comfortable
        - Idle/rest when not needed
        
        Args:
            context: Current situation or considerations
            
        Returns:
            Recommended activity and reasoning
        """
        status = state.tracker.get_status()
        balance = status["balance"]
        survival_status = status["survival_status"]
        
        # Decision logic based on survival status
        if survival_status in ["depleted", "critical"]:
            recommendation = "work"
            reasoning = f"Balance is {survival_status} (${balance:.2f}). Prioritize paid work immediately."
        elif survival_status == "struggling":
            recommendation = "work"
            reasoning = f"Balance is low (${balance:.2f}). Focus on paid tasks but consider quick learning opportunities."
        elif survival_status == "stable":
            recommendation = "balanced"
            reasoning = f"Balance is stable (${balance:.2f}). Mix paid work with skill development."
        else:  # thriving
            recommendation = "learn"
            reasoning = f"Balance is healthy (${balance:.2f}). Good time to invest in learning and exploration."
        
        return {
            "recommended_activity": recommendation,
            "reasoning": reasoning,
            "balance": balance,
            "survival_status": survival_status,
            "context_considered": context or "none provided",
        }
    
    def submit_work_tool(
        task_id: str,
        submission: str,
        work_artifact: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit completed work for evaluation and payment.
        
        Use this tool when you've finished a paid task to:
        1. Submit your work for quality evaluation
        2. Receive payment based on quality score
        3. Update your balance
        
        Args:
            task_id: ID of the task you're submitting for
            submission: Description of what you accomplished
            work_artifact: Optional path to work output file
            
        Returns:
            Evaluation result with quality score and payment
        """
        # Find the task
        task = state.current_tasks.get(task_id)
        
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found. Cannot submit work.",
            }
        
        # Evaluate the work
        evaluation = state.evaluator.evaluate_work(
            task=task,
            submission=submission,
            work_artifact=work_artifact,
        )
        
        # Add payment to balance
        payment = evaluation["actual_payment"]
        state.tracker.add_payment(payment, reason=f"work_payment_{task_id}")
        
        # Remove from current tasks
        del state.current_tasks[task_id]
        
        return {
            "success": True,
            "task_id": task_id,
            "quality_score": evaluation["quality_score"],
            "payment": payment,
            "max_payment": evaluation["max_payment"],
            "feedback": evaluation["feedback"],
            "new_balance": state.tracker.balance,
            "survival_status": state.tracker.get_survival_status(),
        }
    
    def learn_tool(
        insight: str,
        category: str = "general",
        confidence: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Store a learning insight in long-term memory.
        
        Use this tool to remember:
        - Patterns you've discovered
        - Lessons from successes and failures
        - Strategies that work well
        - Domain knowledge you've acquired
        
        Args:
            insight: The learning insight to store
            category: Category (e.g., "technical", "strategy", "domain_knowledge")
            confidence: Confidence in this insight (0-1)
            
        Returns:
            Confirmation of storage
        """
        entry = state.memory.add_entry(
            content=insight,
            category=category,
            metadata={"confidence": confidence},
        )
        
        return {
            "success": True,
            "message": "Insight stored in long-term memory",
            "category": category,
            "timestamp": entry["timestamp"],
        }
    
    def get_status_tool() -> Dict[str, Any]:
        """
        Check current economic status and survival metrics.
        
        Use this tool to understand:
        - Current balance
        - Survival status (thriving, stable, struggling, critical, depleted)
        - Recent economic activity
        - Active tasks
        
        Returns:
            Complete status report
        """
        status = state.tracker.get_status()
        
        # Get recent evaluations
        recent_evaluations = state.evaluator.get_evaluations(limit=5)
        
        # Get memory stats
        memory_entries = state.memory.get_entries()
        
        return {
            "balance": status["balance"],
            "initial_balance": status["initial_balance"],
            "survival_status": status["survival_status"],
            "token_pricing": {
                "input_per_million": status["input_price_per_million"],
                "output_per_million": status["output_price_per_million"],
            },
            "active_tasks": list(state.current_tasks.keys()),
            "recent_work_count": len(recent_evaluations),
            "total_memories": len(memory_entries),
            "average_quality": (
                sum(e["quality_score"] for e in recent_evaluations) / len(recent_evaluations)
                if recent_evaluations else None
            ),
        }
    
    # Return tool definitions
    return [
        {
            "name": "decide_activity",
            "description": "Decide what activity to pursue based on economic state and survival status",
            "function": decide_activity_tool,
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Current situation or considerations for the decision",
                    }
                },
            },
        },
        {
            "name": "submit_work",
            "description": "Submit completed work for a task to receive quality evaluation and payment",
            "function": submit_work_tool,
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task being submitted",
                    },
                    "submission": {
                        "type": "string",
                        "description": "Description of what you accomplished",
                    },
                    "work_artifact": {
                        "type": "string",
                        "description": "Optional path to work output file",
                    },
                },
                "required": ["task_id", "submission"],
            },
        },
        {
            "name": "learn",
            "description": "Store a learning insight or pattern in long-term memory",
            "function": learn_tool,
            "parameters": {
                "type": "object",
                "properties": {
                    "insight": {
                        "type": "string",
                        "description": "The learning insight to store",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category (technical, strategy, domain_knowledge, etc.)",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence in this insight (0-1)",
                    },
                },
                "required": ["insight"],
            },
        },
        {
            "name": "get_status",
            "description": "Check current economic status, survival metrics, and activity summary",
            "function": get_status_tool,
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    ]


# Aliases for backwards compatibility
decide_activity_tool = None  # Will be set by create_clawwork_tools
submit_work_tool = None
learn_tool = None
get_status_tool = None
