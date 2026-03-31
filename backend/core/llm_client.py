import anthropic
from typing import Dict, List, Any, Optional
from core.config import settings
from core.logger import setup_logger

logger = setup_logger(__name__)


class LLMClient:
    """Wrapper around Anthropic Claude for agent reasoning."""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
        if self.provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                logger.warning("ANTHROPIC_API_KEY not set — LLM calls will use simulation mode")
                self.client = None
            else:
                self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            logger.warning(f"Unsupported LLM provider '{self.provider}' — using simulation mode")
            self.client = None
    
    @property
    def is_available(self) -> bool:
        return self.client is not None
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from the LLM."""
        if not self.is_available:
            return ""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=self.temperature,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return ""
    
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a JSON response from the LLM."""
        json_system = system_prompt + "\n\nYou MUST respond with valid JSON only. No markdown, no explanation, just JSON."
        return await self.generate(json_system, user_prompt, max_tokens)


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
