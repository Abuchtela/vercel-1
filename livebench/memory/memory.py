"""
Memory Store - Persistent memory for agent learning.

Stores learning entries, insights, and patterns discovered by the agent.
"""

import jsonlines
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class MemoryStore:
    """Manages persistent memory for an agent."""
    
    def __init__(self, signature: str, data_path: Path):
        """
        Initialize memory store.
        
        Args:
            signature: Agent identifier
            data_path: Root directory for agent data
        """
        self.signature = signature
        self.data_path = Path(data_path) / signature
        self.memory_path = self.data_path / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.memory_path / "memory.jsonl"
    
    def add_entry(
        self,
        content: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a memory entry.
        
        Args:
            content: Memory content
            category: Memory category (e.g., "learning", "insight", "pattern")
            metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "category": category,
            **(metadata or {}),
        }
        
        with jsonlines.open(self.memory_file, mode="a") as writer:
            writer.write(entry)
        
        return entry
    
    def get_entries(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memory entries.
        
        Args:
            category: Filter by category (optional)
            limit: Maximum number of entries to return (optional)
            
        Returns:
            List of memory entries
        """
        if not self.memory_file.exists():
            return []
        
        with jsonlines.open(self.memory_file) as reader:
            entries = list(reader)
        
        # Filter by category if specified
        if category:
            entries = [e for e in entries if e.get("category") == category]
        
        # Apply limit if specified
        if limit:
            entries = entries[-limit:]
        
        return entries
    
    def search_entries(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memory entries by content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching memory entries
        """
        if not self.memory_file.exists():
            return []
        
        with jsonlines.open(self.memory_file) as reader:
            entries = list(reader)
        
        # Simple substring search (case-insensitive)
        query_lower = query.lower()
        matches = [
            e for e in entries
            if query_lower in e.get("content", "").lower()
        ]
        
        return matches[-limit:] if limit else matches
