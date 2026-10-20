"""Model Initialization and Client Factory for 3G-agent.

STRICT SEPARATION OF CONCERNS:
This module is strictly isolated to model and client initialization. It takes
pre-collected parameters from `ThreeGAgentConfig`, creates and authenticates
the client instance, and returns an initialized handle. No prompt execution,
turn orchestration, or task execution takes place in this file.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from .config import ThreeGAgentConfig

logger = logging.getLogger("3G-agent.initializer")


@dataclass
class InitializedClient:
    """Represents a successfully initialized client connection.
    
    Attributes:
        client: The underlying SDK client instance (google.genai.Client or adapter).
        config: The configuration used to initialize this client.
        backend_type: Description of backend ("genai_api_key", "vertex_ai", or "custom").
    """
    client: Any
    config: ThreeGAgentConfig
    backend_type: str


class ModelInitializer:
    """Factory responsible strictly for model client creation and authentication.
    
    Decoupled from client parameter collection and execution loops.
    """

    @classmethod
    def initialize(cls, config: ThreeGAgentConfig) -> InitializedClient:
        """Initializes the SDK client instance based on the provided configuration.
        
        Args:
            config: Validated ThreeGAgentConfig instance.
            
        Returns:
            InitializedClient handle containing the live client.
            
        Raises:
            RuntimeError: If initialization or authentication fails.
        """
        logger.info(
            "Initializing Antigravity SDK client for agent '%s' targeting model '%s'...",
            config.agent_name,
            config.model_name,
        )

        try:
            # First, attempt to import the official google.genai SDK
            from google import genai
            from google.genai import types

            client_kwargs: dict[str, Any] = {}

            if config.vertex_ai:
                client_kwargs["vertexai"] = True
                if config.project:
                    client_kwargs["project"] = config.project
                if config.location:
                    client_kwargs["location"] = config.location
                backend_type = "vertex_ai"
            else:
                if config.api_key:
                    client_kwargs["api_key"] = config.api_key
                backend_type = "genai_api_key"

            client = genai.Client(**client_kwargs)
            logger.info("Successfully initialized GenAI client (backend: %s)", backend_type)

            return InitializedClient(
                client=client,
                config=config,
                backend_type=backend_type,
            )

        except ImportError:
            # Fallback or adapter if google-genai package is pending installation
            logger.warning(
                "google-genai package is not installed in the current environment. "
                "Creating simulated client adapter for local testing."
            )
            return cls._create_fallback_client(config)

    @classmethod
    def _create_fallback_client(cls, config: ThreeGAgentConfig) -> InitializedClient:
        """Creates a mock/fallback client adapter when live SDK is not yet imported."""
        class FallbackInteractionsAPI:
            def create(self, **kwargs: Any) -> Any:
                raise RuntimeError(
                    "google-genai package is required to execute remote Antigravity interactions. "
                    "Please install via: pip install google-genai google-antigravity"
                )

        class FallbackClient:
            def __init__(self) -> None:
                self.interactions = FallbackInteractionsAPI()

        return InitializedClient(
            client=FallbackClient(),
            config=config,
            backend_type="mock_fallback",
        )
