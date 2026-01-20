from typing import Optional, Dict, Any
from openai import OpenAI
from app.config import get_settings

settings = get_settings()


class LLMClient:
    """Unified client for interacting with LLM providers."""

    def __init__(self):
        self.openai_client = None

        if settings.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)

    async def generate(
        self,
        prompt: str,
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a response from the specified LLM provider."""

        if provider == "openai":
            return await self._generate_openai(
                prompt, model or "gpt-4o-mini", temperature, max_tokens, system_prompt
            )
        else:
            raise ValueError(f"Unknown provider: {provider}. Only 'openai' is supported.")

    async def _generate_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        system_prompt: Optional[str],
    ) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not configured. Set OPENAI_API_KEY.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = self.openai_client.chat.completions.create(**kwargs)

        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }


# Singleton instance
llm_client = LLMClient()
