import os
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
import torch
import openai
from anthropic import Anthropic
import google.generativeai as genai
from vllm import LLM, SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
from utils.logging_utils import Logger

@dataclass
class Message:
    role: str
    content: str

class Conversation:
    def __init__(self):
        self.messages: List[Message] = []
    
    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
    
    def get_messages(self) -> List[Message]:
        return self.messages
    
    def clear(self):
        self.messages = []

class LLMCaller:
    def __init__(self, secrets_dir: str = "secrets", device_map: Optional[Dict[str, List[int]]] = None):
        self.logger = Logger("LLMCaller")
        self.secrets_dir = secrets_dir
        self.device_map = device_map or {"local": list(range(torch.cuda.device_count()))}
        
        # Initialize API keys from secrets directory
        self._init_api_keys()
        
        # Initialize clients
        self._init_clients()
        
        # Initialize local models
        self._init_local_models()
        
        # Initialize conversations
        self.conversations: Dict[str, Conversation] = {}
    
    def _init_api_keys(self):
        """Initialize API keys from secrets directory"""
        try:
            with open(os.path.join(self.secrets_dir, "openai.key")) as f:
                self.openai_key = f.read().strip()
            with open(os.path.join(self.secrets_dir, "anthropic.key")) as f:
                self.anthropic_key = f.read().strip()
            with open(os.path.join(self.secrets_dir, "google.key")) as f:
                self.google_key = f.read().strip()
        except FileNotFoundError as e:
            self.logger.error(f"API key file not found: {e}")
            raise
    
    def _init_clients(self):
        """Initialize API clients"""
        openai.api_key = self.openai_key
        self.anthropic_client = Anthropic(api_key=self.anthropic_key)
        genai.configure(api_key=self.google_key)
    
    def _init_local_models(self):
        """Initialize local models using vLLM"""
        self.local_models = {}
        model_configs = {
            "llama2-70b": {
                "model": "meta-llama/Llama-2-70b-chat-hf",
                "tensor_parallel_size": len(self.device_map["local"]),
            },
            "qwen-72b": {
                "model": "Qwen/Qwen-72B-Chat",
                "tensor_parallel_size": len(self.device_map["local"]),
            },
            "deepseek-67b": {
                "model": "deepseek-ai/deepseek-coder-33b-instruct",
                "tensor_parallel_size": len(self.device_map["local"]),
            }
        }
        
        for model_name, config in model_configs.items():
            try:
                engine_args = AsyncEngineArgs(
                    model=config["model"],
                    tensor_parallel_size=config["tensor_parallel_size"],
                    gpu_memory_utilization=0.85,
                    max_num_batched_tokens=4096,
                    trust_remote_code=True,
                )
                self.local_models[model_name] = LLM(engine_args=engine_args)
                self.logger.info(f"Successfully loaded local model: {model_name}")
            except Exception as e:
                self.logger.error(f"Failed to load local model {model_name}: {e}")
    
    def get_or_create_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation()
        return self.conversations[conversation_id]
    
    async def call_openai(
        self,
        conversation_id: str,
        prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call OpenAI API with conversation history"""
        try:
            conv = self.get_or_create_conversation(conversation_id)
            conv.add_message("user", prompt)
            
            messages = [{"role": msg.role, "content": msg.content} for msg in conv.get_messages()]
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            conv.add_message("assistant", response.choices[0].message.content)
            self.logger.info(f"Successfully called OpenAI API with model {model}")
            return response
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            raise

    async def call_anthropic(
        self,
        conversation_id: str,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call Anthropic API with conversation history"""
        try:
            conv = self.get_or_create_conversation(conversation_id)
            conv.add_message("user", prompt)
            
            messages = [{"role": msg.role, "content": msg.content} for msg in conv.get_messages()]
            response = await self.anthropic_client.messages.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            conv.add_message("assistant", response.content[0].text)
            self.logger.info(f"Successfully called Anthropic API with model {model}")
            return response
        except Exception as e:
            self.logger.error(f"Error calling Anthropic API: {e}")
            raise

    async def call_gemini(
        self,
        conversation_id: str,
        prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Call Google's Gemini API with conversation history"""
        try:
            conv = self.get_or_create_conversation(conversation_id)
            conv.add_message("user", prompt)
            
            model_instance = genai.GenerativeModel(model_name=model)
            chat = model_instance.start_chat(history=[
                {"role": msg.role, "parts": [msg.content]} for msg in conv.get_messages()
            ])
            
            response = await chat.send_message_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    **kwargs
                )
            )
            
            conv.add_message("assistant", response.text)
            self.logger.info(f"Successfully called Gemini API with model {model}")
            return response
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {e}")
            raise

    async def call_local_model(
        self,
        conversation_id: str,
        prompt: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call local model using vLLM"""
        try:
            if model_name not in self.local_models:
                raise ValueError(f"Local model {model_name} not found")
            
            conv = self.get_or_create_conversation(conversation_id)
            conv.add_message("user", prompt)
            
            # Format conversation history according to model's expected format
            formatted_prompt = self._format_conversation_for_model(model_name, conv.get_messages())
            
            sampling_params = SamplingParams(
                temperature=temperature,
                max_tokens=max_tokens or 2048,
                **kwargs
            )
            
            outputs = await self.local_models[model_name].generate(formatted_prompt, sampling_params)
            response_text = outputs[0].outputs[0].text
            
            conv.add_message("assistant", response_text)
            self.logger.info(f"Successfully called local model {model_name}")
            
            return {"model": model_name, "choices": [{"message": {"content": response_text}}]}
        except Exception as e:
            self.logger.error(f"Error calling local model {model_name}: {e}")
            raise

    def _format_conversation_for_model(self, model_name: str, messages: List[Message]) -> str:
        """Format conversation history according to model's expected format"""
        if model_name.startswith("llama"):
            return self._format_llama_conversation(messages)
        elif model_name.startswith("qwen"):
            return self._format_qwen_conversation(messages)
        elif model_name.startswith("deepseek"):
            return self._format_deepseek_conversation(messages)
        else:
            raise ValueError(f"Unknown model format: {model_name}")

    def _format_llama_conversation(self, messages: List[Message]) -> str:
        formatted = ""
        for msg in messages:
            if msg.role == "user":
                formatted += f"[INST] {msg.content} [/INST]"
            else:
                formatted += f"{msg.content}"
        return formatted

    def _format_qwen_conversation(self, messages: List[Message]) -> str:
        formatted = ""
        for msg in messages:
            if msg.role == "user":
                formatted += f"User: {msg.content}\n"
            else:
                formatted += f"Assistant: {msg.content}\n"
        return formatted

    def _format_deepseek_conversation(self, messages: List[Message]) -> str:
        formatted = ""
        for msg in messages:
            if msg.role == "user":
                formatted += f"### Instruction: {msg.content}\n"
            else:
                formatted += f"### Response: {msg.content}\n"
        return formatted

    async def call_model(
        self,
        conversation_id: str,
        provider: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generic method to call any supported model"""
        provider_map = {
            "openai": self.call_openai,
            "anthropic": self.call_anthropic,
            "gemini": self.call_gemini,
            "local": self.call_local_model
        }
        
        if provider not in provider_map:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return await provider_map[provider](conversation_id, prompt, **kwargs)