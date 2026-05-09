"""
LLM Manager - Support for multiple LLM providers
Supports: Anthropic (Claude), OpenAI (GPT), and custom providers
"""

import logging
from typing import Optional
from coach.config import LLMConfig

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Unified interface for multiple LLM providers
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider = config.provider.lower()
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == "anthropic":
            return self._init_anthropic()
        elif self.provider == "openai":
            return self._init_openai()
        elif self.provider == "custom":
            return self._init_custom()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _init_anthropic(self):
        """Initialize Anthropic Claude client"""
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=self.config.api_key)
        except ImportError:
            logger.error("anthropic library not installed. Run: pip install anthropic")
            return None

    def _init_openai(self):
        """Initialize OpenAI GPT client"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.api_key)
            if self.config.base_url:
                client.base_url = self.config.base_url
            return client
        except ImportError:
            logger.error("openai library not installed. Run: pip install openai")
            return None

    def _init_custom(self):
        """Initialize custom LLM provider"""
        try:
            from openai import OpenAI
            # Custom providers often use OpenAI-compatible API
            return OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
        except ImportError:
            logger.error("openai library not installed. Run: pip install openai")
            return None

    def generate_outline(
        self,
        task: str,
        domain: str,
        context: str = ""
    ) -> str:
        """
        Generate task outline using configured LLM
        """
        if not self.client:
            raise RuntimeError(f"LLM client not initialized for {self.provider}")

        prompt = f"""
        Create a structured task outline for the following:

        Task: {task}
        Domain: {domain}
        Context: {context}

        Generate 3-5 main phases with clear descriptions.
        """

        if self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider in ["openai", "custom"]:
            return self._call_openai(prompt)

    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        message = self.client.messages.create(
            model=self.config.model_name,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API (or compatible)"""
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_micro_tasks(
        self,
        phase_description: str,
        target_duration: int = 120
    ) -> str:
        """
        Generate micro-tasks for a phase
        """
        if not self.client:
            raise RuntimeError(f"LLM client not initialized for {self.provider}")

        prompt = f"""
        Break down the following phase into specific micro-tasks of {target_duration} minutes each:

        Phase: {phase_description}

        For each task, include:
        - Title
        - Description
        - Verification criteria (testable)
        - Time estimate

        Format as a numbered list.
        """

        if self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider in ["openai", "custom"]:
            return self._call_openai(prompt)

    def get_coaching_advice(self, context: str) -> str:
        """
        Get coaching advice for a specific situation
        """
        if not self.client:
            raise RuntimeError(f"LLM client not initialized for {self.provider}")

        prompt = f"""
        As an AI coach, provide helpful advice for this situation:

        {context}

        Be encouraging, practical, and actionable.
        """

        if self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider in ["openai", "custom"]:
            return self._call_openai(prompt)

    def __repr__(self) -> str:
        return f"LLMManager(provider={self.provider}, model={self.config.model_name})"
