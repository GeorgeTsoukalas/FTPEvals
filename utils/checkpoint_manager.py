import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from utils.logging_utils import Logger

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = "checkpoints", max_attempts: int = 1):
        self.logger = Logger("CheckpointManager")
        self.checkpoint_dir = checkpoint_dir
        self.max_attempts = max_attempts
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Initialize checkpoint state
        self.current_checkpoint: Optional[str] = None
        self.state: Dict[str, Any] = {
            "completed_problems": {},
            "results": [],
            "max_attempts": self.max_attempts,
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "last_updated": None,
                "total_problems": 0,
                "completed_count": 0
            }
        }
    
    def initialize_run(self, config: Dict[str, Any], total_problems: int):
        """Initialize a new evaluation run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_checkpoint = os.path.join(
            self.checkpoint_dir,
            f"checkpoint_{config['model']['name']}_{timestamp}.json"
        )
        
        self.state["config"] = config
        self.state["metadata"]["total_problems"] = total_problems
        self._save_checkpoint()
    
    def save_result(self, problem_id: str, result: Dict[str, Any]):
        """Save a single problem result"""
        problem_attempts = self.state["completed_problems"].get(problem_id, 0)
        if problem_attempts >= self.max_attempts:
            self.logger.warning(f"Problem {problem_id} already completed, skipping")
            return
        
        self.state["completed_problems"][problem_id] = problem_attempts + 1
        self.state["results"].append({
            "problem_id": problem_id,
            "attempts": problem_attempts + 1,
            "timestamp": datetime.now().isoformat(),
            **result
        })
        self.state["metadata"]["completed_count"] = len(self.state["completed_problems"])
        self.state["metadata"]["last_updated"] = datetime.now().isoformat()
        
        self._save_checkpoint()
    
    def load_latest_checkpoint(self, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    # ^ This is unused function
        """Load the latest checkpoint for a given model"""
        checkpoints = []
        for filename in os.listdir(self.checkpoint_dir):
            if not filename.endswith(".json"):
                continue
            if model_name and model_name not in filename:
                continue
            
            filepath = os.path.join(self.checkpoint_dir, filename)
            with open(filepath, 'r') as f:
                checkpoint = json.load(f)
                checkpoints.append((filepath, checkpoint))
        
        if not checkpoints:
            return None
        
        # Sort by last_updated timestamp and get the most recent
        latest = max(checkpoints, key=lambda x: x[1]["metadata"]["last_updated"])
        self.current_checkpoint = latest[0]
        self.state = latest[1]
        # self.state["completed_problems"] = set(self.state["completed_problems"])
        
        return self.state
    
    def get_remaining_problems(self) -> set:
        """Get the set of problems that still need to be evaluated"""
        # We don't generate indices anymore, we use the actual problem IDs from the state
        return set(range(self.state["metadata"]["total_problems"])) - self.state["completed_problems"]
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of the evaluation progress"""
        return {
            "total_problems": self.state["metadata"]["total_problems"],
            "completed_problems": len(self.state["completed_problems"]),
            "remaining_problems": self.state["metadata"]["total_problems"] - len(self.state["completed_problems"]),
            "start_time": self.state["metadata"]["start_time"],
            "last_updated": self.state["metadata"]["last_updated"]
        }
    
    def export_results(self, output_dir: str = "results"):
        """Export results to a JSON file and CSV summary"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert set to list for JSON serialization
        export_state = self.state.copy()
        export_state["completed_problems"] = list(export_state["completed_problems"].keys())
        
        # Save full results as JSON
        results_file = os.path.join(output_dir, "results.json")
        with open(results_file, "w") as f:
            json.dump(export_state, f, indent=2)
        
        # Create summary DataFrame
        df = pd.DataFrame(self.state["results"])
        if not df.empty:
            summary_file = os.path.join(output_dir, "summary.csv")
            df.to_csv(summary_file, index=False)
    
    def _save_checkpoint(self):
        """Save current state to checkpoint file"""
        if not self.current_checkpoint:
            return
            
        # Convert set to list for JSON serialization
        checkpoint_state = self.state.copy()
        # checkpoint_state["completed_problems"] = list(checkpoint_state["completed_problems"])
        
        self.state["metadata"]["last_updated"] = datetime.now().isoformat()
        self.state["metadata"]["completed_count"] = len(self.state["completed_problems"])
        
        self.logger.info(f"Saved checkpoint to {self.current_checkpoint}")
        with open(self.current_checkpoint, "w") as f:
            json.dump(checkpoint_state, f, indent=2) 