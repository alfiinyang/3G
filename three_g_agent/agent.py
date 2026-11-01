"""3G-agent: Custom Reusable Antigravity Agent.

Core Execution Engine strictly decoupled from initialization and parameter collection.

Features:
- Configured with remote execution environment (`environment="remote"`).
- Automatically mounts skills from a folder (`.agents/skills/...`).
- Securely stores and reuses the remote `environment_id` across turns.
- Downloads and guarantees local file accessibility for all agent outputs.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .config import ClientParameterCollector, ThreeGAgentConfig
from .deletion import AgentDeletionManager, DeletionResult
from .environment import EnvironmentStore
from .initializer import InitializedClient, ModelInitializer
from .registry import AgentRegistry, ConversationSession
from .skills import Skill, SkillLoader
from .status import TurnStatusReporter
from .storage import FileStorageManager, SavedFile

logger = logging.getLogger("3G-agent")


@dataclass
class ThreeGAgentResponse:
    """Encapsulates the response from a 3G-agent execution turn.
    
    Attributes:
        output_text: Text response or deliverable from the agent.
        environment_id: The remote environment container ID used/persisted.
        interaction_id: Unique interaction ID for multi-turn history.
        session_id: The conversation session ID holding this environment state.
        saved_files: List of files created by the agent and saved locally.
        raw_interaction: The underlying raw interaction object from SDK.
    """
    output_text: str
    environment_id: str
    interaction_id: Optional[str] = None
    session_id: Optional[str] = None
    saved_files: List[SavedFile] = field(default_factory=list)
    raw_interaction: Any = None

    def get_file_links(self) -> List[str]:
        """Returns a list of clickable markdown file links for saved deliverables."""
        return [f"[{f.file_name}]({f.file_uri})" for f in self.saved_files]


def extract_interaction_text(interaction: Any, fallback_streamed: Optional[str] = None) -> str:
    """Extracts strictly the human-readable text response from an Antigravity Interaction object.
    
    Prevents leaking raw API structures, JSON payloads, or Python object representations
    (e.g., `Interaction(...)` or `InteractionSseEventInteraction(...)`).
    """
    if interaction is None:
        return (fallback_streamed or "").strip()

    if isinstance(interaction, str):
        return interaction.strip()

    # 1. Direct output_text attribute or dict key
    direct_out = getattr(interaction, "output_text", None)
    if direct_out is None and isinstance(interaction, dict):
        direct_out = interaction.get("output_text")
    if isinstance(direct_out, str) and direct_out.strip():
        return direct_out.strip()

    # 2. Extract from steps (Google GenAI Interaction / InteractionSseEventInteraction)
    steps = getattr(interaction, "steps", None)
    if steps is None and isinstance(interaction, dict):
        steps = interaction.get("steps")

    if steps and isinstance(steps, (list, tuple)):
        text_parts: List[str] = []
        for step in steps:
            step_type = getattr(step, "type", None)
            if step_type is None and isinstance(step, dict):
                step_type = step.get("type")

            # Only model_output contains the agent's textual response to the user
            if str(step_type) in ("model_output", "output", "model"):
                content = getattr(step, "content", None)
                if content is None and isinstance(step, dict):
                    content = step.get("content")

                if isinstance(content, list):
                    for item in content:
                        item_text = getattr(item, "text", None)
                        if item_text is None and isinstance(item, dict):
                            item_text = item.get("text")
                        if isinstance(item_text, str) and item_text:
                            text_parts.append(item_text)
                elif isinstance(content, str) and content.strip():
                    text_parts.append(content)
                elif hasattr(step, "text") and isinstance(step.text, str) and step.text.strip():
                    text_parts.append(step.text)

        if text_parts:
            return "".join(text_parts).strip()

    # 3. Direct text property or output property if string
    for attr in ("text", "output", "content", "response"):
        val = getattr(interaction, attr, None)
        if val is None and isinstance(interaction, dict):
            val = interaction.get(attr)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # 4. Standard Gemini GenerateContent response (candidates -> content -> parts -> text)
    candidates = getattr(interaction, "candidates", None)
    if candidates is None and isinstance(interaction, dict):
        candidates = interaction.get("candidates")
    if isinstance(candidates, list) and candidates:
        first_cand = candidates[0]
        content = getattr(first_cand, "content", None) or (first_cand.get("content") if isinstance(first_cand, dict) else None)
        if content:
            parts = getattr(content, "parts", None) or (content.get("parts") if isinstance(content, dict) else None)
            if isinstance(parts, list):
                cand_texts = []
                for p in parts:
                    t = getattr(p, "text", None) or (p.get("text") if isinstance(p, dict) else None)
                    if isinstance(t, str):
                        cand_texts.append(t)
                if cand_texts:
                    return "".join(cand_texts).strip()

    # 5. Check fallback streamed chunks accumulated during event streaming
    if fallback_streamed and fallback_streamed.strip():
        return fallback_streamed.strip()

    # 6. Fallback: Return empty string instead of dumping the raw API object repr
    return ""


class ThreeGAgent:
    """The reusable 3G-agent.
    
    Separates parameter collection and client initialization from runtime execution.
    """

    def __init__(
        self,
        config: ThreeGAgentConfig,
        initialized_client: InitializedClient,
        skill_loader: SkillLoader,
        environment_store: EnvironmentStore,
        storage_manager: FileStorageManager,
        registry: Optional[AgentRegistry] = None,
        load_local_context: bool = True,
    ) -> None:
        """Initializes 3G-agent with pre-configured and pre-initialized dependencies.

        load_local_context: If False (existing custom remote agent), local skills and
        instructions are never read or uploaded; the agent's persisted remote
        base_environment is used instead.
        """
        self.config = config
        self.client_handle = initialized_client
        self.client = initialized_client.client
        self.skills = skill_loader
        self.environment = environment_store
        self.storage = storage_manager
        self.registry = registry or AgentRegistry(state_dir=config.state_dir)
        self.load_local_context = load_local_context
        self.active_session_id: Optional[str] = None
        self.last_interaction_id: Optional[str] = None


    @classmethod
    def create(
        cls,
        skills_dir: Union[str, Path] = "./skills",
        agent_id: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        state_dir: Union[str, Path] = "./.3g_agent",
        output_dir: Union[str, Path] = "./outputs/3g_agent",
        instructions_file: Union[str, Path, None] = "./instructions.md",
        vertex_ai: bool = False,
        project: Optional[str] = None,
        location: Optional[str] = None,
        system_instruction_override: Optional[str] = None,
        load_local_context: Optional[bool] = None,
    ) -> ThreeGAgent:
        """Factory method to assemble 3G-agent while maintaining clean separation of concerns.
        
        1. Parameter Collection: Collects and validates parameters (including instructions.md).
        2. Client Initialization: Creates the client connection targeting the Antigravity agent.
        3. Skill Discovery: Loads skills from the designated folder.
        4. Environment Store: Prepares secure remote environment tracking.
        5. Storage Manager: Prepares local file accessibility infrastructure.
        """
        # Resolve target agent (not model)
        target_agent = agent_id or model_name
        if not target_agent or target_agent.strip() in ("1", "0", "true", "false", "yes", "no"):
            from .config import resolve_default_agent_id
            target_agent = resolve_default_agent_id()

        # Step 1: Collect parameters
        config = ThreeGAgentConfig(
            agent_name="3G-agent",
            agent_id=target_agent,
            environment_type="remote",  # Mandatory: remote environment
            api_key=api_key,
            skills_dir=Path(skills_dir),
            state_dir=Path(state_dir),
            output_dir=Path(output_dir),
            instructions_file=Path(instructions_file) if instructions_file else None,
            vertex_ai=vertex_ai,
            project=project,
            location=location,
            system_instruction_override=system_instruction_override,
        )
        # Existing custom agents (created via client.agents.create) already hold their
        # skills + instructions in their remote base_environment: never reload locally.
        from .config import is_base_agent_id
        if load_local_context is None:
            load_local_context = is_base_agent_id(target_agent)

        ClientParameterCollector.validate(config, require_skills_dir=load_local_context)

        # Step 2: Separate Client Initialization
        initialized_client = ModelInitializer.initialize(config)

        # Step 3: Skill Discovery & Packaging (only for stock base engines)
        if load_local_context:
            skill_loader = SkillLoader(config.skills_dir)
        else:
            skill_loader = SkillLoader.empty()
            logger.info(
                "Agent '%s' is an existing remote agent: using skills/instructions persisted "
                "in its remote environment (local files are not loaded).",
                target_agent,
            )

        # Step 4: Secure Environment Store
        environment_store = EnvironmentStore(
            state_dir=config.state_dir,
            agent_name=config.agent_name,
        )

        # Step 5: File Storage & Local Accessibility Manager
        storage_manager = FileStorageManager(output_dir=config.output_dir)

        # Step 6: Agent & Session Registry
        registry = AgentRegistry(state_dir=config.state_dir)

        # Step 7: Return the assembled 3G-agent
        return cls(
            config=config,
            initialized_client=initialized_client,
            skill_loader=skill_loader,
            environment_store=environment_store,
            storage_manager=storage_manager,
            registry=registry,
            load_local_context=load_local_context,
        )

    def execute(
        self,
        prompt: str,
        force_fresh_environment: bool = False,
        additional_sources: Optional[List[Dict[str, Any]]] = None,
        save_deliverables_locally: bool = True,
        status_reporter: Optional[TurnStatusReporter] = None,
        show_status: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes an operation in the remote Antigravity sandbox with real-time status reporting.
        
        Args:
            prompt: User instructions or query for the agent.
            force_fresh_environment: If True, ignores previous environment ID and starts a fresh container.
            additional_sources: Optional extra inline files or data to mount.
            save_deliverables_locally: Whether to automatically extract and save generated files locally.
            status_reporter: Optional custom status reporter instance.
            show_status: Whether to display dynamic terminal status updates while waiting.
            
        Returns:
            ThreeGAgentResponse with output text, environment ID, and local saved file links.
        """
        logger.info("Executing 3G-agent turn...")
        reporter = status_reporter or TurnStatusReporter(enabled=show_status)
        reporter.start("Thinking", "Analyzing prompt...")

        # 1. Prepare remote sources. Local skills & instructions are only used for
        #    stock base engines; existing custom agents use their persisted remote env.
        remote_sources: List[Dict[str, Any]] = []
        system_instructions: Optional[str] = None
        if self.load_local_context:
            skill_names = [s.name for s in self.skills.skills]
            if skill_names:
                reporter.skill_use(", ".join(skill_names))
            remote_sources = self.skills.build_remote_sources()

            system_instructions = self.config.load_instructions()
            if system_instructions:
                remote_sources.append({
                    "type": "inline",
                    "target": ".agents/instructions.md",
                    "content": system_instructions,
                })
                remote_sources.append({
                    "type": "inline",
                    "target": ".agents/AGENTS.md",
                    "content": system_instructions,
                })
                logger.info("Loaded system prompt from instructions file into remote environment sources.")
        if additional_sources:
            remote_sources.extend(additional_sources)

        # 2. Build remote environment payload (reuses existing environment_id if active)
        active_env_id = self.environment.get_environment_id()
        if active_env_id and not force_fresh_environment:
            reporter.environment(f"Reusing remote sandbox ({active_env_id[:18]}...)")
        else:
            reporter.environment("Provisioning fresh remote sandbox container...")

        env_payload = self.environment.build_environment_payload(
            sources=remote_sources,
            force_fresh=force_fresh_environment,
            inherit_agent_environment=not self.load_local_context,
        )

        # 3. Augment prompt with system instructions & skill catalog context if needed
        full_input = prompt
        context_prefixes = []
        if self.load_local_context and not self.environment.get_environment_id():
            catalog = self.skills.format_skill_catalog()
            if system_instructions:
                context_prefixes.append(f"<!-- System Instructions -->\n{system_instructions}")
            if catalog:
                context_prefixes.append(f"<!-- Available Skills In Remote Environment -->\n{catalog}")

        if context_prefixes:
            full_input = "\n\n".join(context_prefixes) + f"\n\n{prompt}"

        # 4. Execute interaction via client using Antigravity coding agent
        interaction_kwargs: Dict[str, Any] = {
            "agent": self.config.agent_id,
            "input": full_input,
        }
        if env_payload is not None:
            interaction_kwargs["environment"] = env_payload

        if self.last_interaction_id and not force_fresh_environment:
            interaction_kwargs["previous_interaction_id"] = self.last_interaction_id

        reporter.thinking("Reasoning through instructions and planning solution...")

        interaction = None
        streamed_chunks: List[str] = []
        try:
            # First attempt streaming to capture live steps (thinking, skill use, tool call)
            try:
                stream_kwargs = dict(interaction_kwargs)
                stream_kwargs["stream"] = True
                stream_result = self.client.interactions.create(**stream_kwargs)
                if hasattr(stream_result, "__iter__") and not hasattr(stream_result, "output_text"):
                    for raw_event in stream_result:
                        data = getattr(raw_event, "data", raw_event)
                        # Check step events
                        step = getattr(data, "step", None)
                        if step:
                            step_name = type(step).__name__.lower()
                            if "thought" in step_name:
                                txt = getattr(step, "thought", "") or getattr(step, "summary", "")
                                reporter.thinking(txt[:60] if txt else "Reasoning...")
                            elif any(k in step_name for k in ("tool", "function", "codeexecution", "filesearch", "mcpserver")):
                                t_name = getattr(step, "name", None) or getattr(getattr(step, "function_call", None), "name", None) or "sandbox_tool"
                                reporter.tool_call(str(t_name))
                            elif "processing" in step_name or "skill" in step_name:
                                reporter.skill_use("Executing skill step")
                            elif "modeloutput" in step_name:
                                reporter.responding()

                        # Collect text delta if streaming
                        delta = getattr(data, "delta", None)
                        if delta:
                            d_text = getattr(delta, "text", None)
                            if isinstance(d_text, str) and d_text:
                                streamed_chunks.append(d_text)

                        if hasattr(data, "interaction"):
                            interaction = data.interaction
                else:
                    interaction = stream_result
            except Exception as stream_err:
                logger.debug("Streaming execution fallback: %s", stream_err)
                interaction = self.client.interactions.create(**interaction_kwargs)

        except Exception as api_err:
            err_msg = str(api_err)
            # If 404 occurs because a previously persisted environment ID has expired on Google's servers:
            if ("404" in err_msg or "not found" in err_msg.lower() or "not_found" in err_msg.lower()) and isinstance(env_payload, str):
                reporter.environment("Sandbox expired. Provisioning fresh container...")
                logger.info(
                    "Remote container Environment ID '%s' not found (expired). "
                    "Resetting local state and provisioning a fresh remote sandbox...",
                    env_payload,
                )
                self.environment.reset_environment()
                fresh_env_payload = self.environment.build_environment_payload(
                    sources=remote_sources,
                    force_fresh=True,
                    inherit_agent_environment=not self.load_local_context,
                )
                if fresh_env_payload is not None:
                    interaction_kwargs["environment"] = fresh_env_payload
                else:
                    interaction_kwargs.pop("environment", None)
                if "previous_interaction_id" in interaction_kwargs:
                    del interaction_kwargs["previous_interaction_id"]
                reporter.thinking("Awaiting Antigravity response in fresh container...")
                interaction = self.client.interactions.create(**interaction_kwargs)
            else:
                reporter.stop("Execution failed")
                raise

        reporter.complete("Response received")

        # 5. Securely capture and persist the remote environment ID
        returned_env_id = getattr(interaction, "environment_id", None) or (
            env_payload if isinstance(env_payload, str) else "env_persisted_active"
        )
        interaction_id = getattr(interaction, "id", None)
        if interaction_id:
            self.last_interaction_id = interaction_id

        if returned_env_id and returned_env_id != "unknown_env":
            self.environment.save_environment_id(
                environment_id=returned_env_id,
                skills_signature=self.skills.get_combined_signature() if self.load_local_context else None,
                metadata={"last_prompt_snippet": prompt[:100]},
            )
            # Track and hold environment_id per conversation session in registry
            if self.active_session_id:
                self.registry.update_conversation_session(
                    agent_id=self.config.agent_id,
                    session_id=self.active_session_id,
                    environment_id=returned_env_id,
                    last_interaction_id=interaction_id,
                    increment_turn=True,
                )
            else:
                session = self.registry.create_conversation_session(
                    agent_id=self.config.agent_id,
                    environment_id=returned_env_id,
                    title=prompt[:45].strip() or "New Chat",
                )
                self.active_session_id = session.session_id
                if interaction_id:
                    self.registry.update_conversation_session(
                        agent_id=self.config.agent_id,
                        session_id=self.active_session_id,
                        last_interaction_id=interaction_id,
                        increment_turn=True,
                    )

        # 6. Extract only the clean text response and capture local files
        output_text = extract_interaction_text(interaction, fallback_streamed="".join(streamed_chunks))
        saved_files: List[SavedFile] = []
        if save_deliverables_locally:
            saved_files = self.storage.capture_remote_interaction_files(interaction, output_text=output_text)

        logger.info(
            "Turn completed. Agent: %s, Session: %s, Environment ID: %s, Local files: %d",
            self.config.agent_id,
            self.active_session_id,
            returned_env_id,
            len(saved_files),
        )

        return ThreeGAgentResponse(
            output_text=output_text,
            environment_id=returned_env_id,
            interaction_id=interaction_id,
            session_id=self.active_session_id,
            saved_files=saved_files,
            raw_interaction=interaction,
        )

    def chat(self, message: str, show_status: bool = True) -> ThreeGAgentResponse:
        """Conducts a multi-turn conversation turn while maintaining session state."""
        return self.execute(message, force_fresh_environment=False, show_status=show_status)

    def run_skill_stage(
        self,
        skill_name: str,
        stage_identifier: Union[int, str],
        stage_input: str,
        save_output_as: Optional[str] = None,
        show_status: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes a specific stage from a loaded multi-stage skill (e.g. pedagogy-engineering).
        
        Args:
            skill_name: Name of the skill (e.g. "pedagogy-engineering").
            stage_identifier: Stage number or key (e.g. 0, 1, "stage_0").
            stage_input: Input parameters for this stage.
            save_output_as: Optional filename to save the stage deliverable locally.
            show_status: Whether to display dynamic terminal status updates.
        """
        stage_ref = (
            f"stage_{stage_identifier}"
            if isinstance(stage_identifier, int)
            else str(stage_identifier)
        )
        stage_prompt = (
            f"Execute {skill_name} {stage_ref}.\n"
            f"Adhere strictly to the rubric and checklist in `.agents/skills/{skill_name}/stages/{stage_ref}.md`.\n"
            f"Inputs:\n{stage_input}\n\n"
            f"Produce the full deliverable using explicit file blocks so it can be saved locally."
        )

        response = self.execute(stage_prompt, show_status=show_status)

        # If a specific filename was requested, also write the output text directly
        if save_output_as:
            saved_file = self.storage.save_file(
                relative_name=save_output_as,
                content=response.output_text,
                source_type="direct_stage_deliverable",
            )
            response.saved_files.append(saved_file)

        return response

    def start_new_chat(self, title: str = "New Chat") -> None:
        """Starts a fresh conversation for this agent, requesting a new remote sandbox container."""
        self.active_session_id = None
        self.last_interaction_id = None
        self.environment.reset_environment()
        logger.info("Started fresh conversation session for agent '%s'.", self.config.agent_id)

    def resume_conversation(self, session_id: str) -> bool:
        """Resumes an existing conversation session and restores its remote environment ID.
        
        Guarantees that the environment_id is held for persistence purposes.
        """
        convs = self.registry.list_conversations(self.config.agent_id)
        target = next((c for c in convs if c.session_id == session_id), None)
        if not target:
            logger.warning("Conversation session '%s' not found for agent '%s'", session_id, self.config.agent_id)
            return False

        self.active_session_id = target.session_id
        self.last_interaction_id = target.last_interaction_id
        # Restore and hold the environment ID
        self.environment.save_environment_id(target.environment_id)
        logger.info(
            "Resumed conversation '%s' for agent '%s' holding environment ID: %s",
            target.session_id,
            self.config.agent_id,
            target.environment_id,
        )
        return True

    def list_conversations(self) -> List[ConversationSession]:
        """Lists all persistent conversation sessions for this agent."""
        return self.registry.list_conversations(self.config.agent_id)

    def get_environment_id(self) -> Optional[str]:
        """Returns the currently active remote environment ID."""
        return self.environment.get_environment_id()

    def reset_environment(self) -> None:
        """Resets the remote sandbox session so a fresh container will be spawned."""
        self.environment.reset_environment()
        self.active_session_id = None
        self.last_interaction_id = None
        logger.info("3G-agent environment session reset.")

    def list_local_files(self) -> List[Dict[str, Any]]:
        """Lists all files created and accessible locally."""
        return self.storage.list_saved_files()

    def delete_agent(self, agent_id: Optional[str] = None) -> DeletionResult:
        """Deletes the agent according to Antigravity SDK procedure."""
        target = agent_id or self.config.agent_id
        return AgentDeletionManager.delete_agent(
            agent_id=target,
            client=self.client,
            registry=self.registry,
            state_dir=self.config.state_dir,
        )

    def delete_interaction(self, interaction_id: Optional[str] = None) -> DeletionResult:
        """Deletes an interaction according to Antigravity SDK procedure."""
        target = interaction_id or self.last_interaction_id
        if not target:
            return DeletionResult(
                success=False,
                target_type="interaction",
                target_id="none",
                remote_deleted=False,
                local_deleted=False,
                message="No interaction ID provided or active.",
            )
        return AgentDeletionManager.delete_interaction(
            interaction_id=target,
            client=self.client,
            registry=self.registry,
            state_dir=self.config.state_dir,
        )

    def delete_conversation_session(self, session_id: Optional[str] = None) -> DeletionResult:
        """Deletes a conversation session, held remote interaction, and environment."""
        target = session_id or self.active_session_id
        if not target:
            return DeletionResult(
                success=False,
                target_type="session",
                target_id="none",
                remote_deleted=False,
                local_deleted=False,
                message="No session ID provided or active.",
            )
        res = AgentDeletionManager.delete_conversation_session(
            agent_id=self.config.agent_id,
            session_id=target,
            client=self.client,
            registry=self.registry,
            state_dir=self.config.state_dir,
        )
        if target == self.active_session_id:
            self.active_session_id = None
            self.last_interaction_id = None
        return res


