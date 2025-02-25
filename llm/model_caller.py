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
            "gemini": "gemini.key"
        }
        
        # If no model config is provided, we need all keys
        required_providers = [self.model_config.provider] if self.model_config and self.model_config.provider else key_files.keys()
        
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
        if not hasattr(self, "openai_key") and not hasattr(self, "anthropic_key") and not hasattr(self, "gemini_key"):
            return
            
        # We don't need to initialize OpenAI client here as we create it in the call_openai method
        if hasattr(self, "anthropic_key"):
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)
        if hasattr(self, "gemini_key"):
            genai.configure(api_key=self.gemini_key)
    
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
        system_prompt: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,
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
            
            # Add system message if provided
            if system_prompt is not None:
                self.logger.info(f"\n{'='*50}\nUsing SYSTEM PROMPT for {conversation_id} with OpenAI:\n{system_prompt}\n{'='*50}")
                # Insert system message at the beginning
                messages.insert(0, {"role": "system", "content": system_prompt})
            
            # Prepare API parameters
            api_params = {
                "model": model,
                "messages": messages,
                **kwargs
            }
            
            # Handle o3 models specially
            is_o3_model = "o3" in model.lower()
            
            # Add temperature only for non-o3 models and if it's not None
            if not is_o3_model and temperature is not None:
                api_params["temperature"] = temperature
                self.logger.info(f"Using temperature: {temperature} for model {model}")
            else:
                self.logger.info(f"Skipping temperature parameter for model {model}")
            
            # Handle token limits based on model type
            if is_o3_model:
                if max_completion_tokens is not None:
                    self.logger.info(f"Using max_completion_tokens: {max_completion_tokens} for model {model}")
                    api_params["max_completion_tokens"] = max_completion_tokens
                elif max_tokens is not None:
                    self.logger.info(f"Converting max_tokens to max_completion_tokens: {max_tokens} for model {model}")
                    api_params["max_completion_tokens"] = max_tokens
            else:
                # For other OpenAI models, use max_tokens
                if max_tokens is not None:
                    self.logger.info(f"Using max_tokens: {max_tokens} for model {model}")
                    api_params["max_tokens"] = max_tokens
            
            response = await client.chat.completions.create(**api_params)
            
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
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call Anthropic API with conversation history"""
        try:
            conv = self.get_or_create_conversation(conversation_id)
            conv.add_message("user", prompt)
            
            messages = [{"role": msg.role, "content": msg.content} for msg in conv.get_messages()]
            
            # Add system parameter if provided
            if system_prompt is not None:
                self.logger.info(f"\n{'='*50}\nUsing SYSTEM PROMPT for {conversation_id} with Anthropic:\n{system_prompt}\n{'='*50}")
                # Anthropic uses a separate system parameter
                kwargs["system"] = system_prompt
            
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
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: int = 40,
        response_mime_type: str = "text/plain",
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call Google's Gemini API with conversation history"""
        try:
            # Log API key status for debugging
            self.logger.info(f"Checking Gemini API key status...")
            if not hasattr(self, "gemini_key"):
                self.logger.error("No Gemini API found in instance attributes")
                raise ValueError("Gemini API key not loaded. Please check your gemini.key file.")
            
            # Ensure API is configured
            genai.configure(api_key=self.gemini_key)
            self.logger.info(f"Gemini API configured with key: {self.gemini_key[:4]}...{self.gemini_key[-4:]}")
            
            conv = self.get_or_create_conversation(conversation_id)
            
            # Add the user message to conversation
            conv.add_message("user", prompt)
            
            # Create generation config with all parameters
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "response_mime_type": response_mime_type,
                **kwargs
            }
            
            # Add max_tokens if provided (called max_output_tokens in Gemini)
            if max_tokens is not None:
                generation_config["max_output_tokens"] = max_tokens
            
            self.logger.info(f"Creating Gemini model with name: {model}")
            # Create the model with the generation config
            model_instance = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )
            
            # Prepare history with system prompt if provided
            history = []
            
            # Log system prompt if provided
            if system_prompt is not None:
                self.logger.info(f"\n{'='*50}\nUsing SYSTEM PROMPT for {conversation_id} with Gemini:\n{system_prompt}\n{'='*50}")
                
                # For Gemini, we combine the system prompt with the user's prompt
                # This ensures they're processed together rather than as separate exchanges
                combined_prompt = f"{system_prompt}\n\n{prompt}"
                
                # Use the combined prompt for the API call
                for msg in conv.get_messages():
                    if msg.role == "user" and msg.content == prompt:
                        # Replace the last user message with the combined prompt
                        history.append({"role": "user", "parts": [combined_prompt]})
                    else:
                        history.append({"role": msg.role, "parts": [msg.content]})
            else:
                # Use regular conversation history
                for msg in conv.get_messages():
                    history.append({"role": msg.role, "parts": [msg.content]})
            
            # Start chat with history
            self.logger.info(f"Starting chat with history length: {len(history)}")
            chat = model_instance.start_chat(history=history[:-1])  # Exclude the last message
            
            # Send the last message (which is either the original prompt or the combined prompt)
            self.logger.info(f"Sending message to Gemini API...")
            last_message = history[-1]["parts"][0]
            response = await chat.send_message_async(last_message)
            
            conv.add_message("assistant", response.text)
            self.logger.info(f"Successfully called Gemini API with model {model}")
            return response
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
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
        
        # Check if system_prompt is provided in kwargs or model_config
        system_prompt = kwargs.get("system_prompt")
        if system_prompt is None and hasattr(self, "model_config") and hasattr(self.model_config, "system_prompt"):
            system_prompt = self.model_config.system_prompt
            kwargs["system_prompt"] = system_prompt
        
        # Handle token limits and other parameters based on provider and model
        if provider == "openai":
            model_name = kwargs.get("model", "")
            if not model_name and hasattr(self, "model_config") and hasattr(self.model_config, "name"):
                model_name = self.model_config.name
                
            # For o3 models, use max_completion_tokens and remove temperature
            if "o3" in model_name.lower() and hasattr(self, "model_config"):
                # Remove temperature for o3 models
                if "temperature" in kwargs:
                    self.logger.info(f"Removing temperature parameter for o3 model: {model_name}")
                    kwargs.pop("temperature")
                
                # Handle token limits
                if hasattr(self.model_config, "max_completion_tokens"):
                    kwargs["max_completion_tokens"] = self.model_config.max_completion_tokens
                    self.logger.info(f"Using max_completion_tokens: {self.model_config.max_completion_tokens} from model config")
                elif hasattr(self.model_config, "max_tokens"):
                    kwargs["max_completion_tokens"] = self.model_config.max_tokens
                    self.logger.info(f"Converting max_tokens to max_completion_tokens: {self.model_config.max_tokens} from model config")
            # For other OpenAI models, use max_tokens
            elif hasattr(self, "model_config") and hasattr(self.model_config, "max_tokens"):
                kwargs["max_tokens"] = self.model_config.max_tokens
                self.logger.info(f"Using max_tokens: {self.model_config.max_tokens} from model config")
        
        # Remove None values from kwargs to avoid API errors
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        # Log system prompt if it exists
        if system_prompt is not None:
            self.logger.info(f"\n{'='*50}\nSYSTEM PROMPT for {conversation_id} using {provider}:\n{system_prompt}\n{'='*50}")
        
        # For Gemini, log the entire prompt to verify it's correctly formatted
        if provider == "gemini":
            self.logger.info(f"\n{'='*50}\nFULL PROMPT sent to {provider} for {conversation_id}:\n{prompt}\n{'='*50}")
        else:
            # For other providers, just log the theorem part for brevity
            theorem_content = ""
            if "Here is the theorem to prove:" in prompt:
                theorem_start = prompt.find("Here is the theorem to prove:")
                theorem_end = prompt.find("IMPORTANT:", theorem_start)
                if theorem_end > theorem_start:
                    theorem_content = prompt[theorem_start:theorem_end].strip()
                else:
                    # If we can't find the end marker, just take a reasonable chunk
                    theorem_content = prompt[theorem_start:theorem_start+500].strip() + "..."
            
            self.logger.info(f"\n{'='*50}\nProcessing theorem for {conversation_id} using {provider}:\n{theorem_content}\n{'='*50}")
        
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
            
        # Log a shorter version of the response if it's very long
        if len(response_text) > 1000:
            log_response = response_text[:500] + "\n...\n" + response_text[-500:]
            self.logger.info(f"\n{'='*50}\nResponse for {conversation_id} using {provider} (truncated):\n{log_response}\n{'='*50}")
        else:
            self.logger.info(f"\n{'='*50}\nResponse for {conversation_id} using {provider}:\n{response_text}\n{'='*50}")
        
        return response