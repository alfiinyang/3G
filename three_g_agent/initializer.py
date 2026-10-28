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
from pathlib import Path
from typing import Any, Optional, Union

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


def load_dotenv_if_present(env_path: Optional[Union[str, Path]] = None) -> None:
    """Loads key-value pairs from .env file into os.environ if not already set."""
    candidates = [
        Path(env_path) if env_path else None,
        Path(".env"),
        Path("./.3g_agent/.env"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            try:
                content = candidate.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1].strip()
                    if key and key not in os.environ:
                        os.environ[key] = val
                        logger.debug("Loaded %s from %s into environment", key, candidate)
            except Exception as e:
                logger.debug("Could not read .env file from %s: %s", candidate, e)


def collect_api_key(
    api_key: Optional[str] = None,
    interactive_prompt: bool = True,
) -> Optional[str]:
    """Collects API key from explicit argument, .env file, environment, or interactive input."""
    # 0. Load .env file if available
    load_dotenv_if_present()

    # 1. Explicit argument
    if api_key and api_key.strip():
        clean = api_key.strip()
        if (clean.startswith('"') and clean.endswith('"')) or (clean.startswith("'") and clean.endswith("'")):
            clean = clean[1:-1].strip()
        return clean

    # 2. Environment variables
    for env_var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTIGRAVITY_API_KEY"):
        val = os.getenv(env_var)
        if val and val.strip():
            clean = val.strip()
            if (clean.startswith('"') and clean.endswith('"')) or (clean.startswith("'") and clean.endswith("'")):
                clean = clean[1:-1].strip()
            logger.info("Found API key in environment variable: %s", env_var)
            return clean

    # 3. Interactive prompt if terminal attached
    if interactive_prompt and sys.stdin:
        try:
            if sys.stdin.isatty():
                print("\n--- Client Authentication ---")
                print("No API key detected in GEMINI_API_KEY / GOOGLE_API_KEY or .env file.")
                user_key = input("Enter your Gemini/Antigravity API Key (press Enter to skip): ").strip()
                if user_key:
                    if (user_key.startswith('"') and user_key.endswith('"')) or (user_key.startswith("'") and user_key.endswith("'")):
                        user_key = user_key[1:-1].strip()
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
                logger.debug(
                    "No API key provided (%s). Using local testing client adapter. "
                    "Set GEMINI_API_KEY environment variable to execute live remote queries.",
                    val_err,
                )
                return cls._create_fallback_client(
                    config,
                    warning=f"No API key provided ({val_err}). Ensure GEMINI_API_KEY is exported in your active terminal, defined in .env, or passed explicitly.",
                    masked_key=masked_key,
                )
            except Exception as client_err:
                logger.warning("Error initializing GenAI client: %s", client_err)
                return cls._create_fallback_client(
                    config,
                    warning=f"Failed to initialize google.genai.Client: {client_err}",
                    masked_key=masked_key,
                )

        except ImportError as imp_err:
            logger.debug(
                "google-genai package is not installed in the current environment (%s): %s. "
                "Creating simulated client adapter for local testing.",
                sys.executable,
                imp_err,
            )
            return cls._create_fallback_client(
                config,
                warning=(
                    f"google-genai package is not installed in this Python environment ({sys.executable}).\n"
                    f"Details: {imp_err}\n"
                    f"Please run: {sys.executable} -m pip install -r requirements.txt"
                ),
                masked_key=masked_key,
            )

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
                    f"Details: {warning or 'google-genai not configured'}\n\n"
                    f"Resolution Options:\n"
                    f"  1. Persistent Windows PowerShell: [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_key', 'User')\n"
                    f"  2. Current session PowerShell:   $env:GEMINI_API_KEY = 'your_key'\n"
                    f"  3. Create a .env file:            Add GEMINI_API_KEY=your_key in project root\n"
                    f"  4. Linux / macOS:                 export GEMINI_API_KEY='your_key'\n"
                    f"  5. Verify Python Environment:     Ensure you are running the Python environment with dependencies installed ({sys.executable})"
                )

            def delete(self, id: str, **kwargs: Any) -> Any:
                logger.info("FallbackInteractionsAPI.delete called for id='%s'", id)
                return {"status": "deleted", "id": id}

            def cancel(self, id: str, **kwargs: Any) -> Any:
                logger.info("FallbackInteractionsAPI.cancel called for id='%s'", id)
                return {"status": "cancelled", "id": id}

        class FallbackAgentModel:
            def __init__(self, **kwargs: Any) -> None:
                self.id = kwargs.get("id") or "antigravity-preview-09-2026"
                self.base_agent = kwargs.get("base_agent", "antigravity-preview-09-2026")
                self.description = kwargs.get("description", "")
                self.system_instruction = kwargs.get("system_instruction", "")
                self.tools = kwargs.get("tools", [])
                self.agent_config = kwargs.get("agent_config", {})
                self.model = self.agent_config.get("model") or kwargs.get("model") or "gemini-3.1-flash-lite"
                self.created_at = kwargs.get("created_at", "2026-10-20T12:00:00")

            def __repr__(self) -> str:
                return f"Agent(id='{self.id}', base_agent='{self.base_agent}', model='{self.model}')"

        class FallbackAgentListResponse:
            def __init__(self, agents: List[Any]) -> None:
                self.agents = agents
                self.next_page_token = None

        class FallbackAgentsAPI:
            def __init__(self) -> None:
                self._remote_agents: Dict[str, Any] = {}

            def create(self, **kwargs: Any) -> Any:
                agent_id = kwargs.get("id") or "agent-default"
                logger.info("Antigravity SDK API -> POST /agents (create): id='%s'", agent_id)
                agent_obj = FallbackAgentModel(**kwargs)
                self._remote_agents[agent_id] = agent_obj
                return agent_obj

            def delete(self, id: str, **kwargs: Any) -> Any:
                logger.info("Antigravity SDK API -> DELETE /agents/%s", id)
                self._remote_agents.pop(id, None)
                return {"status": "deleted", "id": id}

            def list(self, **kwargs: Any) -> Any:
                logger.info("Antigravity SDK API -> GET /agents (list)")
                return FallbackAgentListResponse(list(self._remote_agents.values()))

            def get(self, id: str, **kwargs: Any) -> Any:
                logger.info("Antigravity SDK API -> GET /agents/%s", id)
                return self._remote_agents.get(id)

        class FallbackEnvironmentsAPI:
            def create(self, **kwargs: Any) -> Any:
                return {"status": "created", "environment_id": "env_fallback_mock"}

            def delete(self, id: str, **kwargs: Any) -> Any:
                logger.info("FallbackEnvironmentsAPI.delete called for id='%s'", id)
                return {"status": "deleted", "id": id}

        class FallbackClient:
            def __init__(self) -> None:
                self.interactions = FallbackInteractionsAPI()
                self.agents = FallbackAgentsAPI()
                self.environments = FallbackEnvironmentsAPI()

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
