"""Parent Orchestrator Agent for 3G-agent Architecture.

STRICT ARCHITECTURAL PRINCIPLES:
1. Brain (agent_config.model) = "3.1 flash lite" (gemini-3.1-flash-lite).
2. Sole interface to the user; subagents remain internal.
3. System prompt loaded from common directory (instructions/orch_instruction.md) in ANIR.
4. Validates other agents' outputs against user requests before returning results.
5. Hands over specific tasks to agents based on user requests.
6. Subagents (designer and builder) are only spun up on-demand when user need demands them.
7. All 3 agents share the exact same remote sandbox environment (EnvironmentStore).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .agent import ThreeGAgent, ThreeGAgentResponse
from .config import (
    MODEL_BUILDER,
    MODEL_DESIGNER,
    MODEL_ORCHESTRATOR,
    ThreeGAgentConfig,
    canonicalize_model_name,
)
from .environment import EnvironmentStore
from .initializer import AgentClientInitializer, InitializedClient
from .skills import SkillLoader
from .status import TurnStatusReporter
from .storage import FileStorageManager, SavedFile
from .subagents import (
    BuilderSubagent,
    DesignerSubagent,
    SubagentConfig,
    SubagentYamlLoader,
)

logger = logging.getLogger("3G-agent.orchestrator")


@dataclass
class ValidationResult:
    """Result of orchestrator output validation against user requests."""
    is_valid: bool
    agent_name: str
    target_dir: str
    checks: Dict[str, bool] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    saved_files: List[SavedFile] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASSED" if self.is_valid else "FAILED"
        return f"[{status}] Validation for {self.agent_name} -> {'; '.join(self.reasons) or 'All criteria satisfied'}"


@dataclass
class OrchestratorResponse:
    """Encapsulates the consolidated response from the Orchestrator."""
    output_text: str
    environment_id: str
    task_type: str
    delegated_to: List[str]
    validations: List[ValidationResult] = field(default_factory=list)
    saved_files: List[SavedFile] = field(default_factory=list)
    design_files: List[SavedFile] = field(default_factory=list)
    build_files: List[SavedFile] = field(default_factory=list)

    def get_file_links(self) -> List[str]:
        """Clickable markdown file links for saved deliverables."""
        return [f"[{f.file_name}]({f.file_uri})" for f in self.saved_files]


class ThreeGOrchestrator:
    """Parent Orchestrator Agent created with the current process.
    
    Coordinates the multi-agent system, lazily spinning up Designer and Builder
    subagents only when the user's need demands them, and validating their outputs.
    """

    def __init__(
        self,
        config: Optional[ThreeGAgentConfig] = None,
        client_handle: Optional[InitializedClient] = None,
        skills_dir: Union[str, Path] = "./skills",
        instructions_file: Union[str, Path, None] = "./instructions/orch_instruction.md",
        subagents_dir: Union[str, Path] = "./subagents",
        output_dir: Union[str, Path] = "./outputs",
        state_dir: Union[str, Path] = "./.3g_agent",
        brain: str = MODEL_ORCHESTRATOR,
    ) -> None:
        self.brain = brain
        self.skills_dir = Path(skills_dir)
        self.output_dir = Path(output_dir)
        self.state_dir = Path(state_dir)
        self.subagents_dir = Path(subagents_dir)

        # Common instructions resolution (strictly within /instructions directory)
        self.instructions_file = Path(instructions_file) if instructions_file else None
        if self.instructions_file and not self.instructions_file.exists():
            alt = Path("./instructions/orch_instruction.md")
            if alt.exists():
                self.instructions_file = alt


        # Orchestrator Configuration: brain = 3.1 flash lite
        self.config = config or ThreeGAgentConfig(
            agent_name="3G-orchestrator",
            agent_id=canonicalize_model_name(brain),
            model=brain,
            brain=brain,
            skills_dir=None,  # Only designer agent needs custom skills
            instructions_file=self.instructions_file,
            output_dir=self.output_dir,
            state_dir=self.state_dir,
        )

        # Initialize SDK connection
        self.client_handle = client_handle or AgentClientInitializer.initialize(
            self.config, interactive_prompt=False
        )

        # All 3 agents share the exact same EnvironmentStore & remote environment_id
        self.environment = EnvironmentStore(
            state_dir=self.state_dir,
            agent_name=self.config.agent_name,
        )

        self.storage = FileStorageManager(output_dir=self.output_dir)

        # Subagent instances are None initially: lazily spun up strictly on demand
        self._designer_subagent: Optional[DesignerSubagent] = None
        self._builder_subagent: Optional[BuilderSubagent] = None
        self._subagent_yaml_specs: Dict[str, SubagentConfig] = {}
        self._load_yaml_specs()

        # Internal parent agent instance for direct queries / synthesis
        self._agent = ThreeGAgent(
            config=self.config,
            initialized_client=self.client_handle,
            skill_loader=SkillLoader.empty(),
            environment_store=self.environment,
            storage_manager=self.storage,
            load_local_context=True,
        )

    def _load_yaml_specs(self) -> None:
        """Loads declarative YAML definitions from subagents/ directory."""
        if self.subagents_dir.exists():
            self._subagent_yaml_specs = SubagentYamlLoader.load_all(self.subagents_dir)

    # -------------------------------------------------------------------------
    # On-Demand Subagent Lifecycle Management
    # -------------------------------------------------------------------------

    def get_designer_subagent(self) -> DesignerSubagent:
        """Spins up the Designer Subagent strictly when educational design is needed."""
        if self._designer_subagent is None:
            logger.info("Spinting up Designer Subagent on demand (brain: %s)...", MODEL_DESIGNER)
            desi_yaml = self._subagent_yaml_specs.get("designer")
            instr_file = desi_yaml.system_instruction_file if desi_yaml else Path("./instructions/desi_instructions.md")
            skills_dir = desi_yaml.skills_dir if desi_yaml and desi_yaml.skills_dir else self.skills_dir
            out_dir = desi_yaml.output_dir if desi_yaml else self.output_dir / "design"

            self._designer_subagent = DesignerSubagent(
                environment_store=self.environment,  # Shared environment
                client_handle=self.client_handle,
                skills_dir=skills_dir,
                instructions_file=instr_file,
                output_dir=out_dir,
                state_dir=self.state_dir,
                brain=desi_yaml.brain if desi_yaml else MODEL_DESIGNER,
            )
        return self._designer_subagent

    def get_builder_subagent(self) -> BuilderSubagent:
        """Spins up the Builder Subagent strictly when it is time to build."""
        if self._builder_subagent is None:
            logger.info("Spinning up Builder Subagent on demand (brain: %s)...", MODEL_BUILDER)
            build_yaml = self._subagent_yaml_specs.get("builder")
            out_dir = build_yaml.output_dir if build_yaml else self.output_dir / "build"

            self._builder_subagent = BuilderSubagent(
                environment_store=self.environment,  # Shared environment
                client_handle=self.client_handle,
                output_dir=out_dir,
                state_dir=self.state_dir,
                brain=build_yaml.brain if build_yaml else MODEL_BUILDER,
            )
        return self._builder_subagent

    @property
    def is_designer_spun_up(self) -> bool:
        """Returns True if the designer subagent has been created in this process."""
        return self._designer_subagent is not None

    @property
    def is_builder_spun_up(self) -> bool:
        """Returns True if the builder subagent has been created in this process."""
        return self._builder_subagent is not None

    # -------------------------------------------------------------------------
    # Intent Routing & Task Handover
    # -------------------------------------------------------------------------

    def classify_intent(self, prompt: str) -> str:
        """Classifies user request into 'design', 'build', 'hybrid', or 'direct'."""
        lower = prompt.lower()

        # Pedagogical / design markers
        design_patterns = [
            r"\bpedagog",
            r"\bcurricul",
            r"\blearning objective",
            r"\blesson plan",
            r"\brubric",
            r"\binstructional",
            r"\bstage\s*[0-4]\b",
            r"\bsyllabus",
            r"\bteach",
            r"\btraining program",
            r"\beducation",
        ]
        has_design = any(re.search(pat, lower) for pat in design_patterns)

        # Code / build markers
        build_patterns = [
            r"\bcode\b",
            r"\bbuild\b",
            r"\bimplement",
            r"\bpython\s*(?:script|code|file)",
            r"\bprototype\b",
            r"\brun(?:nable)?\b",
            r"\bprogram\b",
            r"\bscript\b",
            r"\bconstruct\b",
            r"\bcompile\b",
            r"\bexecution\b",
        ]
        has_build = any(re.search(pat, lower) for pat in build_patterns)

        if has_design and has_build:
            return "hybrid"
        elif has_design:
            return "design"
        elif has_build:
            return "build"
        return "direct"

    # -------------------------------------------------------------------------
    # Output Validation against User Requests
    # -------------------------------------------------------------------------

    def validate_output(
        self,
        user_prompt: str,
        subagent_response: ThreeGAgentResponse,
        agent_type: str,
    ) -> ValidationResult:
        """Validates a subagent's output text and deliverables against user requests."""
        checks: Dict[str, bool] = {}
        reasons: List[str] = []
        text = subagent_response.output_text or ""
        files = subagent_response.saved_files

        if agent_type == "designer":
            target_dir = "outputs/design"
            # 1. Output non-empty
            checks["non_empty"] = len(text.strip()) > 0
            if not checks["non_empty"]:
                reasons.append("Designer output text is empty")

            # 2. Files saved to outputs/design
            checks["saved_to_design_dir"] = all(
                "design" in str(f.local_path).replace("\\", "/") for f in files
            ) if files else True
            if not checks["saved_to_design_dir"]:
                reasons.append("Deliverables were not saved to outputs/design directory")

            # 3. Adherence to non-executable policy (no game engine or executable code)
            forbidden_code_markers = ["pygame.init()", "pygame.display", "import unity", "def run_game("]
            has_forbidden_code = any(m in text for m in forbidden_code_markers)
            checks["avoided_executable_game_code"] = not has_forbidden_code
            if has_forbidden_code:
                reasons.append("Designer produced forbidden executable game simulation code")

            # 4. Contains pedagogical structures if requested
            if any(k in user_prompt.lower() for k in ("objective", "curriculum", "rubric", "plan")):
                checks["pedagogical_content"] = any(
                    w in text.lower() for w in ("objective", "curriculum", "rubric", "stage", "pedagog", "learning")
                )
                if not checks["pedagogical_content"]:
                    reasons.append("Designer response missing requested pedagogical structural elements")

        elif agent_type == "builder":
            target_dir = "outputs/build"
            # 1. Output non-empty
            checks["non_empty"] = len(text.strip()) > 0
            if not checks["non_empty"]:
                reasons.append("Builder output text is empty")

            # 2. Files saved to outputs/build
            checks["saved_to_build_dir"] = all(
                "build" in str(f.local_path).replace("\\", "/") for f in files
            ) if files else True
            if not checks["saved_to_build_dir"]:
                reasons.append("Deliverables were not saved to outputs/build directory")

            # 3. Code deliverables check
            if any(k in user_prompt.lower() for k in ("code", "python", "script", "prototype", "implement")):
                checks["contains_code_deliverable"] = (
                    len(files) > 0 or "```python" in text or "```" in text or "def " in text or "class " in text
                )
                if not checks["contains_code_deliverable"]:
                    reasons.append("Builder output lacks code implementation or executable deliverables")

        else:
            target_dir = "outputs"
            checks["non_empty"] = len(text.strip()) > 0

        is_valid = all(checks.values()) if checks else True
        return ValidationResult(
            is_valid=is_valid,
            agent_name=agent_type,
            target_dir=target_dir,
            checks=checks,
            reasons=reasons,
            saved_files=files,
        )

    # -------------------------------------------------------------------------
    # Core Execution & Turn Orchestration
    # -------------------------------------------------------------------------

    def execute(
        self,
        prompt: str,
        force_task_type: Optional[str] = None,
        status_reporter: Optional[TurnStatusReporter] = None,
        show_status: bool = True,
    ) -> OrchestratorResponse:
        """Executes a user request through the multi-agent architecture.
        
        Orchestration Steps:
        1. Classifies user requirement (design, build, hybrid, or direct).
        2. Lazily spins up the demanded subagent (designer or builder).
        3. Executes the subagent operation using the shared environment container.
        4. Validates the subagent output against user constraints.
        5. Synthesizes and delivers verified results to the user with local file links.
        """
        reporter = status_reporter or TurnStatusReporter(enabled=show_status)
        reporter.start("Orchestrating", "Analyzing user request and coordinating agents...")

        task_type = force_task_type or self.classify_intent(prompt)
        logger.info("Orchestrator identified task type: '%s' for prompt: %.50s...", task_type, prompt)

        delegated_to: List[str] = []
        validations: List[ValidationResult] = []
        all_saved_files: List[SavedFile] = []
        design_files: List[SavedFile] = []
        build_files: List[SavedFile] = []
        final_text_parts: List[str] = []

        active_env_id = self.environment.get_environment_id() or "env_shared"

        # -------------------------------------------------------------
        # Branch 1: DESIGN Task
        # -------------------------------------------------------------
        if task_type == "design":
            delegated_to.append("designer")
            reporter.thinking("Delegating pedagogical design to Designer Subagent (3.5 flash lite)...")
            designer = self.get_designer_subagent()
            desi_resp = designer.execute(prompt=prompt, status_reporter=reporter, show_status=show_status)

            # Validate designer output
            val = self.validate_output(prompt, desi_resp, "designer")
            validations.append(val)
            active_env_id = desi_resp.environment_id or active_env_id
            design_files.extend(desi_resp.saved_files)
            all_saved_files.extend(desi_resp.saved_files)

            final_text_parts.append(desi_resp.output_text)
            if not val.is_valid:
                logger.warning("Designer validation note: %s", val.summary())

        # -------------------------------------------------------------
        # Branch 2: BUILD Task
        # -------------------------------------------------------------
        elif task_type == "build":
            delegated_to.append("builder")
            reporter.thinking("Delegating code construction to Builder Subagent (3.8 flash)...")
            builder = self.get_builder_subagent()
            build_resp = builder.execute(prompt=prompt, status_reporter=reporter, show_status=show_status)

            # Validate builder output
            val = self.validate_output(prompt, build_resp, "builder")
            validations.append(val)
            active_env_id = build_resp.environment_id or active_env_id
            build_files.extend(build_resp.saved_files)
            all_saved_files.extend(build_resp.saved_files)

            final_text_parts.append(build_resp.output_text)
            if not val.is_valid:
                logger.warning("Builder validation note: %s", val.summary())

        # -------------------------------------------------------------
        # Branch 3: HYBRID Task (Design First -> Then Build)
        # -------------------------------------------------------------
        elif task_type == "hybrid":
            # Step A: Designer
            delegated_to.append("designer")
            reporter.thinking("[1/2] Handing pedagogical design to Designer Subagent (3.5 flash lite)...")
            designer = self.get_designer_subagent()
            desi_resp = designer.execute(
                prompt=f"Create complete pedagogical curriculum specification for: {prompt}",
                status_reporter=reporter,
                show_status=show_status,
            )
            val_desi = self.validate_output(prompt, desi_resp, "designer")
            validations.append(val_desi)
            design_files.extend(desi_resp.saved_files)
            all_saved_files.extend(desi_resp.saved_files)
            active_env_id = desi_resp.environment_id or active_env_id

            # Step B: Builder (Called only when it is time to build)
            delegated_to.append("builder")
            reporter.thinking("[2/2] Handing implementation to Builder Subagent (3.8 flash)...")
            builder = self.get_builder_subagent()
            build_prompt = (
                f"Implement executable software components based on the verified design specifications.\n\n"
                f"Original User Request: {prompt}\n\n"
                f"Design Specification:\n{desi_resp.output_text[:2000]}"
            )
            build_resp = builder.execute(
                prompt=build_prompt,
                status_reporter=reporter,
                show_status=show_status,
            )
            val_build = self.validate_output(prompt, build_resp, "builder")
            validations.append(val_build)
            build_files.extend(build_resp.saved_files)
            all_saved_files.extend(build_resp.saved_files)
            active_env_id = build_resp.environment_id or active_env_id

            final_text_parts.append("### Pedagogical Design Specifications (Designer Subagent - 3.5 flash lite)")
            final_text_parts.append(desi_resp.output_text)
            final_text_parts.append("\n---\n### Executable Implementation (Builder Subagent - 3.8 flash)")
            final_text_parts.append(build_resp.output_text)

        # -------------------------------------------------------------
        # Branch 4: DIRECT Query (Handled directly by Orchestrator)
        # -------------------------------------------------------------
        else:
            delegated_to.append("orchestrator")
            reporter.thinking("Resolving query directly via Orchestrator (3.1 flash lite)...")
            orch_resp = self._agent.execute(prompt=prompt, status_reporter=reporter, show_status=show_status)
            active_env_id = orch_resp.environment_id or active_env_id
            all_saved_files.extend(orch_resp.saved_files)
            final_text_parts.append(orch_resp.output_text)

        # -------------------------------------------------------------
        # Append Deliverable Links & Validation Badges
        # -------------------------------------------------------------
        if all_saved_files:
            file_sections: List[str] = ["\n\n### Verified Deliverables"]
            if design_files:
                file_sections.append("**Design Deliverables (`outputs/design`):**")
                for df in design_files:
                    file_sections.append(f"- [{df.file_name}]({df.file_uri}) ({df.size_bytes} bytes)")
            if build_files:
                file_sections.append("**Build Deliverables (`outputs/build`):**")
                for bf in build_files:
                    file_sections.append(f"- [{bf.file_name}]({bf.file_uri}) ({bf.size_bytes} bytes)")
            final_text_parts.append("\n".join(file_sections))

        reporter.complete(f"Task completed ({task_type}) across {len(delegated_to)} agent(s)")

        return OrchestratorResponse(
            output_text="\n\n".join(final_text_parts),
            environment_id=active_env_id,
            task_type=task_type,
            delegated_to=delegated_to,
            validations=validations,
            saved_files=all_saved_files,
            design_files=design_files,
            build_files=build_files,
        )
