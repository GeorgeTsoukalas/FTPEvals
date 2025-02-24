import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
from omegaconf import OmegaConf

from main import BatchProofEvaluator, ProofResult
from utils.logging_utils import Logger
from llm.model_caller import LLMCaller

@pytest.fixture
def mock_logger():
    return Logger("test")

@pytest.fixture
def mock_model_caller():
    caller = MagicMock(spec=LLMCaller)
    async def mock_call_model(*args, **kwargs):
        # Return different proofs based on theorem name
        theorem_name = kwargs.get("conversation_id", "")
        if "test_theorem1" in theorem_name:
            proof = "exact Nat.add_comm a b"
        elif "test_theorem2" in theorem_name:
            proof = "apply Nat.mul_pos\nexact h\nexact h"
        else:
            proof = "by\n  simp\n  exact rfl"
        
        return MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=proof
                    )
                )
            ]
        )
    caller.call_model = mock_call_model
    return caller

@pytest.fixture
def test_config():
    return OmegaConf.create({
        "model": {
            "name": "test-model",
            "provider": "test",
            "temperature": 0.7,
            "max_tokens": 2048
        }
    })

@pytest.fixture
def evaluator(mock_model_caller, mock_logger):
    return BatchProofEvaluator(
        model_caller=mock_model_caller,
        batch_size=2,
        project_root="data/putnambench/lean4",
        logger=mock_logger,
        max_parallel_envs=2,
        max_proof_depth=10
    )

@pytest.mark.asyncio
async def test_proof_generation(evaluator, test_config):
    """Test that proof generation works correctly."""
    # Test theorem1
    proof1, success1 = await evaluator.generate_proof(
        theorem_name="test_theorem1",
        prompt_template="Prove this theorem: {theorem}",
        model_config=test_config.model
    )
    
    assert success1
    assert "exact Nat.add_comm a b" in proof1
    
    # Test theorem2
    proof2, success2 = await evaluator.generate_proof(
        theorem_name="test_theorem2",
        prompt_template="Prove this theorem: {theorem}",
        model_config=test_config.model
    )
    
    assert success2
    assert "apply Nat.mul_pos" in proof2
    assert "exact h" in proof2

@pytest.mark.asyncio
async def test_batch_evaluation(evaluator, test_config):
    """Test that batch evaluation works correctly."""
    # Create test problem files
    problem_files = [
        "data/putnambench/lean4/solutions_replaced_new/test_theorem1.lean",
        "data/putnambench/lean4/solutions_replaced_new/test_theorem2.lean"
    ]
    
    # Mock the ProofEnvPool and ProofEnvActor
    with patch("main.ProofEnvPool") as mock_pool, \
         patch("main.ProofEnvActor") as mock_actor:
        
        # Configure mock pool to simulate successful proof verification
        mock_pool.return_value.__enter__.return_value = mock_pool.return_value
        mock_pool.return_value.step.return_value = [
            (None, None, None, 1.0, True, MagicMock(error_message=None))
        ]
        
        # Run batch evaluation
        results = await evaluator.evaluate_batch(
            problem_files=problem_files,
            prompt_template="Prove this theorem: {theorem}",
            model_config=test_config.model
        )
        
        print("\n=== Batch Evaluation Results ===")
        # Verify results
        assert len(results) == 2
        for result in results:
            print(f"\nTheorem: {result.theorem_name}")
            print(f"Success: {result.success}")
            print(f"Error Message: {result.error_message}")
            print(f"Proof:\n{result.proof}")
            print("=" * 50)
            
            assert isinstance(result, ProofResult)
            assert result.success
            assert result.proof is not None
            assert result.error_message is None
            
            # Verify specific proofs
            if result.theorem_name == "test_theorem1":
                assert "exact Nat.add_comm a b" in result.proof
            elif result.theorem_name == "test_theorem2":
                assert "apply Nat.mul_pos" in result.proof
                assert "exact h" in result.proof

@pytest.mark.asyncio
async def test_failed_proof_generation(evaluator, test_config):
    """Test handling of failed proof generation."""
    # Mock model caller to simulate failure
    evaluator.model_caller.call_model = MagicMock(side_effect=Exception("Model error"))
    
    proof, success = await evaluator.generate_proof(
        theorem_name="test_theorem1",
        prompt_template="Prove this theorem: {theorem}",
        model_config=test_config.model
    )
    
    assert not success
    assert proof == ""

@pytest.mark.asyncio
async def test_failed_proof_verification(evaluator, test_config):
    """Test handling of failed proof verification."""
    problem_files = ["data/putnambench/lean4/solutions_replaced_new/test_theorem1.lean"]
    
    # Mock the ProofEnvPool to simulate verification failure
    with patch("main.ProofEnvPool") as mock_pool, \
         patch("main.ProofEnvActor") as mock_actor:
        
        mock_pool.return_value.__enter__.return_value = mock_pool.return_value
        mock_pool.return_value.step.return_value = [
            (None, None, None, 0.0, False, MagicMock(error_message="Tactic failed"))
        ]
        
        results = await evaluator.evaluate_batch(
            problem_files=problem_files,
            prompt_template="Prove this theorem: {theorem}",
            model_config=test_config.model
        )
        
        assert len(results) == 1
        assert not results[0].success
        assert results[0].error_message == "Tactic failed"

@pytest.mark.asyncio
async def test_real_problem_attempt(evaluator, test_config):
    """Test attempting a real problem from the dataset."""
    # Use our created test files
    problem_files = [
        "data/putnambench/lean4/solutions_replaced_new/test_theorem1.lean",
        "data/putnambench/lean4/solutions_replaced_new/test_theorem2.lean"
    ]
    
    if not all(Path(f).exists() for f in problem_files):
        pytest.skip("Test files not found")
    
    # Test with the first problem
    results = await evaluator.evaluate_batch(
        problem_files=[problem_files[0]],
        prompt_template="Prove this theorem: {theorem}",
        model_config=test_config.model
    )
    
    assert len(results) == 1
    assert isinstance(results[0], ProofResult)
    assert hasattr(results[0], 'theorem_name')
    assert hasattr(results[0], 'success')
    assert hasattr(results[0], 'time_taken')
    assert hasattr(results[0], 'proof')
    assert hasattr(results[0], 'error_message') 