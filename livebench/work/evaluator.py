"""
Work Evaluator - Evaluates agent work submissions using LLM.

Provides quality scoring and payment calculation for completed tasks.
"""

import os
import json
import jsonlines
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import litellm


class WorkEvaluator:
    """Evaluates work submissions and determines payment."""
    
    def __init__(
        self,
        signature: str,
        data_path: Path,
        meta_prompts_dir: Optional[Path] = None,
        use_strict_eval: bool = True,
    ):
        """
        Initialize work evaluator.
        
        Args:
            signature: Agent identifier
            data_path: Root directory for agent data
            meta_prompts_dir: Directory containing evaluation prompts
            use_strict_eval: If True, use LLM evaluation; if False, allow fallback
        """
        self.signature = signature
        self.data_path = Path(data_path) / signature
        self.work_path = self.data_path / "work"
        self.work_path.mkdir(parents=True, exist_ok=True)
        
        self.meta_prompts_dir = meta_prompts_dir
        self.use_strict_eval = use_strict_eval
        self.evaluations_file = self.work_path / "evaluations.jsonl"
        
        # Check for evaluation credentials
        self.eval_api_key = os.getenv("EVALUATION_API_KEY")
        self.eval_api_base = os.getenv("EVALUATION_API_BASE")
        self.eval_model = os.getenv("EVALUATION_MODEL", "openai/gpt-4o")
        
    def evaluate_work(
        self,
        task: Dict[str, Any],
        submission: str,
        work_artifact: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a work submission.
        
        Args:
            task: Task definition dictionary
            submission: Agent's submission text
            work_artifact: Optional path to work artifact file
            
        Returns:
            Evaluation result with quality_score (0-1) and feedback
        """
        task_id = task.get("task_id", "unknown")
        instruction = task.get("instruction", "")
        max_payment = task.get("max_payment", 0.0)
        
        # Use LLM evaluation if configured
        if self.eval_api_key and self.use_strict_eval:
            try:
                quality_score, feedback = self._llm_evaluate(
                    instruction=instruction,
                    submission=submission,
                )
            except Exception as e:
                print(f"⚠️  LLM evaluation failed: {e}")
                if self.use_strict_eval:
                    quality_score = 0.0
                    feedback = f"Evaluation failed: {str(e)}"
                else:
                    # Fallback to simple heuristic
                    quality_score = self._heuristic_evaluate(submission)
                    feedback = "Used heuristic evaluation (LLM unavailable)"
        else:
            # Heuristic evaluation
            quality_score = self._heuristic_evaluate(submission)
            feedback = "Used heuristic evaluation (no LLM configured)"
        
        payment = quality_score * max_payment
        
        result = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "submission": submission[:500],  # Truncate for storage
            "quality_score": round(quality_score, 2),
            "max_payment": max_payment,
            "actual_payment": round(payment, 2),
            "feedback": feedback,
        }
        
        # Save evaluation
        with jsonlines.open(self.evaluations_file, mode="a") as writer:
            writer.write(result)
        
        # Save work artifact if provided
        if work_artifact:
            artifact_file = self.work_path / f"{task_id}.txt"
            artifact_file.write_text(work_artifact)
        
        return result
    
    def _llm_evaluate(self, instruction: str, submission: str) -> tuple[float, str]:
        """
        Use LLM to evaluate work quality.
        
        Args:
            instruction: Original task instruction
            submission: Agent's work submission
            
        Returns:
            (quality_score, feedback)
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(instruction, submission)
        
        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        
        response = litellm.completion(
            model=self.eval_model,
            messages=messages,
            api_key=self.eval_api_key,
            api_base=self.eval_api_base,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        quality_score = float(result.get("quality_score", 0.5))
        feedback = result.get("feedback", "No feedback provided")
        
        # Clamp score to [0, 1]
        quality_score = max(0.0, min(1.0, quality_score))
        
        return quality_score, feedback
    
    def _build_evaluation_prompt(self, instruction: str, submission: str) -> str:
        """Build evaluation prompt for LLM."""
        return f"""Evaluate the quality of this work submission.

TASK INSTRUCTION:
{instruction}

AGENT SUBMISSION:
{submission}

Evaluate the submission on:
1. **Completeness**: Does it address all aspects of the task?
2. **Quality**: Is the work well-done and professional?
3. **Accuracy**: Is the information correct and relevant?
4. **Effort**: Does it demonstrate appropriate effort?

Provide your evaluation as JSON:
{{
  "quality_score": <float between 0 and 1>,
  "feedback": "<brief explanation of the score>"
}}

A score of 1.0 means excellent work that fully meets or exceeds expectations.
A score of 0.5 means acceptable work with room for improvement.
A score of 0.0 means poor work that doesn't meet requirements.
"""
    
    def _heuristic_evaluate(self, submission: str) -> float:
        """
        Simple heuristic evaluation based on submission length and structure.
        
        Args:
            submission: Work submission text
            
        Returns:
            Quality score between 0 and 1
        """
        if not submission or len(submission.strip()) < 50:
            return 0.1
        
        # Basic quality indicators
        length = len(submission)
        has_structure = any(marker in submission for marker in ['\n\n', '##', '**', '-', '1.'])
        
        # Score based on length and structure
        if length > 1000 and has_structure:
            return 0.85
        elif length > 500:
            return 0.70
        elif length > 200:
            return 0.55
        else:
            return 0.40
    
    def get_evaluations(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent evaluations.
        
        Args:
            limit: Maximum number of evaluations to return
            
        Returns:
            List of evaluation dictionaries
        """
        if not self.evaluations_file.exists():
            return []
        
        with jsonlines.open(self.evaluations_file) as reader:
            evaluations = list(reader)
        
        if limit:
            evaluations = evaluations[-limit:]
        
        return evaluations


class LLMEvaluator:
    """
    Alias for WorkEvaluator for backwards compatibility.
    
    This class name is referenced in the documentation but is functionally
    identical to WorkEvaluator.
    """
    
    def __init__(self, *args, **kwargs):
        self._evaluator = WorkEvaluator(*args, **kwargs)
    
    def __getattr__(self, name):
        return getattr(self._evaluator, name)
