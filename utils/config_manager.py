from dataclasses import dataclass
from typing import Any, Optional
import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig, OmegaConf

@dataclass
class ModelConfig:
    name: str
    provider: str
    temperature: float
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

@dataclass
class EvaluationConfig:
    name: str
    dataset: DictConfig
    metrics: list[str]
    max_attempts: int
    timeout: int

@dataclass
class ProjectConfig:
    name: str
    output_dir: str
    log_dir: str

@dataclass
class FTPEvalsConfig:
    project: ProjectConfig
    model: ModelConfig
    evaluation: EvaluationConfig
    seed: int
    debug: bool

cs = ConfigStore.instance()
cs.store(name="ftpevals_config", node=FTPEvalsConfig)

def register_configs():
    """Register configurations with Hydra"""
    cs.store(name="model/gpt4", node=ModelConfig)
    cs.store(name="model/claude3", node=ModelConfig)
    cs.store(name="model/gemini", node=ModelConfig)
    cs.store(name="evaluation/putnam", node=EvaluationConfig)
    cs.store(name="evaluation/minif2f", node=EvaluationConfig)

def get_config(config_path: str = "../configs", config_name: str = "config") -> DictConfig:
    """
    Get configuration using Hydra
    
    Args:
        config_path: Path to config directory
        config_name: Name of the main config file
    
    Returns:
        DictConfig: Configuration object
    """
    register_configs()
    
    @hydra.main(version_base=None, config_path=config_path, config_name=config_name)
    def _get_config(cfg: DictConfig) -> DictConfig:
        return cfg
    
    return _get_config() 