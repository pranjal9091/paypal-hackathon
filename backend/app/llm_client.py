import json
import logging
from typing import Optional, Dict, Any
import httpx
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger(__name__)

class LLMResult(BaseModel):
    content: str
    provider: str
    mode: str # "live" or "fallback"
    model: str
    is_fallback: bool
    error_detail: Optional[str] = None

class LLMClient:
    """
    Robust Server-Side LLM Client with Honest Fallbacks.
    - Connects to Google Gemini or OpenAI REST APIs when credentials exist.
    - Enforces timeouts (15s default) and bounded retries.
    - Handles rate limits, timeouts, schema parse failures.
    - Never exposes secret API keys.
    - Explicitly labels fallback output; never misrepresents fallback as live AI.
    """

    def __init__(self):
        self.api_key = settings.llm_api_key.strip()
        self.provider = settings.llm_provider.strip().lower()
        self.model = settings.llm_model.strip()
        self.timeout = settings.llm_timeout_seconds

    @property
    def is_live_configured(self) -> bool:
        return settings.has_real_llm_credentials

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        fallback_content: str = "",
        force_fallback: bool = False
    ) -> LLMResult:
        if force_fallback or not self.is_live_configured:
            return LLMResult(
                content=fallback_content,
                provider="deterministic-fallback",
                mode="fallback",
                model="local-rule-engine-v1",
                is_fallback=True,
                error_detail="Live LLM credentials not configured or fallback forced"
            )

        # Attempt Live Provider Call with Bounded Retries
        last_error = None
        for attempt in range(2):
            try:
                if self.provider == "gemini":
                    content = await self._call_gemini(prompt, system_instruction)
                    return LLMResult(
                        content=content,
                        provider="gemini",
                        mode="live",
                        model=self.model,
                        is_fallback=False
                    )
                elif self.provider in ["openai", "openai-compatible"]:
                    content = await self._call_openai(prompt, system_instruction)
                    return LLMResult(
                        content=content,
                        provider="openai",
                        mode="live",
                        model=self.model,
                        is_fallback=False
                    )
                else:
                    return LLMResult(
                        content=fallback_content,
                        provider="deterministic-fallback",
                        mode="fallback",
                        model="local-rule-engine-v1",
                        is_fallback=True,
                        error_detail=f"Unknown LLM provider '{self.provider}'"
                    )
            except Exception as e:
                last_error = str(e)
                logger.warning(f"LLM call attempt {attempt + 1} failed: {last_error}")

        # If all attempts failed, return clearly labeled fallback
        return LLMResult(
            content=fallback_content,
            provider="deterministic-fallback",
            mode="fallback",
            model="local-rule-engine-v1",
            is_fallback=True,
            error_detail=f"Live LLM call failed after retries: {last_error}"
        )

    async def _call_gemini(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {system_instruction}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will strictly follow these instructions."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048,
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=body)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned status {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError) as err:
                raise RuntimeError(f"Unexpected Gemini response structure: {str(err)}")

    async def _call_openai(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=body)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI API returned status {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError) as err:
                raise RuntimeError(f"Unexpected OpenAI response structure: {str(err)}")

llm_client = LLMClient()
