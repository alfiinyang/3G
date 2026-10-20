"""Configuration and Client Parameter Collection for 3G-agent.

Strictly separates configuration parsing, parameter collection, and validation
from model initialization and runtime execution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ThreeGAgentConfig:
    """Strongly-typed configuration schema for 3G-agent.
    
    Attributes:
        agent_name: Name identifier of the agent (default: "3G-agent").
        model_name: Underlying Gemini/Antigravity model or agent ID.
        environment_type: Sandbox environment type ("remote" by default).
        api_key: Gemini/Google Cloud API Key (optional if using ADC or env vars).
        skills_dir: Path to directory containing a skill or group of skills.
        state_dir: Local directory for securely storing environment IDs and session state.
        output_dir: Local directory where created files and artifacts are stored locally.
        vertex_ai: Whether to use Vertex AI / Gemini Enterprise backend.
        project: Google Cloud project ID (for Vertex AI).
        location: Google Cloud region (e.g., "us-central1").
        max_total_tokens: Optional token limit for agent reasoning and execution.
        system_instruction_override: Optional custom system instructions.
        instructions_file: Path to instructions.md holding system prompt.
        extra_sources: Additional files or sources to mount in the remote environment.
    """

    agent_name: str = "3G-agent"
    model_name: str = "antigravity-preview-09-2026"
    environment_type: str = "remote"
    api_key: Optional[str] = None
    skills_dir: Path = field(default_factory=lambda: Path("./skills"))
    state_dir: Path = field(default_factory=lambda: Path("./.3g_agent"))
    output_dir: Path = field(default_factory=lambda: Path("./outputs/3g_agent"))
    instructions_file: Optional[Path] = field(default_factory=lambda: Path("./instructions.md"))
    vertex_ai: bool = False
    project: Optional[str] = None
    location: Optional[str] = None
    max_total_tokens: Optional[int] = None
    system_instruction_override: Optional[str] = None
    extra_sources: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Convert string paths to Path objects and normalize defaults."""
        if isinstance(self.skills_dir, str):
            self.skills_dir = Path(self.skills_dir)
        if isinstance(self.state_dir, str):
            self.state_dir = Path(self.state_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.instructions_file, str):
            self.instructions_file = Path(self.instructions_file)

    def load_instructions(self) -> Optional[str]:
        """Loads system instructions from override or instructions.md file."""
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

        # Resolve API Key from environment if not explicitly passed
        if not self.api_key:
            self.api_key = (
                os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or os.getenv("ANTIGRAVITY_API_KEY")
            )

        # Resolve GCP Project from environment if not explicitly passed
        if not self.project:
            self.project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")

        if not self.location:
            self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


class ClientParameterCollector:
    """Collects, validates, and builds configuration parameters for 3G-agent.
    
    This component is solely responsible for collecting client parameters from
    various inputs (CLI args, environment variables, settings files, dicts)
    and ensuring validation before any model initialization or runtime execution occurs.
    """

    @classmethod
    def from_env(cls, skills_dir: Optional[str | Path] = None) -> ThreeGAgentConfig:
        """Constructs configuration by collecting all settings from environment variables."""
        resolved_skills_dir = Path(skills_dir) if skills_dir else Path(os.getenv("ANTIGRAVITY_SKILLS_DIR", "./skills"))
        
        return ThreeGAgentConfig(
            agent_name=os.getenv("ANTIGRAVITY_AGENT_NAME", "3G-agent"),
            model_name=os.getenv("ANTIGRAVITY_MODEL", "antigravity-preview-09-2026"),
            environment_type="remote",  # Mandatory requirement: set environment to remote
            api_key=(
                os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or os.getenv("ANTIGRAVITY_API_KEY")
            ),
            skills_dir=resolved_skills_dir,
            state_dir=Path(os.getenv("ANTIGRAVITY_STATE_DIR", "./.3g_agent")),
            output_dir=Path(os.getenv("ANTIGRAVITY_OUTPUT_DIR", "./outputs/3g_agent")),
            instructions_file=Path(os.getenv("ANTIGRAVITY_INSTRUCTIONS_FILE", "./instructions.md")),
            vertex_ai=os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() in ("true", "1", "yes"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ThreeGAgentConfig:
        """Constructs and validates configuration from a dictionary."""
        config_data = dict(data)
        # Ensure environment_type defaults to remote if not explicitly provided
        config_data.setdefault("environment_type", "remote")
        config_data.setdefault("agent_name", "3G-agent")
        return ThreeGAgentConfig(**config_data)

    @classmethod
    def validate(cls, config: ThreeGAgentConfig) -> List[str]:
        """Validates configuration parameters and returns a list of warnings or issues.
        
        Raises:
            ValueError: If critical mandatory parameters are missing or invalid.
        """
        errors: List[str] = []

        if config.environment_type != "remote":
            # Per requirement: Environment MUST be remote
            errors.append(f"environment_type must be 'remote', got '{config.environment_type}'")

        if not config.skills_dir.exists():
            errors.append(f"Specified skills directory does not exist: {config.skills_dir.resolve()}")

        if not config.api_key and not config.vertex_ai:
            # Note: Might still work if user has gcloud auth ADC configured
            pass

        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

        return errors
