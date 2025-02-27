import hydra
from omegaconf import DictConfig, OmegaConf
import os
import time
import logging
import asyncio
import ray
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

from utils.config_manager import get_config
from llm.model_caller import LLMCaller
from utils.logging_utils import Logger
from utils.checkpoint_manager import CheckpointManager

from itp_interface.rl.proof_action import ProofAction
from itp_interface.rl.simple_proof_env import ProofEnv, ProofEnvActor, ProofEnvInfo, ProofEnvReRankStrategy
from itp_interface.tools.lean4_sync_executor import get_all_theorems_in_file
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
    theorem_match_pattern = re.compile(r"^\s*(theorem\s+[\s|\S]+?:=\s*sorry)", re.MULTILINE)
    proof_extraction_pattern = re.compile(r"\[PROOF\]([\s|\S]+)\[END PROOF\]", re.MULTILINE)
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
        theorem_content: str,
        system_prompt: Optional[str] = None
    ) -> Tuple[str, bool]:
        """Generate a proof using the model."""
        try:
            # Add system_prompt to kwargs if provided
            kwargs = {}
            if system_prompt is not None:
                kwargs["system_prompt"] = system_prompt
            
            response = await self.model_caller.call_model(
                conversation_id=theorem_name,
                provider=model_config.provider,
                prompt=prompt_template.format(theorem=theorem_content),
                model=model_config.name,
                temperature=model_config.temperature if hasattr(model_config, "temperature") else None,
                max_tokens=model_config.max_tokens if hasattr(model_config, "max_tokens") else None,
                **kwargs
            )
            
            # Extract proof text based on provider
            if model_config.provider == "openai":
                proof = response.choices[0].message.content
            elif model_config.provider == "anthropic":
                proof = response.content[0].text
            elif model_config.provider == "gemini":
                proof = response.text
            else:
                raise ValueError(f"Unsupported provider: {model_config.provider}")
            
            # Log the generated proof
            self.logger.info(f"\n{'='*50}\nGenerated proof for {theorem_name}:\n{proof}\n{'='*50}")
            
            return proof, True
        except Exception as e:
            self.logger.exception(f"Error generating proof for {theorem_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return "", False
    
    async def evaluate_batch(
        self,
        problem_files: List[str],
        prompt_template: str,
        model_config: DictConfig,
        system_prompt: Optional[str] = None
    ) -> List[ProofResult]:
        """Evaluate a batch of problems."""
        results = []
        
        # Create proof executors for each problem
        env_actors = []
        # Read theorems from files
        theorem_contents_per_file = {}
        for file_path in problem_files:
            theorems = get_all_theorems_in_file(file_path)
            # Assuming run only for putnam bench
            assert len(theorems) == 1, f"Expected exactly 1 theorem in file {file_path}"
            theorem_name = theorems[0].theorem_name
            # Read the theorem content from the file
            with open(file_path, 'r') as f:
                file_content = f.read()
                
            # Extract imports and open statements
            import_lines = []
            open_lines = []
            for line in file_content.split('\n'):
                if line.strip().startswith('import '):
                    import_lines.append(line)
                elif line.strip().startswith('open '):
                    open_lines.append(line)
            
            # Extract only the theorem statement
            theorem_statements = BatchProofEvaluator.theorem_match_pattern.findall(file_content)
            assert len(theorem_statements) == 1, f"Expected exactly 1 theorem statement in file {file_path}"
            theorem_statement : str = theorem_statements[0]
            theorem_statement = theorem_statement.replace(theorem_name, "problem")            
            # Combine imports, open statements, and theorem content
            combined_content = []
            if import_lines:
                combined_content.extend(import_lines)
            if open_lines:
                combined_content.extend(open_lines)
            if combined_content:
                combined_content.append("")  # Add a blank line for readability
            combined_content.append(theorem_statement)  # Add the theorem statement
            
            theorem_content = '\n'.join(combined_content)
            self.logger.info(f"\n{'='*50}\nTheorem content for {theorem_name} with imports and open statements:\n{theorem_content}\n{'='*50}")
            theorem_details = theorem_contents_per_file.get(file_path, {})
            theorem_details[theorem_name] = {"name": theorem_name, "content": theorem_content}
            theorem_contents_per_file[file_path] = theorem_details
                
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
            theorem_details_list = []
            # Generate proofs for all problems in parallel
            proof_tasks = []
            for file_path in problem_files:
                # theorem_name = self._get_theorem_name(str(file_path))
                # Pass the theorem content and system prompt
                theorem_details = theorem_contents_per_file[file_path]
                theorem_content = theorem_details[theorem_name]["content"]
                theorem_name = theorem_details[theorem_name]["name"]
                theorem_details_list.append(theorem_details)
                # Note the name has been changed in content
                assert theorem_name not in theorem_content, f"Theorem name {theorem_name} should not be present in theorem content"
                task = self.generate_proof(theorem_name, prompt_template, model_config, theorem_content, system_prompt)
                proof_tasks.append(task)
            
            proofs = await asyncio.gather(*proof_tasks)
            extracted_proofs = []
            extracted_env_ids = []
            extracted_theorem_names = []
            for i, (proof, generation_success) in enumerate(proofs):
                start_time = time.time()
                theorem_name = theorem_details_list[i][theorem_name]["name"]
                if not generation_success:
                    results.append(ProofResult(
                        theorem_name=theorem_name,
                        success=False,
                        time_taken=time.time() - start_time,
                        error_message="Failed to generate proof"
                    ))
                    continue
                    
                # Extract proof from between [PROOF] and [END PROOF] delimiters if present
                extracted_proof = BatchProofEvaluator.proof_extraction_pattern.findall(proof)
                if len(extracted_proof) == 1:
                    extracted_proof: str = extracted_proof[0].strip()
                    if extracted_proof.startswith(":="):
                        # If the proof starts with ":=", remove it
                        extracted_proof = extracted_proof[len(":="):].strip()
                    if extracted_proof.startswith("by "): # Note 'by' is not sufficient because there are tactics like 'by_cases'
                        # If the proof starts with "by", remove it
                        extracted_proof = extracted_proof[len("by"):].strip()
                    extracted_proofs.append(ProofAction(
                        ProofAction.ActionType.RUN_TACTIC, 
                        ProofAction.Language.LEAN4, 
                        tactics=[extracted_proof])) # TODO fix to execute not beyond the proof completion or first failure
                    extracted_env_ids.append(i)
                    extracted_theorem_names.append(theorem_name)
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

            with pool:
                # Parallely verify proofs using the pool
                try:                   
                    step_results = pool.step(extracted_proofs, extracted_env_ids)
                    for thm_idx, (_, _, _, _, done, info) in enumerate(step_results):
                        # Handle the case where info might be None
                        success = done
                        error_message = None
                        if info is None:
                            success = False
                            error_message = "Proof verification failed: Lean server error or timeout"
                            self.logger.error(f"Received None info object during proof verification for {theorem_name}")                            
                        if info.error_message:
                            success = False
                            error_message = info.error_message
                        
                        theorem_name = extracted_theorem_names[thm_idx]
                        results.append(ProofResult(
                            theorem_name=theorem_name,
                            success=success,
                            time_taken=time.time() - start_time,
                            proof=extracted_proof if success else None,
                            error_message=error_message))
                except Exception as e:
                    # Catch any unexpected errors during the evaluation of this problem
                    error_message = f"Unexpected error during evaluation: {str(e)}"
                    self.logger.exception(f"Error evaluating {theorem_name}: {error_message}")
                    
                    # Add a failed result for this problem
                    results.append(ProofResult(
                        theorem_name=theorem_name,
                        success=False,
                        time_taken=time.time() - start_time,
                        error_message=error_message))        
        except Exception as e:
            # Catch any unexpected errors during the batch evaluation
            self.logger.exception(f"Unexpected error during batch evaluation: {str(e)}")
            # For any problems that haven't been processed yet, add failed results
            processed_theorems = [result.theorem_name for result in results]
            for file_path in problem_files:
                theorem_name = self._get_theorem_name(str(file_path))
                if theorem_name not in processed_theorems:
                    results.append(ProofResult(
                        theorem_name=theorem_name,
                        success=False,
                        time_taken=0.0,
                        error_message=f"Evaluation skipped due to batch error: {str(e)}"
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
    
    # Log the system prompt if it exists
    if hasattr(cfg.prompts, "system_prompt"):
        logger.info(f"\n{'='*50}\nUsing system prompt from config:\n{cfg.prompts.system_prompt}\n{'='*50}")
    else:
        logger.info("No system prompt found in config")
    
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
    all_problems = [p for p in solutions_dir.glob("*.lean") if p.stem.startswith("putnam_")]
    
    # Define priority problems with their exact filenames
    priority_problems = [
        "putnam_1986_b1_sol.lean",
        "putnam_1988_b2_sol.lean", 
        "putnam_2008_a1_sol.lean",
        "putnam_1988_b1_sol.lean", 
        "putnam_1977_a3_sol.lean",
        "putnam_2001_a1_sol.lean",
        "putnam_1986_a1_sol.lean",
        "putnam_1990_a1_sol.lean"
    ]
    
    # Print all available problems for debugging
    all_problem_names = [p.name for p in all_problems]
    logger.info(f"All available problems: {all_problem_names}")
    
    # Reorder problems to prioritize the specified ones
    problems = []
    
    # First add the priority problems in the specified order if they exist
    for problem_name in priority_problems:
        matching_problems = [p for p in all_problems if p.name == problem_name]
        if matching_problems:
            problems.extend(matching_problems)
            # Remove from all_problems to avoid duplicates
            all_problems = [p for p in all_problems if p.name != problem_name]
        else:
            logger.warning(f"Priority problem {problem_name} not found in dataset")
    
    # Then add the remaining problems
    problems.extend(all_problems)
    
    logger.info(f"Found problems: {[p.name for p in problems]}")
    total_problems = len(problems)
    
    logger.info(f"Found {total_problems} problems in {solutions_dir}")
    logger.info(f"Priority problems found: {[p.name for p in problems if p.name in priority_problems]}")
    
    # Initialize or load checkpoint
    if not checkpoint_manager.current_checkpoint:
        checkpoint_manager.initialize_run(
            config=OmegaConf.to_container(cfg, resolve=True),
            total_problems=total_problems
        )
    else:
        logger.info(f"Using existing checkpoint: {checkpoint_manager.current_checkpoint}")
        # Update total_problems in the checkpoint if needed
        if checkpoint_manager.state["metadata"]["total_problems"] != total_problems:
            logger.warning(f"Checkpoint has {checkpoint_manager.state['metadata']['total_problems']} problems, but current dataset has {total_problems} problems")
            checkpoint_manager.state["metadata"]["total_problems"] = total_problems
    
    # Get IDs of completed problems
    completed_problem_ids = checkpoint_manager.state["completed_problems"]
    
    # Filter out the problems that have already been completed
    # This ensures we maintain the priority order
    remaining_problems = [problems[i] for i in range(len(problems)) if i not in completed_problem_ids]
    
    logger.info(f"Remaining problems to evaluate: {len(remaining_problems)}")
    logger.info(f"First few problems to evaluate: {[p.name for p in remaining_problems[:5]]}")

    error_retry_count = 0
    max_error_retries = 10
    backoff_time = 10  # seconds
    exp_backoff = 1.25  # exponential backoff factor
    
    # Process problems in batches
    for i in range(0, len(remaining_problems), cfg.evaluation.batch_size):
        batch_problems = remaining_problems[i:i + cfg.evaluation.batch_size]
        
        while error_retry_count < max_error_retries:
            try:
                # Evaluate batch
                results = await evaluator.evaluate_batch(
                    problem_files=batch_problems,
                    prompt_template=cfg.prompts.template,
                    model_config=cfg.model,
                    system_prompt=cfg.prompts.system_prompt if hasattr(cfg.prompts, "system_prompt") else None
                )
                error_retry_count = 0  # Reset error retry count
                backoff_time = 10  # Reset backoff time
                break
            except Exception as e:
                logger.exception(f"Unhandled exception occurred while evaluating batch: {e}")
                error_retry_count += 1
                logger.info(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                backoff_time *= exp_backoff

        
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
    
    # Check if a specific checkpoint file is provided
    if hasattr(cfg, "checkpoint_file") and cfg.checkpoint_file:
        logger.info(f"Loading checkpoint from: {cfg.checkpoint_file}")
        # Load the specified checkpoint file
        with open(cfg.checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
            checkpoint_manager.current_checkpoint = cfg.checkpoint_file
            checkpoint_manager.state = checkpoint
            checkpoint_manager.state["completed_problems"] = set(checkpoint_manager.state["completed_problems"])
        logger.info(f"Loaded checkpoint with {len(checkpoint_manager.state['completed_problems'])} completed problems")
    
    # Run evaluation
    asyncio.run(evaluate_benchmark(cfg, logger, checkpoint_manager))

if __name__ == "__main__":
    main() 