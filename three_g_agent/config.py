"""Configuration and Client Parameter Collection for 3G-agent.

Strictly separates configuration parsing, parameter collection, and validation
from model initialization and runtime execution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


MODEL_ORCHESTRATOR = "3.1 flash lite"
MODEL_DESIGNER = "3.5 flash lite"
MODEL_BUILDER = "3.8 flash"

CANONICAL_MODEL_MAP: Dict[str, str] = {
    "3.1 flash lite": "gemini-3.1-flash-lite",
    "3.1-flash-lite": "gemini-3.1-flash-lite",
    "3.5 flash lite": "gemini-3.5-flash-lite",
    "3.5-flash-lite": "gemini-3.5-flash-lite",
    "3.8 flash": "gemini-3.8-flash",
    "3.8-flash": "gemini-3.8-flash",
}


def canonicalize_model_name(name: Optional[str]) -> str:
    """Normalizes model names (e.g. '3.1 flash lite' -> 'gemini-3.1-flash-lite')."""
    if not name:
        return "gemini-3.1-flash-lite"
    clean = str(name).strip()
    return CANONICAL_MODEL_MAP.get(clean.lower(), clean)


def resolve_default_agent_id() -> str:
    """Resolves the default custom agent ID, ignoring boolean environment flags.
    
    agent_id is strictly the user-defined custom agent identifier (e.g. orch-001, coder-12345),
    never a base model name or engine name.
    """
    env_agent = os.getenv("ANTIGRAVITY_AGENT_ID")
    if not env_agent:
        raw_agent = os.getenv("ANTIGRAVITY_AGENT")
        if raw_agent and raw_agent.lower() not in ("1", "0", "true", "false", "yes", "no"):
            env_agent = raw_agent

    return env_agent or "orch-001"


def is_base_agent_id(agent_id: Optional[str]) -> bool:
    """Deprecated helper retained for backwards compatibility.
    
    In 3G-agent, agent_id is strictly the ID given to the custom agent.
    """
    return False


def resolve_default_instructions_file() -> Path:
    """Finds instructions file strictly within the /instructions directory."""
    env_file = os.getenv("ANTIGRAVITY_INSTRUCTIONS_FILE")
    if env_file:
        p = Path(env_file)
        if p.exists():
            return p
    for candidate in [
        Path("./instructions/orch_instruction.md"),
        Path("./instructions/desi_instructions.md"),
    ]:
        if candidate.exists():
            return candidate
    return Path("./instructions/orch_instruction.md")



@dataclass
class ThreeGAgentConfig:
    """Strongly-typed configuration schema for 3G-agent.
    
    Attributes:
        agent_name: Name identifier of the agent (default: "3G-agent").
        agent_id: User-defined custom agent identifier (e.g. "orch-001", "coder-12345").
        environment_type: Sandbox environment type ("remote" by default).
        api_key: Gemini/Google Cloud API Key (optional if using ADC or env vars).
        skills_dir: Path to directory containing a skill or group of skills (None if no skills needed).
        state_dir: Local directory for securely storing environment IDs and session state.
        output_dir: Local directory where created files and artifacts are stored locally.
        vertex_ai: Whether to use Vertex AI / Gemini Enterprise backend.
        project: Google Cloud project ID (for Vertex AI).
        location: Google Cloud region (e.g., "us-central1").
        max_total_tokens: Optional token limit for agent reasoning and execution.
        system_instruction_override: Optional custom system instructions.
        instructions_file: Path to instructions file holding system prompt.
        extra_sources: Additional files or sources to mount in the remote environment.
        model_name: Optional backwards-compatible alias for model / brain.
        model: Model / brain identifier (e.g. '3.1 flash lite', '3.5 flash lite', '3.8 flash').
        brain: Semantic alias for model.
        tools_allowed: Optional list of allowed tools (for tool restriction).
        tools_disabled: Optional list of disabled tools (for tool restriction).
    """

    agent_name: str = "3G-agent"
    agent_id: str = field(default_factory=resolve_default_agent_id)
    environment_type: str = "remote"
    api_key: Optional[str] = None
    skills_dir: Optional[Path] = field(default_factory=lambda: Path("./skills"))
    state_dir: Path = field(default_factory=lambda: Path("./.3g_agent"))
    output_dir: Path = field(default_factory=lambda: Path("./outputs/3g_agent"))
    instructions_file: Optional[Path] = field(default_factory=resolve_default_instructions_file)
    vertex_ai: bool = False
    project: Optional[str] = None
    location: Optional[str] = None
    max_total_tokens: Optional[int] = None
    system_instruction_override: Optional[str] = None
    extra_sources: List[Dict[str, Any]] = field(default_factory=list)
    model_name: Optional[str] = None
    model: Optional[str] = None
    brain: Optional[str] = None
    tools_allowed: Optional[List[str]] = None
    tools_disabled: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Convert string paths to Path objects and normalize defaults."""
        # Synchronize brain and model aliases without overwriting agent_id
        if self.brain and not self.model:
            self.model = self.brain
        elif self.model and not self.brain:
            self.brain = self.model
        if self.skills_dir is not None and isinstance(self.skills_dir, str):
            self.skills_dir = Path(self.skills_dir)
        if isinstance(self.state_dir, str):
            self.state_dir = Path(self.state_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.instructions_file, str):
            self.instructions_file = Path(self.instructions_file)

        # Ensure custom agent_id is valid and non-boolean
        if not self.agent_id or str(self.agent_id).strip() in ("1", "0", "true", "false", "yes", "no"):
            self.agent_id = resolve_default_agent_id()

        # Resolve model / brain aliases without overwriting agent_id
        chosen_model = self.model or self.brain or self.model_name
        if chosen_model and str(chosen_model).strip() not in ("1", "0", "true", "false", "yes", "no"):
            clean_m = str(chosen_model).strip()
            self.model = clean_m
            self.brain = clean_m
            self.model_name = clean_m

        # Resolve API Key from environment or .env if not explicitly passed
        if not self.api_key:
            from .initializer import load_dotenv_if_present
            load_dotenv_if_present()
            self.api_key = (
                os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or os.getenv("ANTIGRAVITY_API_KEY")
            )

        if self.api_key:
            self.api_key = self.api_key.strip()
            if (self.api_key.startswith('"') and self.api_key.endswith('"')) or (self.api_key.startswith("'") and self.api_key.endswith("'")):
                self.api_key = self.api_key[1:-1].strip()

        # Resolve GCP Project from environment if not explicitly passed
        if not self.project:
            self.project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")

        if not self.location:
            self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    def load_instructions(self) -> Optional[str]:
        """Loads system instructions from override or instructions file."""
        if self.system_instruction_override and self.system_instruction_override.strip():
            return self.system_instruction_override.strip()

        if self.instructions_file and self.instructions_file.is_file():
            try:
                content = self.instructions_file.read_text(encoding="utf-8").strip()
                if content:
                    return content
            except Exception:
                pass
        return None




class ClientParameterCollector:
    """Collects, validates, and builds configuration parameters for 3G-agent.
    
    This component is solely responsible for collecting client parameters from
    various inputs (CLI args, environment variables, settings files, dicts)
    and ensuring validation before any agent client initialization or runtime execution occurs.
    """

    @classmethod
    def from_env(cls, skills_dir: Optional[str | Path] = None) -> ThreeGAgentConfig:
        """Constructs configuration by collecting all settings from environment variables."""
        resolved_skills_dir = Path(skills_dir) if skills_dir else Path(os.getenv("ANTIGRAVITY_SKILLS_DIR", "./skills"))
        
        return ThreeGAgentConfig(
            agent_name=os.getenv("ANTIGRAVITY_AGENT_NAME", "3G-agent"),
            agent_id=resolve_default_agent_id(),
            environment_type="remote",  # Mandatory requirement: set environment to remote
            api_key=(
                os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or os.getenv("ANTIGRAVITY_API_KEY")
            ),
            skills_dir=resolved_skills_dir,
            state_dir=Path(os.getenv("ANTIGRAVITY_STATE_DIR", "./.3g_agent")),
            output_dir=Path(os.getenv("ANTIGRAVITY_OUTPUT_DIR", "./outputs/3g_agent")),
            instructions_file=Path(os.getenv("ANTIGRAVITY_INSTRUCTIONS_FILE", "./instructions/orch_instruction.md")),
            vertex_ai=os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() in ("true", "1", "yes"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ThreeGAgentConfig:
        """Constructs and validates configuration from a dictionary."""
        config_data = dict(data)
        # Handle model, brain, and backwards-compatible model_name key
        for key in ("model", "brain", "model_name"):
            if key in config_data and "agent_id" not in config_data:
                val = config_data.pop(key)
                if val and str(val).lower() not in ("1", "0", "true", "false"):
                    config_data["agent_id"] = val
        # Ensure environment_type defaults to remote if not explicitly provided
        config_data.setdefault("environment_type", "remote")
        config_data.setdefault("agent_name", "3G-agent")
        return ThreeGAgentConfig(**config_data)

    @classmethod
    def validate(cls, config: ThreeGAgentConfig, require_skills_dir: bool = True) -> List[str]:
        """Validates configuration parameters and returns a list of warnings or issues.
        
        Raises:
            ValueError: If critical mandatory parameters are missing or invalid.
        """
        errors: List[str] = []

        if config.environment_type != "remote":
            # Per requirement: Environment MUST be remote
            errors.append(f"environment_type must be 'remote', got '{config.environment_type}'")

        if require_skills_dir and config.skills_dir is not None and not config.skills_dir.exists():
            errors.append(f"Specified skills directory does not exist: {config.skills_dir.resolve()}")

        if not config.api_key and not config.vertex_ai:
            # Note: Might still work if user has gcloud auth ADC configured
            pass

        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

        return errors

