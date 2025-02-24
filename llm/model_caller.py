import os
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from anthropic import Anthropic
import google.generativeai as genai
from utils.logging_utils import Logger
from omegaconf import DictConfig

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
    def __init__(self, model_config: Optional[DictConfig] = None, secrets_dir: str = "secrets"):
        self.logger = Logger("LLMCaller")
        # Get the directory containing this file
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to project root
        project_root = os.path.dirname(current_file_dir)
        # Use project root for secrets directory
        self.secrets_dir = os.path.join(project_root, secrets_dir)
        self.model_config = model_config
        
        # Initialize API keys from secrets directory
        self._init_api_keys()
        
        # Initialize clients
        self._init_clients()
        
        # Initialize conversations
        self.conversations: Dict[str, Conversation] = {}
    
    def _init_api_keys(self):
        """Initialize API keys from secrets directory based on provider"""
        # Define required keys and their file names
        key_files = {
            "openai": "openai.key",
            "anthropic": "anthropic.key",
            "google": "gemini.key"
        }
        
        # If no model config is provided, we need all keys
        required_providers = ["openai"] if self.model_config and self.model_config.provider else key_files.keys()
        
        # Read only the required keys
        for provider in required_providers:
            try:
                with open(os.path.join(self.secrets_dir, key_files[provider])) as f:
                    setattr(self, f"{provider}_key", f.read().strip())
            except FileNotFoundError as e:
                missing_file = str(e).split("'")[1]
                self.logger.error(f"API key file not found: {missing_file}")
                self.logger.info(f"Please add your {provider} API key to: {key_files[provider]}")
                raise ValueError(f"Missing API key file for {provider}: {missing_file}")
    
    def _init_clients(self):
        """Initialize API clients based on provider"""
        if not hasattr(self, "openai_key") and not hasattr(self, "anthropic_key") and not hasattr(self, "google_key"):
            return
            
        # We don't need to initialize OpenAI client here as we create it in the call_openai method
        if hasattr(self, "anthropic_key"):
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)
        if hasattr(self, "google_key"):
            genai.configure(api_key=self.google_key)
    
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
            from openai import AsyncOpenAI
            
            # Create client instance
            client = AsyncOpenAI(api_key=self.openai_key)
            
            conv = self.get_or_create_conversation(conversation_id)
            conv.add_message("user", prompt)
            
            messages = [{"role": msg.role, "content": msg.content} for msg in conv.get_messages()]
            response = await client.chat.completions.create(
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
            "gemini": self.call_gemini
        }
        
        if provider not in provider_map:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Log the prompt
        self.logger.info(f"\n{'='*50}\nPrompt for {conversation_id} using {provider}:\n{prompt}\n{'='*50}")
        
        # Call the model
        response = await provider_map[provider](conversation_id, prompt, **kwargs)
        
        # Log the response
        if provider == "openai":
            response_text = response.choices[0].message.content
        elif provider == "anthropic":
            response_text = response.content[0].text
        elif provider == "gemini":
            response_text = response.text
        else:
            response_text = "Response format unknown"
            
        self.logger.info(f"\n{'='*50}\nResponse for {conversation_id} using {provider}:\n{response_text}\n{'='*50}")
        
        return response