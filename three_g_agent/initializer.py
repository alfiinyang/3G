"""Agent Client Initialization and Factory for 3G-agent.

STRICT SEPARATION OF CONCERNS:
This module is strictly isolated to agent client connection and authentication. It takes
pre-collected parameters from `ThreeGAgentConfig`, creates and authenticates
the client instance, and returns an initialized handle. No prompt execution,
turn orchestration, or task execution takes place in this file.
"""

from __future__ import annotations

import getpass
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Optional

from .config import ThreeGAgentConfig

logger = logging.getLogger("3G-agent.initializer")


def mask_api_key(api_key: Optional[str]) -> str:
    """Masks an API key for safe terminal display (e.g. AIzaSy...7890)."""
    if not api_key:
        return "[Not Provided - Local Testing Adapter]"
    clean = api_key.strip()
    if len(clean) <= 10:
        return clean[:2] + "..." + clean[-2:]
    return clean[:6] + "..." + clean[-4:]


def collect_api_key(
    api_key: Optional[str] = None,
    interactive_prompt: bool = True,
) -> Optional[str]:
    """Collects API key from explicit argument, environment, or interactive input."""
    # 1. Explicit argument
    if api_key and api_key.strip():
        return api_key.strip()

    # 2. Environment variables
    for env_var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTIGRAVITY_API_KEY"):
        val = os.getenv(env_var)
        if val and val.strip():
            logger.info("Found API key in environment variable: %s", env_var)
            return val.strip()

    # 3. Interactive prompt if terminal attached
    if interactive_prompt and sys.stdin and sys.stdin.isatty():
        print("\n--- Client Authentication ---")
        print("No API key detected in GEMINI_API_KEY / GOOGLE_API_KEY.")
        try:
            user_key = input("Enter your Gemini/Antigravity API Key (press Enter to skip): ").strip()
            if user_key:
                # Save to os.environ for child modules
                os.environ["GEMINI_API_KEY"] = user_key
                return user_key
        except (EOFError, KeyboardInterrupt):
            pass

    return None


@dataclass
class InitializedClient:
    """Represents a successfully initialized client connection.
    
    Attributes:
        client: The underlying SDK client instance (google.genai.Client or adapter).
        config: The configuration used to initialize this client.
        backend_type: Description of backend ("genai_api_key", "vertex_ai", or "custom").
        masked_api_key: Masked string for safe display.
    """
    client: Any
    config: ThreeGAgentConfig
    backend_type: str
    masked_api_key: str = "[None]"


class AgentClientInitializer:
    """Factory responsible strictly for agent client connection and authentication.
    
    Decoupled from client parameter collection and execution loops.
    """

    @classmethod
    def initialize(
        cls,
        config: ThreeGAgentConfig,
        interactive_prompt: bool = False,
    ) -> InitializedClient:
        """Initializes the SDK client instance based on the provided configuration.
        
        Args:
            config: Validated ThreeGAgentConfig instance.
            interactive_prompt: Whether to prompt for API key if missing and in terminal.
            
        Returns:
            InitializedClient handle containing the live client.
        """
        # Ensure API key is collected if not already populated
        if not config.api_key and not config.vertex_ai:
            collected = collect_api_key(config.api_key, interactive_prompt=interactive_prompt)
            if collected:
                config.api_key = collected

        masked_key = mask_api_key(config.api_key)

        logger.info(
            "Initializing Antigravity SDK client for agent '%s' targeting agent ID '%s'...",
            config.agent_name,
            config.agent_id,
        )

        try:
            # Attempt to import official google.genai SDK
            from google import genai
            from google.genai import types

            client_kwargs: dict[str, Any] = {}

            if config.vertex_ai:
                client_kwargs["vertexai"] = True
                if config.project:
                    client_kwargs["project"] = config.project
                if config.location:
                    client_kwargs["location"] = config.location
                backend_type = "Vertex AI (Enterprise GCP)"
            else:
                if config.api_key:
                    client_kwargs["api_key"] = config.api_key
                backend_type = "Google GenAI API (Developer)"

            try:
                client = genai.Client(**client_kwargs)
                logger.info("Successfully initialized GenAI client (backend: %s)", backend_type)

                return InitializedClient(
                    client=client,
                    config=config,
                    backend_type=backend_type,
                    masked_api_key=masked_key,
                )
            except ValueError as val_err:
                logger.warning(
                    "No API key provided (%s). Using local testing client adapter. "
                    "Set GEMINI_API_KEY environment variable to execute live remote queries.",
                    val_err,
                )
                return cls._create_fallback_client(config, warning=str(val_err), masked_key=masked_key)

        except ImportError:
            logger.warning(
                "google-genai package is not installed in the current environment. "
                "Creating simulated client adapter for local testing."
            )
            return cls._create_fallback_client(config, masked_key=masked_key)

    @classmethod
    def _create_fallback_client(
        cls,
        config: ThreeGAgentConfig,
        warning: Optional[str] = None,
        masked_key: str = "[None]",
    ) -> InitializedClient:
        """Creates a mock/fallback client adapter when live SDK is not authenticated or not imported."""
        class FallbackInteractionsAPI:
            def create(self, **kwargs: Any) -> Any:
                raise RuntimeError(
                    f"Live API execution requires an API key or ADC credentials.\n"
                    f"Details: {warning or 'google-genai not configured'}\n"
                    f"Please export your API key:\n"
                    f"  PowerShell: $env:GEMINI_API_KEY = 'your_api_key'\n"
                    f"  Bash: export GEMINI_API_KEY='your_api_key'"
                )

        class FallbackClient:
            def __init__(self) -> None:
                self.interactions = FallbackInteractionsAPI()

        return InitializedClient(
            client=FallbackClient(),
            config=config,
            backend_type="Local Test Adapter (Requires GEMINI_API_KEY for live execution)",
            masked_api_key=masked_key,
        )

    @classmethod
    def display_success(cls, initialized: InitializedClient) -> None:
        """Displays a clean summary of successful client initialization."""
        print("\n" + "=" * 65)
        print("  [+] Client Connection Successfully Initialized")
        print("=" * 65)
        print(f"  Backend Type  : {initialized.backend_type}")
        print(f"  API Key       : {initialized.masked_api_key}")
        print(f"  Base Engine   : Antigravity Coding Agent (antigravity-preview-09-2026)")
        print(f"  Environment   : Remote Managed Sandbox Container")
        print("=" * 65)


# Backward-compatible alias
ModelInitializer = AgentClientInitializer
