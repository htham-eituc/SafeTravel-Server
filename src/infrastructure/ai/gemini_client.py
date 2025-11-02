import google.generativeai as genai
import json
from typing import Dict, Any, Optional
from src.config.settings import get_settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class GeminiClient:
    """Base Gemini AI client - handles all Gemini API interactions."""
    
    def __init__(self):
        settings = get_settings()
        
        # Configure API key from environment
        genai.configure(api_key=settings.gemini_api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        self.chat = None
        logger.info("GeminiClient initialized successfully")
    
    def _start_chat(self, system_context: str = ""):
        """Start a chat session with optional system context"""
        self.chat = self.model.start_chat(history=[])
        if system_context:
            self.chat.send_message(system_context)
        logger.debug(f"Chat session started{' with system context' if system_context else ''}")
        return self.chat
    
    async def generate_json(
        self, 
        prompt: str, 
        system_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response from Gemini.
        
        Args:
            prompt: The prompt to send to Gemini
            system_context: Optional system instruction for the AI
            
        Returns:
            Parsed JSON response as dictionary
        """
        try:
            if not self.chat and system_context:
                self._start_chat(system_context)
            elif not self.chat:
                self._start_chat()
            
            logger.debug(f"Sending prompt to Gemini: {prompt[:100]}...")
            
            # Send message
            response = await self.chat.send_message_async(prompt)
            
            # Clean and parse JSON
            text = response.text.strip()
            logger.debug(f"Received response: {text[:200]}...")
            
            # Remove markdown code blocks if present
            text = text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(text)
            logger.info("Gemini JSON response parsed successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini: {str(e)}")
            logger.error(f"Response text: {response.text}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}", exc_info=True)
            raise
    
    async def generate_text(self, prompt: str) -> str:
        """Generate plain text response (for non-JSON cases)"""
        try:
            if not self.chat:
                self._start_chat()
            
            logger.debug(f"Sending text prompt: {prompt[:100]}...")
            response = await self.chat.send_message_async(prompt)
            
            logger.info("Gemini text response received")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}", exc_info=True)
            raise
