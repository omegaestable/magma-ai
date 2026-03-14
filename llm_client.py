"""
llm_client.py — Unified LLM client supporting OpenAI and Anthropic APIs.

Handles retry logic, cost tracking, and response parsing.
Used for cheatsheet distillation and LLM-based evaluation.
"""

import json
import os
import time
import logging
from typing import Optional
from dataclasses import dataclass, field

from config import ModelConfig, MODELS

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
    """Unified client for calling LLM APIs with cost tracking."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        if model_name in MODELS:
            self.config = MODELS[model_name]
        else:
            raise ValueError(f"Unknown model: {model_name}. Available: {list(MODELS.keys())}")
        self.total_cost = 0.0
        self.total_calls = 0
        self._client = None

    def _get_openai_client(self):
        if self._client is None:
            import openai
            self._client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
        return self._client

    def _get_anthropic_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.config.api_key)
        return self._client

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
                if self.config.provider == "openai":
                    resp = self._call_openai(prompt, system, temp, max_tok)
                elif self.config.provider == "anthropic":
                    resp = self._call_anthropic(prompt, system, temp, max_tok)
                else:
                    raise ValueError(f"Unsupported provider: {self.config.provider}")
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

    def _call_openai(self, prompt, system, temperature, max_tokens) -> LLMResponse:
        client = self._get_openai_client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            text=choice.message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

    def _call_anthropic(self, prompt, system, temperature, max_tokens) -> LLMResponse:
        client = self._get_anthropic_client()
        kwargs = {
            "model": self.config.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature > 0:
            kwargs["temperature"] = temperature
        if system:
            kwargs["system"] = system

        response = client.messages.create(**kwargs)
        text = response.content[0].text if response.content else ""
        return LLMResponse(
            text=text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )


    def cost_report(self) -> str:
        return f"Total calls: {self.total_calls}, Total cost: ${self.total_cost:.4f}"
