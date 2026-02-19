"""
ClawWork Agent Loop - Integrates economic tracking with nanobot.

Extends nanobot's AgentLoop to:
- Intercept /clawwork commands
- Track token costs for every message
- Append cost footers to responses
- Manage task lifecycle
"""

from typing import Dict, Any, Optional
import re
from datetime import datetime


class ClawWorkState:
    """Shared state for ClawWork integration."""
    
    def __init__(self, tracker, evaluator, memory, classifier):
        self.tracker = tracker
        self.evaluator = evaluator
        self.memory = memory
        self.classifier = classifier
        self.current_tasks = {}  # task_id -> task dict


class ClawWorkAgentLoop:
    """
    Agent loop with economic tracking.
    
    This would normally subclass nanobot's AgentLoop, but since we don't
    have nanobot installed yet, this is a standalone implementation showing
    the key integration points.
    """
    
    def __init__(
        self,
        base_loop: Any,
        state: ClawWorkState,
        tracked_provider: Any,
    ):
        """
        Initialize ClawWork agent loop.
        
        Args:
            base_loop: Base nanobot AgentLoop instance
            state: ClawWorkState with tracker, evaluator, etc.
            tracked_provider: TrackedProvider wrapping the LLM
        """
        self.base_loop = base_loop
        self.state = state
        self.tracked_provider = tracked_provider
        
    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process a message with economic tracking.
        
        Args:
            message: User message
            context: Optional context dict
            
        Returns:
            Agent response with cost footer
        """
        # Start task tracking
        task_id = f"msg_{datetime.now().timestamp()}"
        self.state.tracker.start_task(task_id)
        
        # Check for /clawwork command
        if message.strip().lower().startswith("/clawwork"):
            response = await self._handle_clawwork_command(message)
        else:
            # Regular message - pass to base loop
            response = await self.base_loop.process_message(message, context)
        
        # End task tracking
        self.state.tracker.end_task(metadata={
            "message_preview": message[:100],
        })
        
        # Append cost footer
        response_with_footer = self._append_cost_footer(response)
        
        return response_with_footer
    
    async def _handle_clawwork_command(self, message: str) -> str:
        """
        Handle /clawwork command to assign a paid task.
        
        Args:
            message: Message starting with /clawwork
            
        Returns:
            Response about task assignment
        """
        # Extract instruction after /clawwork
        match = re.match(r"/clawwork\s+(.+)", message, re.IGNORECASE)
        
        if not match:
            return "Usage: /clawwork <instruction>\n\nExample: /clawwork Write a market analysis for electric vehicles"
        
        instruction = match.group(1).strip()
        
        # Classify the task
        classification = self.state.classifier.classify(instruction)
        
        # Create task
        task_id = f"task_{datetime.now().timestamp()}"
        task = {
            "task_id": task_id,
            "instruction": instruction,
            "occupation": classification["occupation"],
            "hourly_wage": classification["hourly_wage"],
            "estimated_hours": classification["estimated_hours"],
            "max_payment": classification["max_payment"],
            "assigned_at": datetime.now().isoformat(),
        }
        
        # Store in current tasks
        self.state.current_tasks[task_id] = task
        
        # Build response with task context
        task_context = f"""
**New Paid Task Assigned: {task_id}**

**Instruction:** {instruction}

**Classification:**
- Occupation: {classification['occupation']}
- Hourly Wage: ${classification['hourly_wage']:.2f}/hr
- Estimated Time: {classification['estimated_hours']:.1f} hours
- Maximum Payment: ${classification['max_payment']:.2f}

**What to do:**
1. Work on this task using your available tools
2. When complete, use `submit_work` tool with:
   - task_id: {task_id}
   - submission: Description of what you accomplished
   - work_artifact: Optional path to output file

Your work will be evaluated for quality, and you'll receive payment proportional to the quality score (0-1.0 × max payment).

**Current Balance:** ${self.state.tracker.balance:.2f}
**Status:** {self.state.tracker.get_survival_status()}
"""
        
        # Let the agent process this
        response = await self.base_loop.process_message(task_context, context=None)
        
        return response
    
    def _append_cost_footer(self, response: str) -> str:
        """
        Append cost and balance information to response.
        
        Args:
            response: Original response
            
        Returns:
            Response with footer
        """
        cost = self.state.tracker.current_task_cost
        balance = self.state.tracker.balance
        status = self.state.tracker.get_survival_status()
        
        footer = f"\n\n---\n**Cost:** ${cost:.4f} | **Balance:** ${balance:.2f} | **Status:** {status}"
        
        return response + footer
    
    def __getattr__(self, name: str) -> Any:
        """Proxy other attributes to base loop."""
        return getattr(self.base_loop, name)


def create_agent_loop_with_tracking(
    base_loop: Any,
    state: ClawWorkState,
    tracked_provider: Any,
) -> ClawWorkAgentLoop:
    """
    Create a ClawWork agent loop wrapping a base nanobot loop.
    
    Args:
        base_loop: Base AgentLoop from nanobot
        state: ClawWorkState instance
        tracked_provider: TrackedProvider instance
        
    Returns:
        ClawWorkAgentLoop instance
    """
    return ClawWorkAgentLoop(
        base_loop=base_loop,
        state=state,
        tracked_provider=tracked_provider,
    )
