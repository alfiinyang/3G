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
from .environment import EnvironmentStore
from .initializer import InitializedClient, ModelInitializer
from .registry import AgentRegistry, ConversationSession
from .skills import Skill, SkillLoader
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
    ) -> None:
        """Initializes 3G-agent with pre-configured and pre-initialized dependencies."""
        self.config = config
        self.client_handle = initialized_client
        self.client = initialized_client.client
        self.skills = skill_loader
        self.environment = environment_store
        self.storage = storage_manager
        self.registry = registry or AgentRegistry(state_dir=config.state_dir)
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
        ClientParameterCollector.validate(config)

        # Step 2: Separate Client Initialization
        initialized_client = ModelInitializer.initialize(config)

        # Step 3: Skill Discovery & Packaging
        skill_loader = SkillLoader(config.skills_dir)

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
        )

    def execute(
        self,
        prompt: str,
        force_fresh_environment: bool = False,
        additional_sources: Optional[List[Dict[str, Any]]] = None,
        save_deliverables_locally: bool = True,
    ) -> ThreeGAgentResponse:
        """Executes an operation in the remote Antigravity sandbox.
        
        Args:
            prompt: User instructions or query for the agent.
            force_fresh_environment: If True, ignores previous environment ID and starts a fresh container.
            additional_sources: Optional extra inline files or data to mount.
            save_deliverables_locally: Whether to automatically extract and save generated files locally.
            
        Returns:
            ThreeGAgentResponse with output text, environment ID, and local saved file links.
        """
        logger.info("Executing 3G-agent turn...")

        # 1. Prepare remote sources from loaded skills & instructions
        remote_sources = self.skills.build_remote_sources()
        if additional_sources:
            remote_sources.extend(additional_sources)

        # Mount system instructions from instructions.md if present
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

        # 2. Build remote environment payload (reuses existing environment_id if active)
        env_payload = self.environment.build_environment_payload(
            sources=remote_sources,
            force_fresh=force_fresh_environment,
        )

        # 3. Augment prompt with system instructions & skill catalog context if needed
        full_input = prompt
        catalog = self.skills.format_skill_catalog()
        
        context_prefixes = []
        if system_instructions and not self.environment.get_environment_id():
            context_prefixes.append(f"<!-- System Instructions -->\n{system_instructions}")
        if catalog and not self.environment.get_environment_id():
            context_prefixes.append(f"<!-- Available Skills In Remote Environment -->\n{catalog}")

        if context_prefixes:
            full_input = "\n\n".join(context_prefixes) + f"\n\n{prompt}"

        # 4. Execute interaction via client using Antigravity coding agent
        interaction_kwargs: Dict[str, Any] = {
            "agent": self.config.agent_id,
            "input": full_input,
            "environment": env_payload,
        }

        if self.last_interaction_id and not force_fresh_environment:
            interaction_kwargs["previous_interaction_id"] = self.last_interaction_id

        try:
            interaction = self.client.interactions.create(**interaction_kwargs)
        except Exception as api_err:
            err_msg = str(api_err)
            # If 404 occurs because a previously persisted environment ID has expired on Google's servers:
            if ("404" in err_msg or "not found" in err_msg.lower() or "not_found" in err_msg.lower()) and isinstance(env_payload, str):
                logger.warning(
                    "Remote container Environment ID '%s' not found (expired). "
                    "Resetting local state and provisioning a fresh remote sandbox...",
                    env_payload,
                )
                print(f"\n[!] Previous remote sandbox '{env_payload}' expired or not found. Provisioning fresh container...")
                self.environment.reset_environment()
                fresh_env_payload = self.environment.build_environment_payload(
                    sources=remote_sources,
                    force_fresh=True,
                )
                interaction_kwargs["environment"] = fresh_env_payload
                if "previous_interaction_id" in interaction_kwargs:
                    del interaction_kwargs["previous_interaction_id"]
                interaction = self.client.interactions.create(**interaction_kwargs)
            else:
                raise

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
                skills_signature=self.skills.get_combined_signature(),
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

        # 6. File Accessibility: capture and save files locally
        output_text = getattr(interaction, "output_text", str(interaction))
        saved_files: List[SavedFile] = []
        if save_deliverables_locally:
            saved_files = self.storage.capture_remote_interaction_files(interaction)

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

    def chat(self, message: str) -> ThreeGAgentResponse:
        """Conducts a multi-turn conversation turn while maintaining session state."""
        return self.execute(message, force_fresh_environment=False)

    def run_skill_stage(
        self,
        skill_name: str,
        stage_identifier: Union[int, str],
        stage_input: str,
        save_output_as: Optional[str] = None,
    ) -> ThreeGAgentResponse:
        """Executes a specific stage from a loaded multi-stage skill (e.g. pedagogy-engineering).
        
        Args:
            skill_name: Name of the skill (e.g. "pedagogy-engineering").
            stage_identifier: Stage number or key (e.g. 0, 1, "stage_0").
            stage_input: Input parameters for this stage.
            save_output_as: Optional filename to save the stage deliverable locally.
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

        response = self.execute(stage_prompt)

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

