import hydra
from omegaconf import DictConfig, OmegaConf
import os
import time
import logging
import asyncio
import ray
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from utils.config_manager import get_config
from llm.model_caller import LLMCaller
from utils.logging_utils import Logger
from utils.checkpoint_manager import CheckpointManager

from itp_interface.rl.proof_action import ProofAction
from itp_interface.rl.simple_proof_env import ProofEnv, ProofEnvActor, ProofEnvInfo, ProofEnvReRankStrategy
from itp_interface.tools.proof_exec_callback import ProofExecutorCallback
from itp_interface.rl.simple_proof_env_pool import ProofEnvPool

@dataclass
class ProofResult:
    theorem_name: str
    success: bool
    time_taken: float
    error_message: Optional[str] = None
    proof: Optional[str] = None

class BatchProofEvaluator:
    def __init__(
        self,
        model_caller: LLMCaller,
        batch_size: int,
        project_root: str,
        logger: Logger,
        max_parallel_envs: int = 3,
        max_proof_depth: int = 10
    ):
        self.model_caller = model_caller
        self.batch_size = batch_size
        self.project_root = project_root
        self.logger = logger
        self.max_parallel_envs = max_parallel_envs
        self.max_proof_depth = max_proof_depth
        
        # Initialize Ray if not already initialized
        if not ray.is_initialized():
            ray.init()
    
    def _create_proof_executor(self, file_path: str) -> ProofExecutorCallback:
        """Create a ProofExecutorCallback for a given file."""
        # Make sure file_path is absolute or correctly relative to project_root
        if not os.path.isabs(file_path):
            # If file_path is not already in the solutions_replaced_new directory,
            # construct the full path correctly
            if "solutions_replaced_new" not in file_path:
                file_path = os.path.join(self.project_root, "solutions_replaced_new", os.path.basename(file_path))
            else:
                # If it already contains solutions_replaced_new, make sure it's absolute
                file_path = os.path.join(self.project_root, os.path.basename(file_path))
        
        return ProofExecutorCallback(
            project_folder=self.project_root,
            file_path=file_path,
            language=ProofAction.Language.LEAN4,
            always_use_retrieval=False,
            keep_local_context=True
        )
    
    def _get_theorem_name(self, file_path: str) -> str:
        """Extract theorem name from file path by removing _sol suffix."""
        stem = Path(file_path).stem
        return stem[:-4] if stem.endswith("_sol") else stem
    
    async def generate_proof(
        self,
        theorem_name: str,
        prompt_template: str,
        model_config: DictConfig,
        theorem_content: str
    ) -> Tuple[str, bool]:
        """Generate a proof using the model."""
        try:
            response = await self.model_caller.call_model(
                conversation_id=theorem_name,
                provider=model_config.provider,
                prompt=prompt_template.format(theorem=theorem_content),
                model=model_config.name,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens
            )
            
            proof = response.choices[0].message.content
            
            # Log the generated proof
            self.logger.info(f"\n{'='*50}\nGenerated proof for {theorem_name}:\n{proof}\n{'='*50}")
            
            return proof, True
        except Exception as e:
            self.logger.error(f"Error generating proof for {theorem_name}: {e}")
            return "", False
    
    async def evaluate_batch(
        self,
        problem_files: List[str],
        prompt_template: str,
        model_config: DictConfig
    ) -> List[ProofResult]:
        """Evaluate a batch of problems."""
        results = []
        
        # Create proof executors for each problem
        env_actors = []
        # Read theorems from files
        theorem_contents = {}
        for file_path in problem_files:
            theorem_name = self._get_theorem_name(str(file_path))
            # Read the theorem content from the file
            with open(file_path, 'r') as f:
                file_content = f.read()
                # Extract only the theorem statement
                theorem_lines = []
                in_theorem = False
                for line in file_content.split('\n'):
                    if 'theorem' in line and not in_theorem:
                        in_theorem = True
                        # Replace the actual theorem name with "theorem problem"
                        line = line.replace(f"theorem {theorem_name}", "theorem problem")
                        theorem_lines.append(line)
                    elif in_theorem and 'sorry' in line:
                        break
                    elif in_theorem:
                        theorem_lines.append(line)
                
                theorem_content = '\n'.join(theorem_lines)
                theorem_contents[theorem_name] = theorem_content
                
            proof_exec = self._create_proof_executor(str(file_path))  # Convert Path to string
            
            # Create ProofEnvActor for each problem
            env_actor = ProofEnvActor.remote(
                "test",
                proof_exec,
                theorem_name,
                retrieval_strategy=ProofEnvReRankStrategy.NO_RE_RANK,
                max_proof_depth=self.max_proof_depth,
                always_retrieve_thms=False,
                logger=self.logger
            )
            env_actors.append(env_actor)
        
        # Create ProofEnvPool
        pool = ProofEnvPool(
            proof_env_actors=env_actors,
            logger=self.logger,
            max_parallel_envs=self.max_parallel_envs
        )
        
        try:
            with pool:
                # Generate proofs for all problems in parallel
                proof_tasks = []
                for file_path in problem_files:
                    theorem_name = self._get_theorem_name(str(file_path))
                    # Pass the theorem content instead of just the name
                    task = self.generate_proof(theorem_name, prompt_template, model_config, theorem_contents[theorem_name])
                    proof_tasks.append(task)
                
                proofs = await asyncio.gather(*proof_tasks)
                
                # Verify proofs using the pool
                for i, (proof, generation_success) in enumerate(proofs):
                    start_time = time.time()
                    theorem_name = self._get_theorem_name(str(problem_files[i]))
                    
                    if not generation_success:
                        results.append(ProofResult(
                            theorem_name=theorem_name,
                            success=False,
                            time_taken=time.time() - start_time,
                            error_message="Failed to generate proof"
                        ))
                        continue
                    
                    # Extract proof from between [PROOF] and [END PROOF] delimiters if present
                    extracted_proof = proof
                    if "[PROOF]" in proof and "[END PROOF]" in proof:
                        start_idx = proof.find("[PROOF]") + len("[PROOF]")
                        end_idx = proof.find("[END PROOF]")
                        if start_idx < end_idx:
                            extracted_proof = proof[start_idx:end_idx].strip()
                            
                            # Remove any theorem declaration line if present
                            lines = extracted_proof.split('\n')
                            if any(line.strip().startswith("theorem") for line in lines):
                                # Find the first line that doesn't start with "theorem" or isn't empty
                                start_line = 0
                                for idx, line in enumerate(lines):
                                    if line.strip().startswith("theorem"):
                                        start_line = idx + 1
                                        # If the line ends with ":= by", skip to the next line
                                        if ":= by" in line:
                                            start_line += 1
                                        break
                                
                                # Extract only the proof tactics
                                extracted_proof = '\n'.join(lines[start_line:])
                    else:
                        # Log an error if the model doesn't use the required delimiters
                        error_msg = f"Model response for {theorem_name} does not contain the required [PROOF] and [END PROOF] delimiters"
                        self.logger.error(error_msg)
                        results.append(ProofResult(
                            theorem_name=theorem_name,
                            success=False,
                            time_taken=time.time() - start_time,
                            error_message=error_msg
                        ))
                        continue
                    
                    # Create a single action with all tactics
                    action = ProofAction(
                        ProofAction.ActionType.RUN_TACTIC,
                        ProofAction.Language.LEAN4,
                        tactics=[extracted_proof]  # Pass the extracted proof as a single tactic
                    )
                    
                    # Execute action
                    success = True
                    error_message = None
                    
                    step_results = pool.step([action], [i])
                    for state, act, new_state, reward, done, info in step_results:
                        if info.error_message:
                            success = False
                            error_message = info.error_message
                        if done:
                            break
                    
                    results.append(ProofResult(
                        theorem_name=theorem_name,
                        success=success,
                        time_taken=time.time() - start_time,
                        proof=extracted_proof if success else None,
                        error_message=error_message
                    ))
        
        finally:
            # Cleanup
            for env_actor in env_actors:
                try:
                    ray.kill(env_actor)
                except (ValueError, AttributeError):
                    # Skip cleanup for mock objects in tests
                    pass
        
        return results

async def evaluate_benchmark(cfg: DictConfig, logger: Logger, checkpoint_manager: CheckpointManager) -> None:
    """Evaluate the model on a benchmark dataset using batched processing."""
    
    # Initialize model caller
    model_caller = LLMCaller(model_config=cfg.model)
    
    # Initialize evaluator
    project_root = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(project_root, cfg.evaluation.dataset.path)
    
    # The project root should be the parent directory of the dataset path
    # This is where the lakefile.lean would be located
    lean_project_root = os.path.dirname(dataset_path)
    
    logger.info(f"Python project root: {project_root}")
    logger.info(f"Dataset path: {dataset_path}")
    logger.info(f"Lean project root: {lean_project_root}")
    
    evaluator = BatchProofEvaluator(
        model_caller=model_caller,
        batch_size=cfg.evaluation.batch_size,
        project_root=lean_project_root,  # Use the correct Lean project root
        logger=logger,
        max_parallel_envs=cfg.evaluation.max_parallel_envs,
        max_proof_depth=cfg.evaluation.max_proof_depth
    )
    
    # Get list of problems from benchmark
    solutions_dir = Path(dataset_path)
    logger.info(f"Solutions directory: {solutions_dir}")
    logger.info(f"Solutions directory exists: {solutions_dir.exists()}")
    logger.info(f"Solutions directory is directory: {solutions_dir.is_dir()}")
    logger.info(f"Solutions directory absolute path: {solutions_dir.absolute()}")
    
    # Filter for only Putnam problems (exclude test files)
    problems = [p for p in solutions_dir.glob("*.lean") if p.stem.startswith("putnam_")]
    logger.info(f"Found problems: {[p.name for p in problems]}")
    total_problems = len(problems)
    
    logger.info(f"Found {total_problems} problems in {solutions_dir}")
    
    # Initialize or load checkpoint
    checkpoint_manager.initialize_run(
        config=OmegaConf.to_container(cfg, resolve=True),
        total_problems=total_problems
    )
    
    # Get remaining problems
    remaining_indices = checkpoint_manager.get_remaining_problems()
    remaining_problems = [problems[i] for i in remaining_indices]
    logger.info(f"Remaining problems to evaluate: {len(remaining_problems)}")
    
    # Process problems in batches
    for i in range(0, len(remaining_problems), cfg.evaluation.batch_size):
        batch_problems = remaining_problems[i:i + cfg.evaluation.batch_size]
        
        # Evaluate batch
        results = await evaluator.evaluate_batch(
            problem_files=batch_problems,
            prompt_template=cfg.prompts.template,
            model_config=cfg.model
        )
        
        # Save results
        for problem_idx, (problem_file, result) in enumerate(zip(batch_problems, results)):
            problem_id = problems.index(problem_file)  # Get the original index
            checkpoint_manager.save_result(problem_id, result.__dict__)
            
            status = 'Success' if result.success else 'Failed'
            log_msg = f"\n{'='*50}\nTheorem: {problem_file.name}\nStatus: {status}"
            if result.success and result.proof:
                log_msg += f"\nProof:\n{result.proof}"
            if not result.success and result.error_message:
                log_msg += f"\nError: {result.error_message}"
            log_msg += f"\nTime taken: {result.time_taken:.2f}s\n{'='*50}"
            logger.info(log_msg)
    
    # Export final results
    checkpoint_manager.export_results()

@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig) -> None:
    # Initialize logger
    logger = Logger(cfg.project.name)
    logger.info("Starting FTPEvals")
    logger.info(f"Configuration:\n{OmegaConf.to_yaml(cfg)}")
    
    # Initialize checkpoint manager
    checkpoint_manager = CheckpointManager()
    
    # Run evaluation
    asyncio.run(evaluate_benchmark(cfg, logger, checkpoint_manager))

if __name__ == "__main__":
    main() 