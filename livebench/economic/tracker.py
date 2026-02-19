"""
Economic Tracker - Tracks token costs and agent balance.

Handles:
- Token cost calculation (input/output tokens)
- Balance tracking and persistence
- Cost per message tracking
- Survival status calculation
"""

import json
import jsonlines
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any


class EconomicTracker:
    """Tracks economic activity for an agent."""
    
    def __init__(
        self,
        signature: str,
        data_path: Path,
        initial_balance: float = 1000.0,
        input_price_per_million: float = 2.5,
        output_price_per_million: float = 10.0,
    ):
        """
        Initialize economic tracker.
        
        Args:
            signature: Agent identifier
            data_path: Root directory for agent data
            initial_balance: Starting balance in dollars
            input_price_per_million: Cost per 1M input tokens
            output_price_per_million: Cost per 1M output tokens
        """
        self.signature = signature
        self.data_path = Path(data_path) / signature
        self.economic_path = self.data_path / "economic"
        self.economic_path.mkdir(parents=True, exist_ok=True)
        
        # Pricing
        self.input_price = input_price_per_million
        self.output_price = output_price_per_million
        
        # Balance tracking
        self.balance_file = self.economic_path / "balance.jsonl"
        self.costs_file = self.economic_path / "token_costs.jsonl"
        
        # Load or initialize balance
        self.balance = self._load_balance(initial_balance)
        self.initial_balance = initial_balance
        
        # Current task tracking
        self.current_task_cost = 0.0
        self.current_task_id = None
        
    def _load_balance(self, default: float) -> float:
        """Load the most recent balance from file."""
        if not self.balance_file.exists():
            return default
            
        try:
            with jsonlines.open(self.balance_file) as reader:
                entries = list(reader)
                if entries:
                    return float(entries[-1]["balance"])
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
            
        return default
    
    def _save_balance_entry(self):
        """Append current balance to balance.jsonl."""
        entry = {
            "date": date.today().isoformat(),
            "balance": round(self.balance, 2),
            "timestamp": datetime.now().isoformat(),
        }
        
        with jsonlines.open(self.balance_file, mode="a") as writer:
            writer.write(entry)
    
    def track_tokens(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost and update balance.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in dollars
        """
        input_cost = (input_tokens / 1_000_000) * self.input_price
        output_cost = (output_tokens / 1_000_000) * self.output_price
        total_cost = input_cost + output_cost
        
        self.balance -= total_cost
        self.current_task_cost += total_cost
        
        return total_cost
    
    def start_task(self, task_id: Optional[str] = None):
        """Start tracking a new task."""
        self.current_task_id = task_id or f"task_{datetime.now().timestamp()}"
        self.current_task_cost = 0.0
    
    def end_task(self, metadata: Optional[Dict[str, Any]] = None):
        """
        End current task and save cost entry.
        
        Args:
            metadata: Additional metadata to include in the cost entry
        """
        if self.current_task_id is None:
            return
            
        entry = {
            "task_id": self.current_task_id,
            "timestamp": datetime.now().isoformat(),
            "cost": round(self.current_task_cost, 4),
            "balance": round(self.balance, 2),
            **(metadata or {}),
        }
        
        with jsonlines.open(self.costs_file, mode="a") as writer:
            writer.write(entry)
        
        # Update daily balance
        self._save_balance_entry()
        
        # Reset task tracking
        self.current_task_id = None
        self.current_task_cost = 0.0
    
    def add_payment(self, amount: float, reason: str = "work_payment"):
        """
        Add payment to balance.
        
        Args:
            amount: Payment amount in dollars
            reason: Reason for payment
        """
        self.balance += amount
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "amount": round(amount, 2),
            "reason": reason,
            "balance": round(self.balance, 2),
        }
        
        with jsonlines.open(self.economic_path / "payments.jsonl", mode="a") as writer:
            writer.write(entry)
        
        self._save_balance_entry()
    
    def get_survival_status(self) -> str:
        """
        Calculate survival status based on current balance.
        
        Returns:
            Status string: "thriving", "stable", "struggling", "critical", "depleted"
        """
        if self.balance <= 0:
            return "depleted"
        elif self.balance < self.initial_balance * 0.1:
            return "critical"
        elif self.balance < self.initial_balance * 0.3:
            return "struggling"
        elif self.balance < self.initial_balance * 0.7:
            return "stable"
        else:
            return "thriving"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current economic status.
        
        Returns:
            Status dictionary with balance, survival status, etc.
        """
        return {
            "balance": round(self.balance, 2),
            "initial_balance": self.initial_balance,
            "survival_status": self.get_survival_status(),
            "input_price_per_million": self.input_price,
            "output_price_per_million": self.output_price,
        }
