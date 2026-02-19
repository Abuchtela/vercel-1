"""
Task Classifier - Classifies tasks and estimates their value.

Uses LLM to classify free-form instructions into occupations with
hourly wage data, then estimates professional hours required.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import litellm
from thefuzz import fuzz


class TaskClassifier:
    """Classifies tasks and computes their economic value."""
    
    def __init__(
        self,
        provider: Any,
        occupation_data_path: Optional[Path] = None,
    ):
        """
        Initialize task classifier.
        
        Args:
            provider: LLM provider (can be TrackedProvider)
            occupation_data_path: Path to occupation wage mapping JSON
        """
        self.provider = provider
        
        # Load occupation data
        if occupation_data_path is None:
            # Default path relative to repo root
            repo_root = Path(__file__).parent.parent
            occupation_data_path = repo_root / "scripts" / "task_value_estimates" / "occupation_to_wage_mapping.json"
        
        self.occupations = self._load_occupations(occupation_data_path)
        
        # Fallback occupation
        self.fallback_occupation = {
            "title": "General and Operations Managers",
            "hourly_wage": 64.00,
        }
    
    def _load_occupations(self, path: Path) -> List[Dict[str, Any]]:
        """Load occupation wage data from JSON."""
        if not path.exists():
            print(f"⚠️  Occupation data not found at {path}, using fallback only")
            return []
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
                
            # Convert to list if it's a dict
            if isinstance(data, dict):
                occupations = [
                    {"title": title, **info}
                    for title, info in data.items()
                ]
            else:
                occupations = data
            
            print(f"✅ Loaded {len(occupations)} occupations from {path.name}")
            return occupations
            
        except Exception as e:
            print(f"⚠️  Failed to load occupations: {e}")
            return []
    
    def classify(self, instruction: str) -> Dict[str, Any]:
        """
        Classify a task instruction and estimate its value.
        
        Args:
            instruction: Free-form task instruction
            
        Returns:
            Dictionary with:
                - occupation: Matched occupation title
                - hourly_wage: Hourly wage for the occupation
                - estimated_hours: Estimated time in hours
                - max_payment: Total task value (hours * wage)
        """
        # Build classification prompt
        occupation_list = "\n".join([
            f"- {occ['title']}: ${occ.get('hourly_wage', 50):.2f}/hr"
            for occ in self.occupations[:40]  # Limit to avoid context overflow
        ])
        
        if not occupation_list:
            # Use fallback if no occupations loaded
            return {
                "occupation": self.fallback_occupation["title"],
                "hourly_wage": self.fallback_occupation["hourly_wage"],
                "estimated_hours": 2.0,
                "max_payment": self.fallback_occupation["hourly_wage"] * 2.0,
            }
        
        prompt = f"""Classify this task instruction into one of the provided occupations and estimate the professional hours required.

TASK INSTRUCTION:
{instruction}

AVAILABLE OCCUPATIONS:
{occupation_list}

Respond with JSON:
{{
  "occupation": "<exact occupation title from the list>",
  "estimated_hours": <float, professional time in hours>,
  "reasoning": "<brief explanation>"
}}

Be realistic about time estimates. Most tasks take 1-5 hours of professional work.
"""
        
        try:
            # Call LLM for classification
            messages = [{"role": "user", "content": prompt}]
            
            response = self.provider.chat(
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Extract classification
            occupation_title = result.get("occupation", "")
            estimated_hours = float(result.get("estimated_hours", 2.0))
            
            # Find matching occupation (fuzzy match)
            matched_occ = self._fuzzy_match_occupation(occupation_title)
            
            if matched_occ:
                hourly_wage = matched_occ.get("hourly_wage", 50.0)
                max_payment = hourly_wage * estimated_hours
                
                return {
                    "occupation": matched_occ["title"],
                    "hourly_wage": hourly_wage,
                    "estimated_hours": estimated_hours,
                    "max_payment": round(max_payment, 2),
                    "reasoning": result.get("reasoning", ""),
                }
        
        except Exception as e:
            print(f"⚠️  Classification failed: {e}")
        
        # Fallback to default occupation
        estimated_hours = 2.0
        return {
            "occupation": self.fallback_occupation["title"],
            "hourly_wage": self.fallback_occupation["hourly_wage"],
            "estimated_hours": estimated_hours,
            "max_payment": self.fallback_occupation["hourly_wage"] * estimated_hours,
            "reasoning": "Used fallback classification",
        }
    
    def _fuzzy_match_occupation(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Find occupation using fuzzy matching.
        
        Args:
            title: Occupation title to match
            
        Returns:
            Matched occupation dict or None
        """
        if not title or not self.occupations:
            return None
        
        title_lower = title.lower().strip()
        
        # Try exact match first
        for occ in self.occupations:
            if occ["title"].lower() == title_lower:
                return occ
        
        # Try substring match
        for occ in self.occupations:
            if title_lower in occ["title"].lower() or occ["title"].lower() in title_lower:
                return occ
        
        # Try fuzzy match
        best_match = None
        best_score = 0
        
        for occ in self.occupations:
            score = fuzz.ratio(title_lower, occ["title"].lower())
            if score > best_score:
                best_score = score
                best_match = occ
        
        # Accept if similarity is high enough
        if best_score >= 70:
            return best_match
        
        return None
