"""Subagent Management and Definitions for 3G-agent Architecture.

Features:
- Subagent YAML configuration loader (parsing subagents/*.yaml).
- Designer Subagent:
  * Brain (model): 3.5 flash lite (gemini-3.5-flash-lite).
  * Preloaded with skills from ./skills directory (pedagogy-engineering).
  * Preloaded with desi_instructions (instructions/desi_instructions.md).
  * Coding tools disabled except file access (create, read, write, list) tools.
  * Outputs saved strictly to outputs/design.
- Builder Subagent:
  * Brain (model): 3.8 flash (gemini-3.8-flash).
  * No specific system instruction (called only when time to build).
  * Full coding and execution tools enabled.
  * Outputs saved strictly to outputs/build.
- Both subagents share the same remote environment container across turns.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import yaml
except ImportError:
    yaml = None

from .agent import ThreeGAgent, ThreeGAgentResponse
from .config import (
    MODEL_BUILDER,
    MODEL_DESIGNER,
    ThreeGAgentConfig,
    canonicalize_model_name,
)
from .environment import EnvironmentStore
from .initializer import InitializedClient
from .skills import SkillLoader
from .status import TurnStatusReporter
from .storage import FileStorageManager

logger = logging.getLogger("3G-agent.subagents")


# Standard file access tools permitted for Designer
FILE_ACCESS_TOOLS = ["file_read", "file_write", "file_create", "list_directory", "read_file", "write_file", "create_file", "list_dir"]
# Coding / terminal execution tools disabled for Designer
CODING_EXECUTION_TOOLS = ["code_execution", "run_command", "terminal", "bash", "execute_python", "shell"]


@dataclass
class SubagentConfig:
    """Configuration schema for a specialized subagent."""
    name: str
    role: str = ""
    description: str = ""
    brain: str = ""
    model: str = ""
    system_instruction_file: Optional[Path] = None
    skills_dir: Optional[Path] = None
    skills: List[str] = field(default_factory=list)
    tools_allowed: List[str] = field(default_factory=list)
    tools_disabled: List[str] = field(default_factory=list)
    output_dir: Path = field(default_factory=lambda: Path("outputs"))
    lifecycle: str = "on_demand"
    environment: str = "shared"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "brain": self.brain,
            "model": self.model,
            "system_instruction_file": str(self.system_instruction_file) if self.system_instruction_file else None,
            "skills_dir": str(self.skills_dir) if self.skills_dir else None,
            "skills": self.skills,
            "tools_allowed": self.tools_allowed,
            "tools_disabled": self.tools_disabled,
            "output_dir": str(self.output_dir),
            "lifecycle": self.lifecycle,
            "environment": self.environment,
        }


class SubagentYamlLoader:
    """Discovers and parses subagent YAML definitions from a structured directory."""

    @classmethod
    def _parse_yaml_text(cls, text: str) -> Dict[str, Any]:
        """Parses YAML text using PyYAML with a resilient fallback parser."""
        if yaml is not None:
            return yaml.safe_load(text) or {}
        # Fallback simple parser if yaml library is unavailable
        result: Dict[str, Any] = {}
        current_list_key = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- ") and current_list_key:
                val = line[2:].strip().strip("\"'")
                result[current_list_key].append(val)
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if not val:
                    result[key] = []
                    current_list_key = key
                else:
                    current_list_key = None
                    if val.lower() == "null" or val == "~":
                        result[key] = None
                    elif val.startswith("[") and val.endswith("]"):
                        items = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
                        result[key] = items
                    else:
                        result[key] = val.strip("\"'")
        return result

    @classmethod
    def load_file(cls, yaml_path: Union[str, Path]) -> SubagentConfig:
        """Loads a single subagent YAML specification file."""
        p = Path(yaml_path)
        if not p.is_file():
            raise FileNotFoundError(f"Subagent YAML definition not found: {p}")

        content = p.read_text(encoding="utf-8")
        raw = cls._parse_yaml_text(content)

        name = raw.get("name") or p.stem
        brain = raw.get("brain") or ""
        model = raw.get("model") or brain

        sys_instr = raw.get("system_instruction_file")
        sys_instr_path = Path(sys_instr) if sys_instr else None

        skills_dir_raw = raw.get("skills_dir")
        skills_dir_path = Path(skills_dir_raw) if skills_dir_raw else None

        output_dir_raw = raw.get("output_dir", "outputs")
        output_dir_path = Path(output_dir_raw)

        tools_sec = raw.get("tools") or {}
        if isinstance(tools_sec, dict):
            allowed = tools_sec.get("allowed") or []
            disabled = tools_sec.get("disabled") or []
        else:
            allowed = raw.get("tools_allowed") or []
            disabled = raw.get("tools_disabled") or []

        return SubagentConfig(
            name=name,
            role=raw.get("role", ""),
            description=raw.get("description", ""),
            brain=brain,
            model=model,
            system_instruction_file=sys_instr_path,
            skills_dir=skills_dir_path,
            skills=raw.get("skills") or [],
            tools_allowed=allowed,
            tools_disabled=disabled,
            output_dir=output_dir_path,
            lifecycle=raw.get("lifecycle", "on_demand"),
            environment=raw.get("environment", "shared"),
        )

    @classmethod
    def load_all(cls, subagents_dir: Union[str, Path] = "./subagents") -> Dict[str, SubagentConfig]:
        """Loads all YAML subagent definitions found in the specified directory."""
        dir_path = Path(subagents_dir)
        configs: Dict[str, SubagentConfig] = {}
        if not dir_path.is_dir():
            logger.warning("Subagents directory not found: %s", dir_path)
            return configs

        for yaml_file in sorted(dir_path.glob("*.yaml")) + sorted(dir_path.glob("*.yml")):
            try:
                cfg = cls.load_file(yaml_file)
                configs[cfg.name] = cfg
                logger.info("Loaded subagent YAML spec: '%s' from %s", cfg.name, yaml_file.name)
            except Exception as err:
                logger.warning("Failed parsing subagent YAML %s: %s", yaml_file, err)

        return configs


class DesignerSubagent:
    """Specialized Pedagogical Designer Subagent.
    
    Attributes:
        brain / model: 3.5 flash lite (gemini-3.5-flash-lite).
        skills: Preloaded from ./skills folder (pedagogy-engineering).
        instructions: Preloaded from instructions/desi_instructions.md.
        tools: File access only (create/read/write/list); coding tools disabled.
        outputs: Written strictly to outputs/design.
    """

    def __init__(
        self,
        environment_store: EnvironmentStore,
        agent_id: Optional[str] = None,
        client_handle: Optional[InitializedClient] = None,
        skills_dir: Union[str, Path] = "./skills",
        instructions_file: Union[str, Path, None] = "./instructions/desi_instructions.md",
        output_dir: Union[str, Path] = "./outputs/design",
        state_dir: Union[str, Path] = "./.3g_agent",
        brain: str = MODEL_DESIGNER,
    ) -> None:
        self.brain = brain
        self.agent_id = agent_id or "desi-001"
        self.skills_dir = Path(skills_dir)
        self.instructions_file = Path(instructions_file) if instructions_file else None
        self.output_dir = Path(output_dir)
        self.environment = environment_store
        self.state_dir = Path(state_dir)

        # Confirm instructions file exists strictly within /instructions
        if self.instructions_file and not self.instructions_file.exists():
            alt = Path("./instructions/desi_instructions.md")
            if alt.exists():
                self.instructions_file = alt

        self.tools_allowed = list(FILE_ACCESS_TOOLS)
        self.tools_disabled = list(CODING_EXECUTION_TOOLS)

        # Assemble underlying ThreeGAgent using custom agent_id and brain model
        self.config = ThreeGAgentConfig(
            agent_name="3G-designer-subagent",
            agent_id=self.agent_id,
            model=brain,
            brain=brain,
            skills_dir=self.skills_dir,
            instructions_file=self.instructions_file,
            output_dir=self.output_dir,
            state_dir=self.state_dir,
            tools_allowed=self.tools_allowed,
            tools_disabled=self.tools_disabled,
        )

        # Reuse client handle if supplied, or initialize client
        from .initializer import AgentClientInitializer
        self.client_handle = client_handle or AgentClientInitializer.initialize(
            self.config, interactive_prompt=False
        )
        self.skill_loader = SkillLoader(self.skills_dir)
        self.storage_manager = FileStorageManager(output_dir=self.output_dir)

        self._agent = ThreeGAgent(
            config=self.config,
            initialized_client=self.client_handle,
            skill_loader=self.skill_loader,
            environment_store=self.environment,
            storage_manager=self.storage_manager,
            load_local_context=True,
        )

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Confirms tool is permitted (file access only, coding tools disabled)."""
        clean = tool_name.lower().strip()
        if any(bad in clean for bad in ("code", "exec", "terminal", "bash", "shell", "run")):
            return False
        return any(ok in clean for ok in ("file", "read", "write", "create", "list", "dir"))

    def execute(
        self,
        prompt: str,
        status_reporter: Optional[TurnStatusReporter] = None,
        show_status: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes a design task in the shared remote environment."""
        logger.info("Executing Designer Subagent (brain: %s) -> outputs/design", self.brain)
        return self._agent.execute(
            prompt=prompt,
            save_deliverables_locally=True,
            status_reporter=status_reporter,
            show_status=show_status,
        )


class BuilderSubagent:
    """Specialized Implementation and Code Construction Builder Subagent.
    
    Attributes:
        brain / model: 3.8 flash (gemini-3.8-flash).
        skills: None (builder agent has no custom skills).
        instructions: None (builder agent has no specific system instruction).
        tools: Full coding and execution tools enabled.
        outputs: Written strictly to outputs/build.
    """

    def __init__(
        self,
        environment_store: EnvironmentStore,
        agent_id: Optional[str] = None,
        client_handle: Optional[InitializedClient] = None,
        output_dir: Union[str, Path] = "./outputs/build",
        state_dir: Union[str, Path] = "./.3g_agent",
        brain: str = MODEL_BUILDER,
    ) -> None:
        self.brain = brain
        self.agent_id = agent_id or "build-001"
        self.output_dir = Path(output_dir)
        self.environment = environment_store
        self.state_dir = Path(state_dir)

        self.tools_allowed = list(FILE_ACCESS_TOOLS) + list(CODING_EXECUTION_TOOLS)
        self.tools_disabled: List[str] = []

        # Builder subagent has NO specific system instruction file and NO custom skills
        self.config = ThreeGAgentConfig(
            agent_name="3G-builder-subagent",
            agent_id=self.agent_id,
            model=brain,
            brain=brain,
            skills_dir=None,
            instructions_file=None,
            system_instruction_override=None,
            output_dir=self.output_dir,
            state_dir=self.state_dir,
            tools_allowed=self.tools_allowed,
            tools_disabled=self.tools_disabled,
        )

        from .initializer import AgentClientInitializer
        self.client_handle = client_handle or AgentClientInitializer.initialize(
            self.config, interactive_prompt=False
        )
        self.skill_loader = SkillLoader.empty()
        self.storage_manager = FileStorageManager(output_dir=self.output_dir)

        self._agent = ThreeGAgent(
            config=self.config,
            initialized_client=self.client_handle,
            skill_loader=self.skill_loader,
            environment_store=self.environment,
            storage_manager=self.storage_manager,
            load_local_context=False,
        )

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Confirms tool is permitted (all coding and file tools allowed)."""
        return True

    def execute(
        self,
        prompt: str,
        status_reporter: Optional[TurnStatusReporter] = None,
        show_status: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes a building task in the shared remote environment."""
        logger.info("Executing Builder Subagent (brain: %s) -> outputs/build", self.brain)
        return self._agent.execute(
            prompt=prompt,
            save_deliverables_locally=True,
            status_reporter=status_reporter,
            show_status=show_status,
        )
