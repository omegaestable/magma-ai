"""
llm_client.py — Unified local LLM client for Ollama/OpenAI-compatible endpoints.

Handles retry logic, local endpoint calls, and response parsing.
Used for cheatsheet distillation and local LLM-based evaluation.
"""

import json
import time
import logging
import urllib.error
import urllib.request
from typing import Optional
from dataclasses import dataclass

from config import MODELS

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Parsed response from an LLM call."""
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    latency_s: float = 0.0


class LLMClient:
    """Client for calling a local Ollama/OpenAI-compatible endpoint."""

    def __init__(self, model_name: str = "ollama-qwen2.5-3b"):
        if model_name in MODELS:
            self.config = MODELS[model_name]
        else:
            raise ValueError(f"Unknown model: {model_name}. Available: {list(MODELS.keys())}")
        self.total_cost = 0.0
        self.total_calls = 0

    def call(
        self,
        prompt: str,
        system: str = "",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retries: int = 3,
    ) -> LLMResponse:
        """Call the LLM and return parsed response with cost tracking."""
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens

        for attempt in range(retries):
            try:
                t0 = time.time()
                if self.config.provider != "local":
                    raise ValueError(f"Unsupported provider: {self.config.provider}")
                resp = self._call_local(prompt, system, temp, max_tok)
                resp.latency_s = time.time() - t0
                resp.model = self.config.model

                # Cost tracking
                resp.cost_usd = (
                    resp.input_tokens * self.config.cost_per_1k_input / 1000
                    + resp.output_tokens * self.config.cost_per_1k_output / 1000
                )
                self.total_cost += resp.cost_usd
                self.total_calls += 1
                return resp

            except Exception as e:
                wait = 2 ** attempt
                logger.warning(f"LLM call failed (attempt {attempt+1}/{retries}): {e}. Retrying in {wait}s...")
                if attempt < retries - 1:
                    time.sleep(wait)
                else:
                    raise

    def _call_local(self, prompt, system, temperature, max_tokens) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        url = f"{self.config.resolved_base_url.rstrip('/')}/chat/completions"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer ollama",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Local LLM request failed with HTTP {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not reach local LLM endpoint at {self.config.resolved_base_url}. "
                "Start Ollama with 'ollama serve' and make sure the model is pulled."
            ) from exc

        choices = body.get("choices", [])
        if not choices:
            raise RuntimeError(f"Local LLM response did not contain choices: {body}")
        message = choices[0].get("message", {})
        usage = body.get("usage", {})
        return LLMResponse(
            text=message.get("content", "") or "",
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )

    def cost_report(self) -> str:
        return f"Total calls: {self.total_calls}, Total cost: ${self.total_cost:.4f}"
