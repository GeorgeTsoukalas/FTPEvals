import hydra
from omegaconf import DictConfig, OmegaConf
import os
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from utils.config_manager import get_config
from llm.model_caller import LLMCaller
from utils.logging_utils import Logger
from utils.checkpoint_manager import CheckpointManager

from itp_interface.rl.proof_action import ProofAction
from itp_interface.rl.simple_proof_env import ProofEnv, ProofEnvReRankStrategy
from itp_interface.tools.proof_exec_callback import ProofExecutorCallback
from itp_interface.tools.lean4_sync_executor import get_all_theorems_in_file, get_fully_qualified_theorem_name

@dataclass
class ProofResult:
    theorem_name: str
    success: bool
    time_taken: float
    error_message: Optional[str] = None
    proof: Optional[str] = None

async def evaluate_proof(
    model_caller: LLMCaller,
    conversation_id: str,
    theorem: str,
    prompt_template: str,
    model_config: DictConfig,
    logger: Logger
) -> Tuple[str, bool]:
    """Generate a proof using the model and return the proof and success status."""
    try:
        prompt = prompt_template.format(theorem=theorem)
        response = await model_caller.call_model(
            conversation_id=conversation_id,
            provider=model_config.provider,
            prompt=prompt,
            model=model_config.name,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens
        )
        
        # Extract the proof from the response
        proof = response.choices[0].message.content
        return proof, True
    except Exception as e:
        logger.error(f"Error generating proof: {e}")
        return "", False

def verify_proof(
    proof: str,
    theorem_name: str,
    project_dir: str,
    file_path: str,
    logger: Logger
) -> bool:
    """Verify a proof using the Lean 4 proof environment."""
    try:
        # Initialize proof environment
        proof_exec_callback = ProofExecutorCallback(
            project_folder=project_dir,
            file_path=file_path,
            language=ProofAction.Language.LEAN4,
            always_use_retrieval=False,
            keep_local_context=True
        )
        
        env = ProofEnv(
            "test",
            proof_exec_callback,
            theorem_name,
            retrieval_strategy=ProofEnvReRankStrategy.NO_RE_RANK,
            max_proof_depth=10,
            always_retrieve_thms=False,
            logger=logger
        )
        
        # Execute the proof line by line
        with env:
            for line in proof.split('\n'):
                if not line.strip():
                    continue
                    
                action = ProofAction(
                    ProofAction.ActionType.RUN_TACTIC,
                    ProofAction.Language.LEAN4,
                    tactics=[line]
                )
                
                _, _, _, _, done, info = env.step(action)
                if done:
                    return True
                
                if info.error_message:
                    logger.error(f"Proof error: {info.error_message}")
                    return False
        
        return False
    except Exception as e:
        logger.error(f"Error verifying proof: {e}")
        return False

async def evaluate_benchmark(
    cfg: DictConfig,
    logger: Logger,
    checkpoint_manager: CheckpointManager
) -> None:
    """Evaluate the model on a benchmark dataset."""
    
    # Initialize model caller
    model_caller = LLMCaller()
    
    # Get list of problems from benchmark
    benchmark_dir = Path(cfg.evaluation.dataset.path)
    problems = list(benchmark_dir.glob("*.lean"))
    total_problems = len(problems)
    
    logger.info(f"Found {total_problems} problems in {benchmark_dir}")
    
    # Initialize or load checkpoint
    checkpoint_manager.initialize_run(
        config=OmegaConf.to_container(cfg, resolve=True),
        total_problems=total_problems
    )
    
    # Get remaining problems
    remaining_problems = checkpoint_manager.get_remaining_problems()
    logger.info(f"Remaining problems to evaluate: {len(remaining_problems)}")
    
    for problem_id in remaining_problems:
        problem_path = problems[int(problem_id)]
        theorem_name = problem_path.stem
        
        start_time = time.time()
        
        # Generate proof
        proof, generation_success = await evaluate_proof(
            model_caller=model_caller,
            conversation_id=theorem_name,
            theorem=problem_path.read_text(),
            prompt_template=cfg.prompts.template,
            model_config=cfg.model,
            logger=logger
        )
        
        if not generation_success:
            result = ProofResult(
                theorem_name=theorem_name,
                success=False,
                time_taken=time.time() - start_time,
                error_message="Failed to generate proof"
            )
        else:
            # Verify proof
            verification_success = verify_proof(
                proof=proof,
                theorem_name=theorem_name,
                project_dir=str(benchmark_dir.parent),
                file_path=str(problem_path),
                logger=logger
            )
            
            result = ProofResult(
                theorem_name=theorem_name,
                success=verification_success,
                time_taken=time.time() - start_time,
                proof=proof if verification_success else None,
                error_message=None if verification_success else "Proof verification failed"
            )
        
        # Save result
        checkpoint_manager.save_result(
            problem_id=problem_id,
            result=result.__dict__
        )
        
        logger.info(f"Completed {theorem_name}: {'Success' if result.success else 'Failed'}")
    
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