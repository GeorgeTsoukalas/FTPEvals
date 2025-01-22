import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from utils.logging_utils import Logger

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.logger = Logger("CheckpointManager")
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Initialize checkpoint state
        self.current_checkpoint: Optional[str] = None
        self.state: Dict[str, Any] = {
            "completed_problems": set(),
            "results": [],
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
        if problem_id in self.state["completed_problems"]:
            self.logger.warning(f"Problem {problem_id} already completed, skipping")
            return
        
        self.state["completed_problems"].add(problem_id)
        self.state["results"].append({
            "problem_id": problem_id,
            "timestamp": datetime.now().isoformat(),
            **result
        })
        self.state["metadata"]["completed_count"] = len(self.state["completed_problems"])
        self.state["metadata"]["last_updated"] = datetime.now().isoformat()
        
        self._save_checkpoint()
    
    def load_latest_checkpoint(self, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
        self.state["completed_problems"] = set(self.state["completed_problems"])
        
        return self.state
    
    def get_remaining_problems(self) -> set:
        """Get the set of problems that still need to be evaluated"""
        all_problems = set(str(i) for i in range(self.state["metadata"]["total_problems"]))
        return all_problems - self.state["completed_problems"]
    
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
        """Export results to CSV and JSON formats"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a timestamp for the export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"results_{self.state['config']['model']['name']}_{timestamp}"
        
        # Export to JSON (complete state)
        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, 'w') as f:
            json.dump(self.state, f, indent=2)
        
        # Export to CSV (just the results)
        df = pd.DataFrame(self.state["results"])
        csv_path = os.path.join(output_dir, f"{base_name}.csv")
        df.to_csv(csv_path, index=False)
        
        self.logger.info(f"Exported results to {json_path} and {csv_path}")
    
    def _save_checkpoint(self):
        """Save the current state to a checkpoint file"""
        if not self.current_checkpoint:
            raise ValueError("No active checkpoint")
        
        # Convert set to list for JSON serialization
        state_copy = self.state.copy()
        state_copy["completed_problems"] = list(self.state["completed_problems"])
        
        with open(self.current_checkpoint, 'w') as f:
            json.dump(state_copy, f, indent=2)
        
        self.logger.debug(f"Saved checkpoint to {self.current_checkpoint}") 