"""Parent Orchestrator Agent for 3G-agent Architecture.

STRICT ARCHITECTURAL PRINCIPLES:
1. Brain (agent_config.model) = "3.1 flash lite" (gemini-3.1-flash-lite) or remote orchestrator.
2. Sole interface to the user; subagents remain internal.
3. System prompt preloaded in remote environment (instructions/orch_instruction.md).
4. Four agents: 1 Orchestrator + 3 Subagents:
   - Pedagogy Engineer Subagent (PEDA): pedagogical curricula, objectives, rubrics
   - Learning Experience Engineer Subagent (LX): learner journey, scenes, tasks, narrative
   - Software Product Manager Subagent (PM): PRD, technical contracts, data models, state flow
5. Validates subagents' outputs against user requests before returning results.
6. Subagents are lazily spun up on-demand when user need demands them.
7. All agents share the exact same remote sandbox environment (EnvironmentStore).
   Once environment id is obtained from orchestrator after first turn, it persists across turns and agents.
8. Turn ID continuity: every turn captures turn.id and saves it in TurnIdRegistry for that agent,
   ensuring conversational continuity (previous_interaction_id = previous_turn.id) for:
   - user <-> orchestrator
   - orchestrator <-> pedagogy_engineer
   - orchestrator <-> learning_experience_engineer
   - orchestrator <-> software_product_manager
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .agent import ThreeGAgent, ThreeGAgentResponse
from .config import (
    AGENT_LEARNING_EXPERIENCE,
    AGENT_ORCHESTRATOR,
    AGENT_PEDAGOGY,
    AGENT_PRODUCT_MANAGER,
    MODEL_BUILDER,
    MODEL_DESIGNER,
    MODEL_ORCHESTRATOR,
    ThreeGAgentConfig,
    canonicalize_model_name,
    resolve_lx_agent_id,
    resolve_orchestrator_agent_id,
    resolve_pedagogy_agent_id,
    resolve_pm_agent_id,
)
from .environment import EnvironmentStore
from .initializer import AgentClientInitializer, InitializedClient
from .registry import TurnIdRegistry
from .skills import SkillLoader
from .status import TurnStatusReporter
from .storage import FileStorageManager, SavedFile
from .subagents import (
    LearningExperienceSubagent,
    PedagogySubagent,
    ProductManagerSubagent,
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
    pedagogy_files: List[SavedFile] = field(default_factory=list)
    lx_files: List[SavedFile] = field(default_factory=list)
    pm_files: List[SavedFile] = field(default_factory=list)
    design_files: List[SavedFile] = field(default_factory=list)
    build_files: List[SavedFile] = field(default_factory=list)

    def get_file_links(self) -> List[str]:
        """Clickable markdown file links for saved deliverables."""
        return [f"[{f.file_name}]({f.file_uri})" for f in self.saved_files]


class ThreeGOrchestrator:
    """Parent Orchestrator Agent created with the current process.

    Coordinates the multi-agent system, lazily spinning up Pedagogy, Learning Experience,
    and Product Manager subagents only when needed, maintaining shared environment persistence
    and conversation continuity via TurnIdRegistry.
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
        agent_id: Optional[str] = None,
    ) -> None:
        self.brain = brain
        self.skills_dir = Path(skills_dir)
        self.output_dir = Path(output_dir)
        self.state_dir = Path(state_dir)
        self.subagents_dir = Path(subagents_dir)

        # Instructions resolution
        self.instructions_file = Path(instructions_file) if instructions_file else None
        if self.instructions_file and not self.instructions_file.exists():
            for alt in [
                Path("./instructions/orch_instruction.md"),
                Path("./orch_instruction.md"),
            ]:
                if alt.exists():
                    self.instructions_file = alt
                    break

        resolved_agent_id = agent_id or resolve_orchestrator_agent_id()

        # Orchestrator Configuration
        self.config = config or ThreeGAgentConfig(
            agent_name=AGENT_ORCHESTRATOR,
            agent_id=resolved_agent_id,
            model=brain,
            brain=brain,
            skills_dir=None,  # No skills employed
            instructions_file=self.instructions_file,
            output_dir=self.output_dir,
            state_dir=self.state_dir,
        )

        # Initialize SDK connection
        self.client_handle = client_handle or AgentClientInitializer.initialize(
            self.config, interactive_prompt=False
        )

        # Shared EnvironmentStore & TurnIdRegistry across all 4 agents
        self.environment = EnvironmentStore(
            state_dir=self.state_dir,
            agent_name=self.config.agent_name,
        )
        self.turn_registry = TurnIdRegistry(state_dir=self.state_dir)
        self.storage = FileStorageManager(output_dir=self.output_dir)

        # Subagent instances are None initially: lazily spun up strictly on demand
        self._pedagogy_subagent: Optional[PedagogySubagent] = None
        self._lx_subagent: Optional[LearningExperienceSubagent] = None
        self._pm_subagent: Optional[ProductManagerSubagent] = None
        self._subagent_yaml_specs: Dict[str, SubagentConfig] = {}
        self._load_yaml_specs()

        # Internal parent agent instance for user facade / synthesis
        self._agent = ThreeGAgent(
            config=self.config,
            initialized_client=self.client_handle,
            skill_loader=SkillLoader.empty(),
            environment_store=self.environment,
            storage_manager=self.storage,
            turn_registry=self.turn_registry,
            load_local_context=False,
        )

    def _load_yaml_specs(self) -> None:
        """Loads declarative YAML definitions from subagents/ directory."""
        if self.subagents_dir.exists():
            self._subagent_yaml_specs = SubagentYamlLoader.load_all(self.subagents_dir)

    # -------------------------------------------------------------------------
    # On-Demand Subagent Lifecycle Management (3 Subagents)
    # -------------------------------------------------------------------------

    def get_pedagogy_subagent(self) -> PedagogySubagent:
        """Spins up the Pedagogy Engineering Subagent strictly when needed."""
        if self._pedagogy_subagent is None:
            logger.info("Spinning up Pedagogy Subagent on demand...")
            yaml_spec = (
                self._subagent_yaml_specs.get("pedagogy_engineer")
                or self._subagent_yaml_specs.get("pedagogy")
                or self._subagent_yaml_specs.get("designer")
            )
            instr_file = (
                yaml_spec.system_instruction_file
                if yaml_spec and yaml_spec.system_instruction_file
                else Path("./instructions/PEDA-instructions.md")
            )
            out_dir = (
                yaml_spec.output_dir
                if yaml_spec and yaml_spec.output_dir
                else self.output_dir / "pedagogical_design"
            )

            self._pedagogy_subagent = PedagogySubagent(
                environment_store=self.environment,  # Shared environment
                client_handle=self.client_handle,
                turn_registry=self.turn_registry,    # Shared TurnIdRegistry
                skills_dir=self.skills_dir,
                instructions_file=instr_file,
                output_dir=out_dir,
                state_dir=self.state_dir,
                brain=yaml_spec.brain if yaml_spec and yaml_spec.brain else MODEL_DESIGNER,
                agent_id=resolve_pedagogy_agent_id(),
            )
        return self._pedagogy_subagent

    def get_learning_experience_subagent(self) -> LearningExperienceSubagent:
        """Spins up the Learning Experience Subagent strictly when needed."""
        if self._lx_subagent is None:
            logger.info("Spinning up Learning Experience Subagent on demand...")
            yaml_spec = (
                self._subagent_yaml_specs.get("learning_experience_engineer")
                or self._subagent_yaml_specs.get("learning_experience")
                or self._subagent_yaml_specs.get("lx")
            )
            instr_file = (
                yaml_spec.system_instruction_file
                if yaml_spec and yaml_spec.system_instruction_file
                else Path("./instructions/LX-instructions.md")
            )
            out_dir = (
                yaml_spec.output_dir
                if yaml_spec and yaml_spec.output_dir
                else self.output_dir / "learning_experience_design"
            )

            self._lx_subagent = LearningExperienceSubagent(
                environment_store=self.environment,  # Shared environment
                client_handle=self.client_handle,
                turn_registry=self.turn_registry,    # Shared TurnIdRegistry
                skills_dir=self.skills_dir,
                instructions_file=instr_file,
                output_dir=out_dir,
                state_dir=self.state_dir,
                brain=yaml_spec.brain if yaml_spec and yaml_spec.brain else MODEL_DESIGNER,
                agent_id=resolve_lx_agent_id(),
            )
        return self._lx_subagent

    def get_product_manager_subagent(self) -> ProductManagerSubagent:
        """Spins up the Software Product Manager Subagent strictly when needed."""
        if self._pm_subagent is None:
            logger.info("Spinning up Software Product Manager Subagent on demand...")
            yaml_spec = (
                self._subagent_yaml_specs.get("software_product_manager")
                or self._subagent_yaml_specs.get("product_manager")
                or self._subagent_yaml_specs.get("pm")
                or self._subagent_yaml_specs.get("builder")
            )
            instr_file = (
                yaml_spec.system_instruction_file
                if yaml_spec and yaml_spec.system_instruction_file
                else Path("./instructions/PM-instructions.md")
            )
            out_dir = (
                yaml_spec.output_dir
                if yaml_spec and yaml_spec.output_dir
                else self.output_dir / "product_requirements"
            )

            self._pm_subagent = ProductManagerSubagent(
                environment_store=self.environment,  # Shared environment
                client_handle=self.client_handle,
                turn_registry=self.turn_registry,    # Shared TurnIdRegistry
                skills_dir=self.skills_dir,
                instructions_file=instr_file,
                output_dir=out_dir,
                state_dir=self.state_dir,
                brain=yaml_spec.brain if yaml_spec and yaml_spec.brain else MODEL_BUILDER,
                agent_id=resolve_pm_agent_id(),
            )
        return self._pm_subagent

    # Backward compatibility accessors
    def get_designer_subagent(self) -> PedagogySubagent:
        return self.get_pedagogy_subagent()

    def get_builder_subagent(self) -> ProductManagerSubagent:
        return self.get_product_manager_subagent()

    @property
    def is_pedagogy_spun_up(self) -> bool:
        return self._pedagogy_subagent is not None

    @property
    def is_designer_spun_up(self) -> bool:
        return self.is_pedagogy_spun_up

    @property
    def is_learning_experience_spun_up(self) -> bool:
        return self._lx_subagent is not None

    @property
    def is_lx_spun_up(self) -> bool:
        return self.is_learning_experience_spun_up

    @property
    def is_product_manager_spun_up(self) -> bool:
        return self._pm_subagent is not None

    @property
    def is_builder_spun_up(self) -> bool:
        return self.is_product_manager_spun_up

    # -------------------------------------------------------------------------
    # Intent Routing & Task Handover
    # -------------------------------------------------------------------------

    def classify_intent(self, prompt: str) -> str:
        """Classifies user request into 'pedagogy', 'lx', 'pm', 'pipeline', or 'direct'."""
        lower = prompt.lower()

        is_peda = any(
            re.search(pat, lower)
            for pat in [
                r"\bpedagog", r"\bcurricul", r"\blearning objective", r"\brubric",
                r"\binstructional", r"\bsyllabus", r"\bteach", r"\btraining program",
                r"\bbloom", r"\bstage_0", r"\bstage_1",
            ]
        )

        is_lx = any(
            re.search(pat, lower)
            for pat in [
                r"\blearner experience", r"\blearning experience\b", r"\blx\b",
                r"\bnarrative\b", r"\bscene", r"\bjourney", r"\bcharacter",
                r"\bgame world", r"\bfeedback message", r"\binteraction context",
            ]
        )

        is_pm = any(
            re.search(pat, lower)
            for pat in [
                r"\bprd\b", r"\bproduct requirement", r"\bsoftware requirement",
                r"\btechnical architecture", r"\bdata model", r"\bacceptance criteria",
                r"\bfunctional requirement", r"\bbuild\b", r"\bcode\b", r"\bimplement",
                r"\bprototype\b", r"\bstate machine", r"\bgame flow",
            ]
        )

        # If user asks for full end-to-end game generator or multiple stages:
        if (is_peda and is_lx) or (is_peda and is_pm) or (is_lx and is_pm) or "full pipeline" in lower or "end-to-end" in lower:
            return "pipeline"
        elif is_peda:
            return "pedagogy"
        elif is_lx:
            return "lx"
        elif is_pm:
            return "pm"

        # Backward compatibility aliases
        if "design" in lower and not is_pm:
            return "pedagogy"
        if "build" in lower and not is_peda:
            return "pm"

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

        # Normalize agent_type
        if agent_type in ("pedagogy", "pedagogy_engineer", "designer"):
            target_dir = "outputs/pedagogical_design"
            checks["non_empty"] = len(text.strip()) > 0
            if not checks["non_empty"]:
                reasons.append("Pedagogy output text is empty")

            forbidden_code_markers = ["pygame.init()", "pygame.display", "import unity", "def run_game("]
            has_forbidden_code = any(m in text for m in forbidden_code_markers)
            checks["avoided_executable_game_code"] = not has_forbidden_code
            if has_forbidden_code:
                reasons.append("Pedagogy subagent produced forbidden executable game simulation code")

            checks["has_deliverable_or_structure"] = (
                len(files) > 0
                or any(w in text.lower() for w in ("objective", "curriculum", "rubric", "stage", "pedagog", "learning"))
            )
            if not checks["has_deliverable_or_structure"]:
                reasons.append("Pedagogy response missing pedagogical structural elements")

        elif agent_type in ("lx", "learning_experience", "learning_experience_engineer"):
            target_dir = "outputs/learning_experience_design"
            checks["non_empty"] = len(text.strip()) > 0
            if not checks["non_empty"]:
                reasons.append("Learning Experience output text is empty")

            checks["has_experience_elements"] = (
                len(files) > 0
                or any(w in text.lower() for w in ("scene", "journey", "narrative", "task", "learner", "experience"))
            )
            if not checks["has_experience_elements"]:
                reasons.append("LX response missing expected learner-experience specifications")

        elif agent_type in ("pm", "product_manager", "software_product_manager", "builder"):
            target_dir = "outputs/product_requirements"
            checks["non_empty"] = len(text.strip()) > 0
            if not checks["non_empty"]:
                reasons.append("Product Manager output text is empty")

            checks["has_prd_or_req_elements"] = (
                len(files) > 0
                or any(w in text.lower() for w in ("prd", "requirement", "functional", "acceptance", "architecture", "state", "ui"))
            )
            if not checks["has_prd_or_req_elements"]:
                reasons.append("PM response lacks PRD specifications or acceptance criteria")

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
        1. Classifies user requirement (pedagogy, lx, pm, pipeline, or direct).
        2. Lazily spins up demanded subagents.
        3. Executes subagents sharing the exact same EnvironmentStore container.
        4. Maintains per-agent conversational continuity via TurnIdRegistry.
        5. Validates subagent outputs against user constraints.
        6. Synthesizes and delivers verified results to the user with clickable file links.
        """
        reporter = status_reporter or TurnStatusReporter(enabled=show_status)
        reporter.start("Orchestrating", "Analyzing user request and coordinating agents...")

        task_type = force_task_type or self.classify_intent(prompt)
        logger.info("Orchestrator identified task type: '%s' for prompt: %.50s...", task_type, prompt)

        delegated_to: List[str] = []
        validations: List[ValidationResult] = []
        all_saved_files: List[SavedFile] = []
        pedagogy_files: List[SavedFile] = []
        lx_files: List[SavedFile] = []
        pm_files: List[SavedFile] = []
        final_text_parts: List[str] = []

        active_env_id = self.environment.get_environment_id() or "env_shared"

        # -------------------------------------------------------------
        # Branch 1: PEDAGOGY Task
        # -------------------------------------------------------------
        if task_type in ("pedagogy", "design"):
            delegated_to.append(AGENT_PEDAGOGY)
            reporter.thinking("Delegating to Pedagogy Engineer Subagent (PEDA)...")
            pedagogy = self.get_pedagogy_subagent()
            resp = pedagogy.execute(prompt=prompt, status_reporter=reporter, show_status=show_status)

            val = self.validate_output(prompt, resp, "pedagogy")
            validations.append(val)
            active_env_id = resp.environment_id or active_env_id
            pedagogy_files.extend(resp.saved_files)
            all_saved_files.extend(resp.saved_files)
            final_text_parts.append(resp.output_text)

        # -------------------------------------------------------------
        # Branch 2: LEARNING EXPERIENCE (LX) Task
        # -------------------------------------------------------------
        elif task_type in ("lx", "learning_experience"):
            delegated_to.append(AGENT_LEARNING_EXPERIENCE)
            reporter.thinking("Delegating to Learning Experience Subagent (LX)...")
            lx = self.get_learning_experience_subagent()
            resp = lx.execute(prompt=prompt, status_reporter=reporter, show_status=show_status)

            val = self.validate_output(prompt, resp, "lx")
            validations.append(val)
            active_env_id = resp.environment_id or active_env_id
            lx_files.extend(resp.saved_files)
            all_saved_files.extend(resp.saved_files)
            final_text_parts.append(resp.output_text)

        # -------------------------------------------------------------
        # Branch 3: PRODUCT MANAGER (PM / RT) Task
        # -------------------------------------------------------------
        elif task_type in ("pm", "product_manager", "build"):
            delegated_to.append(AGENT_PRODUCT_MANAGER)
            reporter.thinking("Delegating to Software Product Manager Subagent (PM)...")
            pm = self.get_product_manager_subagent()
            resp = pm.execute(prompt=prompt, status_reporter=reporter, show_status=show_status)

            val = self.validate_output(prompt, resp, "pm")
            validations.append(val)
            active_env_id = resp.environment_id or active_env_id
            pm_files.extend(resp.saved_files)
            all_saved_files.extend(resp.saved_files)
            final_text_parts.append(resp.output_text)

        # -------------------------------------------------------------
        # Branch 4: FULL PIPELINE (PEDA -> LX -> PM)
        # -------------------------------------------------------------
        elif task_type in ("pipeline", "hybrid"):
            # Step 1: Pedagogy Engineer
            delegated_to.append(AGENT_PEDAGOGY)
            reporter.thinking("[1/3] Step 1: Pedagogy Engineer Subagent (PEDA)...")
            pedagogy = self.get_pedagogy_subagent()
            peda_resp = pedagogy.execute(
                prompt=f"Create complete pedagogical curriculum specification for: {prompt}",
                status_reporter=reporter,
                show_status=show_status,
            )
            val_peda = self.validate_output(prompt, peda_resp, "pedagogy")
            validations.append(val_peda)
            pedagogy_files.extend(peda_resp.saved_files)
            all_saved_files.extend(peda_resp.saved_files)
            active_env_id = peda_resp.environment_id or active_env_id

            # Step 2: Learning Experience Engineer
            delegated_to.append(AGENT_LEARNING_EXPERIENCE)
            reporter.thinking("[2/3] Step 2: Learning Experience Subagent (LX)...")
            lx = self.get_learning_experience_subagent()
            lx_prompt = (
                f"Design the complete Learner-Experience Specification based on the pedagogical plan.\n\n"
                f"User Request: {prompt}\n\n"
                f"Pedagogical Plan:\n{peda_resp.output_text[:3000]}"
            )
            lx_resp = lx.execute(
                prompt=lx_prompt,
                status_reporter=reporter,
                show_status=show_status,
            )
            val_lx = self.validate_output(prompt, lx_resp, "lx")
            validations.append(val_lx)
            lx_files.extend(lx_resp.saved_files)
            all_saved_files.extend(lx_resp.saved_files)
            active_env_id = lx_resp.environment_id or active_env_id

            # Step 3: Software Product Manager
            delegated_to.append(AGENT_PRODUCT_MANAGER)
            reporter.thinking("[3/3] Step 3: Software Product Manager Subagent (PM)...")
            pm = self.get_product_manager_subagent()
            pm_prompt = (
                f"Produce implementation-ready Software Product Requirements Document (PRD).\n\n"
                f"User Request: {prompt}\n\n"
                f"Learner-Experience Specification:\n{lx_resp.output_text[:3000]}"
            )
            pm_resp = pm.execute(
                prompt=pm_prompt,
                status_reporter=reporter,
                show_status=show_status,
            )
            val_pm = self.validate_output(prompt, pm_resp, "pm")
            validations.append(val_pm)
            pm_files.extend(pm_resp.saved_files)
            all_saved_files.extend(pm_resp.saved_files)
            active_env_id = pm_resp.environment_id or active_env_id

            final_text_parts.append("### 1. Pedagogical Architecture (PEDA Subagent)")
            final_text_parts.append(peda_resp.output_text)
            final_text_parts.append("\n---\n### 2. Learner-Experience Specification (LX Subagent)")
            final_text_parts.append(lx_resp.output_text)
            final_text_parts.append("\n---\n### 3. Software Engineering PRD (PM Subagent)")
            final_text_parts.append(pm_resp.output_text)

        # -------------------------------------------------------------
        # Branch 5: DIRECT Query (Handled directly by Orchestrator)
        # -------------------------------------------------------------
        else:
            delegated_to.append(AGENT_ORCHESTRATOR)
            reporter.thinking("Resolving query directly via Orchestrator...")
            orch_resp = self._agent.execute(prompt=prompt, status_reporter=reporter, show_status=show_status)
            active_env_id = orch_resp.environment_id or active_env_id
            all_saved_files.extend(orch_resp.saved_files)
            final_text_parts.append(orch_resp.output_text)

        # Deliverable links section
        if all_saved_files:
            file_sections: List[str] = ["\n\n### Verified Deliverables"]
            if pedagogy_files:
                file_sections.append("**Pedagogy Deliverables (`outputs/pedagogical_design`):**")
                for f in pedagogy_files:
                    file_sections.append(f"- [{f.file_name}]({f.file_uri}) ({f.size_bytes} bytes)")
            if lx_files:
                file_sections.append("**Learning Experience Deliverables (`outputs/learning_experience_design`):**")
                for f in lx_files:
                    file_sections.append(f"- [{f.file_name}]({f.file_uri}) ({f.size_bytes} bytes)")
            if pm_files:
                file_sections.append("**Product Management Deliverables (`outputs/product_requirements`):**")
                for f in pm_files:
                    file_sections.append(f"- [{f.file_name}]({f.file_uri}) ({f.size_bytes} bytes)")
            final_text_parts.append("\n".join(file_sections))

        reporter.complete(f"Task completed ({task_type}) across {len(delegated_to)} agent(s)")

        return OrchestratorResponse(
            output_text="\n\n".join(final_text_parts),
            environment_id=active_env_id,
            task_type=task_type,
            delegated_to=delegated_to,
            validations=validations,
            saved_files=all_saved_files,
            pedagogy_files=pedagogy_files,
            lx_files=lx_files,
            pm_files=pm_files,
            design_files=pedagogy_files,
            build_files=pm_files,
        )
