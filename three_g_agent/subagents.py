"""Subagent Management and Definitions for 3G-agent Architecture.

Four Remote Preloaded Agents:
1. Orchestrator (parent agent, primary facade)
2. Pedagogy Engineer Subagent (PEDA: curriculum, learning goals, Bloom objectives)
3. Learning Experience Engineer Subagent (LX: narrative, scenes, learner journey, tasks)
4. Software Product Manager Subagent (PM: requirements translation, PRD, technical contracts)

Key Principles:
- All agents sit in Antigravity SDK remote environment with preloaded instructions.
- No skills employed (skills folder kept).
- All agents share the same environment container across turns (environment = previous_turn.environment_id).
- Turn ID continuity: every turn captures turn.id and saves it to TurnIdRegistry for that agent,
  so subsequent turns pass previous_interaction_id = previous_turn.id.
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
    AGENT_LEARNING_EXPERIENCE,
    AGENT_ORCHESTRATOR,
    AGENT_PEDAGOGY,
    AGENT_PRODUCT_MANAGER,
    MODEL_BUILDER,
    MODEL_DESIGNER,
    ThreeGAgentConfig,
    canonicalize_model_name,
    resolve_lx_agent_id,
    resolve_pedagogy_agent_id,
    resolve_pm_agent_id,
)
from .environment import EnvironmentStore
from .initializer import InitializedClient
from .registry import TurnIdRegistry
from .skills import SkillLoader
from .status import TurnStatusReporter
from .storage import FileStorageManager

logger = logging.getLogger("3G-agent.subagents")


# Standard file access tools permitted for design subagents
FILE_ACCESS_TOOLS = [
    "file_read", "file_write", "file_create", "list_directory",
    "read_file", "write_file", "create_file", "list_dir", "view_file",
    "edit_file", "search_directory", "find_file",
]
# Coding / terminal execution tools
CODING_EXECUTION_TOOLS = [
    "code_execution", "run_command", "terminal", "bash", "execute_python", "shell"
]


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


class PedagogySubagent:
    """Specialized Pedagogy Engineering Subagent (PEDA).

    Attributes:
        agent_name: pedagogy_engineer
        role: Pedagogical Architecture, measurable objectives, curricula
        output_dir: outputs/pedagogical_design
        instructions: Preloaded remotely in Antigravity SDK environment
        skills: No local skills employed
    """

    def __init__(
        self,
        environment_store: EnvironmentStore,
        client_handle: Optional[InitializedClient] = None,
        turn_registry: Optional[TurnIdRegistry] = None,
        skills_dir: Union[str, Path] = "./skills",
        instructions_file: Union[str, Path, None] = "./instructions/PEDA-instructions.md",
        output_dir: Union[str, Path] = "./outputs/pedagogical_design",
        state_dir: Union[str, Path] = "./.3g_agent",
        brain: str = MODEL_DESIGNER,
        agent_id: Optional[str] = None,
    ) -> None:
        self.brain = brain
        self.skills_dir = Path(skills_dir)
        self.instructions_file = Path(instructions_file) if instructions_file else None
        self.output_dir = Path(output_dir)
        self.environment = environment_store
        self.state_dir = Path(state_dir)
        self.turn_registry = turn_registry or TurnIdRegistry(state_dir=self.state_dir)

        self.tools_allowed = list(FILE_ACCESS_TOOLS)
        self.tools_disabled = list(CODING_EXECUTION_TOOLS)

        resolved_agent_id = agent_id or resolve_pedagogy_agent_id()

        self.config = ThreeGAgentConfig(
            agent_name=AGENT_PEDAGOGY,
            agent_id=resolved_agent_id,
            model=brain,
            brain=brain,
            skills_dir=self.skills_dir,
            instructions_file=self.instructions_file,
            output_dir=self.output_dir,
            state_dir=self.state_dir,
            tools_allowed=self.tools_allowed,
            tools_disabled=self.tools_disabled,
        )

        from .initializer import AgentClientInitializer
        self.client_handle = client_handle or AgentClientInitializer.initialize(
            self.config, interactive_prompt=False
        )
        # Skills folder kept, but no skills employed
        self.skill_loader = SkillLoader.empty()
        self.storage_manager = FileStorageManager(output_dir=self.output_dir)

        self._agent = ThreeGAgent(
            config=self.config,
            initialized_client=self.client_handle,
            skill_loader=self.skill_loader,
            environment_store=self.environment,
            storage_manager=self.storage_manager,
            turn_registry=self.turn_registry,
            load_local_context=False,
        )

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Confirms tool is permitted (file access only, coding tools disabled)."""
        clean = tool_name.lower().strip()
        if any(bad in clean for bad in ("code", "exec", "terminal", "bash", "shell", "run")):
            return False
        return any(ok in clean for ok in ("file", "read", "write", "create", "list", "dir", "view", "edit"))

    def execute(
        self,
        prompt: str,
        status_reporter: Optional[TurnStatusReporter] = None,
        show_status: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes a pedagogy engineering task in the shared remote environment."""
        logger.info("Executing Pedagogy Subagent -> %s", self.output_dir)
        return self._agent.execute(
            prompt=prompt,
            save_deliverables_locally=True,
            status_reporter=status_reporter,
            show_status=show_status,
        )


class LearningExperienceSubagent:
    """Specialized Learning Experience Engineering Subagent (LX).

    Attributes:
        agent_name: learning_experience_engineer
        role: Learner journey, scenes, narrative, tasks, and interaction contexts
        output_dir: outputs/learning_experience_design
        instructions: Preloaded remotely in Antigravity SDK environment
        skills: No local skills employed
    """

    def __init__(
        self,
        environment_store: EnvironmentStore,
        client_handle: Optional[InitializedClient] = None,
        turn_registry: Optional[TurnIdRegistry] = None,
        skills_dir: Union[str, Path] = "./skills",
        instructions_file: Union[str, Path, None] = "./instructions/LX-instructions.md",
        output_dir: Union[str, Path] = "./outputs/learning_experience_design",
        state_dir: Union[str, Path] = "./.3g_agent",
        brain: str = MODEL_DESIGNER,
        agent_id: Optional[str] = None,
    ) -> None:
        self.brain = brain
        self.skills_dir = Path(skills_dir)
        self.instructions_file = Path(instructions_file) if instructions_file else None
        self.output_dir = Path(output_dir)
        self.environment = environment_store
        self.state_dir = Path(state_dir)
        self.turn_registry = turn_registry or TurnIdRegistry(state_dir=self.state_dir)

        self.tools_allowed = list(FILE_ACCESS_TOOLS)
        self.tools_disabled = list(CODING_EXECUTION_TOOLS)

        resolved_agent_id = agent_id or resolve_lx_agent_id()

        self.config = ThreeGAgentConfig(
            agent_name=AGENT_LEARNING_EXPERIENCE,
            agent_id=resolved_agent_id,
            model=brain,
            brain=brain,
            skills_dir=self.skills_dir,
            instructions_file=self.instructions_file,
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
            turn_registry=self.turn_registry,
            load_local_context=False,
        )

    def is_tool_allowed(self, tool_name: str) -> bool:
        clean = tool_name.lower().strip()
        if any(bad in clean for bad in ("code", "exec", "terminal", "bash", "shell", "run")):
            return False
        return any(ok in clean for ok in ("file", "read", "write", "create", "list", "dir", "view", "edit"))

    def execute(
        self,
        prompt: str,
        status_reporter: Optional[TurnStatusReporter] = None,
        show_status: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes a learning experience engineering task in the shared remote environment."""
        logger.info("Executing Learning Experience Subagent -> %s", self.output_dir)
        return self._agent.execute(
            prompt=prompt,
            save_deliverables_locally=True,
            status_reporter=status_reporter,
            show_status=show_status,
        )


class ProductManagerSubagent:
    """Specialized Software Product Management Subagent (PM / RT).

    Attributes:
        agent_name: software_product_manager
        role: Requirements translation, PRD, component contracts, state flow, verification
        output_dir: outputs/product_requirements
        instructions: Preloaded remotely in Antigravity SDK environment
        skills: No local skills employed
    """

    def __init__(
        self,
        environment_store: EnvironmentStore,
        client_handle: Optional[InitializedClient] = None,
        turn_registry: Optional[TurnIdRegistry] = None,
        skills_dir: Union[str, Path] = "./skills",
        instructions_file: Union[str, Path, None] = "./instructions/PM-instructions.md",
        output_dir: Union[str, Path] = "./outputs/product_requirements",
        state_dir: Union[str, Path] = "./.3g_agent",
        brain: str = MODEL_BUILDER,
        agent_id: Optional[str] = None,
    ) -> None:
        self.brain = brain
        self.skills_dir = Path(skills_dir)
        self.instructions_file = Path(instructions_file) if instructions_file else None
        self.output_dir = Path(output_dir)
        self.environment = environment_store
        self.state_dir = Path(state_dir)
        self.turn_registry = turn_registry or TurnIdRegistry(state_dir=self.state_dir)

        self.tools_allowed = list(FILE_ACCESS_TOOLS) + list(CODING_EXECUTION_TOOLS)
        self.tools_disabled: List[str] = []

        resolved_agent_id = agent_id or resolve_pm_agent_id()

        self.config = ThreeGAgentConfig(
            agent_name=AGENT_PRODUCT_MANAGER,
            agent_id=resolved_agent_id,
            model=brain,
            brain=brain,
            skills_dir=self.skills_dir,
            instructions_file=self.instructions_file,
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
            turn_registry=self.turn_registry,
            load_local_context=False,
        )

    def is_tool_allowed(self, tool_name: str) -> bool:
        return True

    def execute(
        self,
        prompt: str,
        status_reporter: Optional[TurnStatusReporter] = None,
        show_status: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes a software product management / PRD task in the shared remote environment."""
        logger.info("Executing Product Manager Subagent -> %s", self.output_dir)
        return self._agent.execute(
            prompt=prompt,
            save_deliverables_locally=True,
            status_reporter=status_reporter,
            show_status=show_status,
        )


# Backward-compatible aliases
DesignerSubagent = PedagogySubagent
PedagogyEngineerSubagent = PedagogySubagent
LXSubagent = LearningExperienceSubagent
SoftwareProductManagerSubagent = ProductManagerSubagent
BuilderSubagent = ProductManagerSubagent
