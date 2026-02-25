"""
Tracked Provider - Wraps nanobot's LLM provider to track token costs.

Intercepts every LLM call and feeds token usage into the economic tracker.
"""

from typing import Any, Dict, List, Optional
from livebench.economic.tracker import EconomicTracker


class TrackedProvider:
    """
    Wraps an LLM provider to track token costs.
    
    This class acts as a transparent proxy that intercepts all LLM calls,
    extracts token usage information, and feeds it to the economic tracker.
    """
    
    def __init__(self, provider: Any, tracker: EconomicTracker):
        """
        Initialize tracked provider.
        
        Args:
            provider: The underlying LLM provider (from nanobot)
            tracker: Economic tracker instance
        """
        self._provider = provider
        self._tracker = tracker
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Any:
        """
        Make a chat completion call and track token usage.
        
        Args:
            messages: Chat messages
            tools: Optional tool definitions
            **kwargs: Additional arguments passed to provider
            
        Returns:
            Provider response
        """
        # Call the underlying provider
        response = self._provider.chat(messages=messages, tools=tools, **kwargs)
        
        # Extract token usage if available
        if hasattr(response, "usage") and response.usage:
            input_tokens = getattr(response.usage, "prompt_tokens", 0)
            output_tokens = getattr(response.usage, "completion_tokens", 0)
            
            # Track the cost
            cost = self._tracker.track_tokens(input_tokens, output_tokens)
            
            # Optionally attach cost info to response
            if hasattr(response, "__dict__"):
                response._tracked_cost = cost
        
        return response
    
    def __getattr__(self, name: str) -> Any:
        """
        Proxy all other attributes to the underlying provider.
        
        This allows the TrackedProvider to be a drop-in replacement
        for the original provider.
        """
        return getattr(self._provider, name)
    
    @property
    def tracker(self) -> EconomicTracker:
        """Access the underlying tracker."""
        return self._tracker
