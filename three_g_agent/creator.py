"""Standalone Agent Creation & Management Module for 3G-agent.

STRICT REMOTE SDK API ARCHITECTURE:
- Agent Creation: Dispatched directly to the Antigravity SDK API (`client.agents.create`).
- Agent Listing: Collected directly from the Antigravity SDK API (`client.agents.list`).
- Agent Retrieval: Fetched directly from the Antigravity SDK API (`client.agents.get`).
- Agent Deletion: Sent directly to the Antigravity SDK API (`client.agents.delete`).
- No local memory, no local JSON files, and no local caches are used for agent definitions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .initializer import InitializedClient
from .registry import validate_agent_id
from .skills import SkillLoader

logger = logging.getLogger("3G-agent.creator")


@dataclass
class AgentCreationSpec:
    """Specification required to create a new Antigravity agent on the SDK API.
    
    Attributes:
        agent_id: Identifier following [name-id_num] format (e.g. "coder-12345").
        skills_dir: Directory containing skills to pre-load into the agent.
        instructions_file: Optional path to instructions.md holding the system prompt.
        description: Developer-facing description of the agent.
        base_agent: Base Antigravity coding engine ("antigravity-preview-09-2026").
        metadata: Arbitrary additional metadata.
    """
    agent_id: str
    skills_dir: Union[str, Path] = "./skills"
    instructions_file: Optional[Union[str, Path]] = "./instructions.md"
    description: Optional[str] = None
    base_agent: str = "antigravity-preview-09-2026"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCreationResult:
    """Result of agent creation directly via the Antigravity SDK API."""
    agent_id: str
    skills_count: int
    stages_count: int
    has_instructions: bool
    instructions_length: int
    remote_agent: Any = None
    warning: Optional[str] = None


class AgentCreator:
    """Standalone module responsible for creating, listing, and managing agents on the Antigravity SDK API."""

    @classmethod
    def _extract_client(cls, client_handle: Any) -> Any:
        """Extracts underlying SDK client instance."""
        return getattr(client_handle, "client", client_handle)

    @classmethod
    def create_agent(
        cls,
        spec: AgentCreationSpec,
        client_handle: Optional[Any] = None,
        registry: Optional[Any] = None,
    ) -> AgentCreationResult:
        """Creates a new Antigravity agent directly on the Antigravity SDK API.
        
        Steps:
        1. Validates agent_id adheres strictly to format [name-id_num].
        2. Pre-loads all skills from the specified folder.
        3. Pre-loads system instructions (system prompt) from instructions.md.
        4. Invokes the Antigravity SDK API via `client.agents.create(...)`.
        5. Zero local storage: Agent definitions live on the Antigravity SDK service.
        
        Args:
            spec: AgentCreationSpec parameters.
            client_handle: Authenticated InitializedClient or raw SDK client.
            registry: Optional legacy parameter (ignored - no local storage).
            
        Returns:
            AgentCreationResult holding the remote agent object returned by the SDK API.
            
        Raises:
            ValueError: If agent_id fails format validation.
            RuntimeError: If SDK client is missing or lacks client.agents.create API.
        """
        # 1. Format validation [name-id_num]
        clean_id = validate_agent_id(spec.agent_id)
        logger.info("Creating new Antigravity agent on SDK API with ID: '%s'...", clean_id)

        # 2. Pre-load skills
        skills_path = Path(spec.skills_dir).resolve()
        loader = SkillLoader(skills_path)
        skill_names = [s.name for s in loader.skills]
        total_stages = sum(len(s.auxiliary_files) for s in loader.skills)
        logger.info(
            "Pre-loaded %d skill(s) with %d stage/auxiliary files for agent '%s'.",
            len(skill_names),
            total_stages,
            clean_id,
        )

        # 3. Pre-load instructions (system prompt)
        instructions_content = None
        has_instructions = False
        instructions_length = 0

        candidate_files = []
        if spec.instructions_file:
            candidate_files.append(Path(spec.instructions_file).resolve())
        candidate_files.extend([Path("./instructions.txt").resolve(), Path("./instructions.md").resolve()])

        for instr_path in candidate_files:
            if instr_path.is_file():
                try:
                    text = instr_path.read_text(encoding="utf-8").strip()
                    if text:
                        instructions_content = text
                        has_instructions = True
                        instructions_length = len(text)
                        logger.info("Pre-loaded system instructions (%d chars) from %s", len(text), instr_path.name)
                        break
                except Exception as read_err:
                    logger.warning("Could not read instructions file %s: %s", instr_path, read_err)

        description = spec.description or f"Antigravity Agent pre-loaded with skills: {', '.join(skill_names) or 'none'}"

        # 4. Invoke Antigravity SDK API directly (no local file saving)
        sdk_client = cls._extract_client(client_handle)
        if sdk_client is None:
            try:
                from .initializer import AgentClientInitializer
                from .config import ThreeGAgentConfig
                initialized = AgentClientInitializer.initialize(
                    ThreeGAgentConfig(skills_dir=spec.skills_dir),
                    interactive_prompt=False,
                )
                sdk_client = cls._extract_client(initialized)
            except Exception as auto_err:
                logger.debug("Auto-initialization of SDK client skipped: %s", auto_err)

        if not sdk_client or not hasattr(sdk_client, "agents") or not hasattr(sdk_client.agents, "create"):
            raise RuntimeError(
                "Antigravity SDK client is required to create an agent via the SDK API (client.agents.create)."
            )

        create_kwargs: Dict[str, Any] = {
            "id": clean_id,
            "base_agent": spec.base_agent,
            "description": description,
        }
        if instructions_content:
            create_kwargs["system_instruction"] = instructions_content

        logger.info("Calling Antigravity SDK API -> client.agents.create(id='%s')...", clean_id)
        remote_agent = sdk_client.agents.create(**create_kwargs)
        logger.info("Agent '%s' successfully created on Antigravity SDK API.", clean_id)

        return AgentCreationResult(
            agent_id=clean_id,
            skills_count=len(skill_names),
            stages_count=total_stages,
            has_instructions=has_instructions,
            instructions_length=instructions_length,
            remote_agent=remote_agent,
            warning=None,
        )

    @classmethod
    def list_agents(cls, client_handle: Optional[Any] = None) -> List[Any]:
        """Lists all agents directly from the Antigravity SDK API (`client.agents.list`).
        
        Zero local memory or local cache is used. Everything is collected from the API.
        
        Args:
            client_handle: InitializedClient or raw SDK client. If None, automatically connects.
            
        Returns:
            List of Agent objects from the Antigravity SDK API.
        """
        sdk_client = cls._extract_client(client_handle)
        if sdk_client is None:
            try:
                from .initializer import AgentClientInitializer
                from .config import ThreeGAgentConfig
                initialized = AgentClientInitializer.initialize(ThreeGAgentConfig(), interactive_prompt=False)
                sdk_client = cls._extract_client(initialized)
            except Exception as e:
                logger.debug("Auto client initialization skipped in list_agents: %s", e)

        if not sdk_client or not hasattr(sdk_client, "agents") or not hasattr(sdk_client.agents, "list"):
            logger.warning("SDK client does not provide client.agents.list")
            return []

        logger.info("Calling Antigravity SDK API -> client.agents.list()...")
        try:
            response = sdk_client.agents.list()
            if hasattr(response, "agents"):
                return list(response.agents)
            if isinstance(response, list):
                return response
            return []
        except Exception as err:
            logger.error("Antigravity SDK API client.agents.list error: %s", err)
            return []

    @classmethod
    def get_agent(cls, agent_id: str, client_handle: Optional[Any] = None) -> Optional[Any]:
        """Retrieves an agent directly from the Antigravity SDK API (`client.agents.get`)."""
        sdk_client = cls._extract_client(client_handle)
        if sdk_client is None:
            try:
                from .initializer import AgentClientInitializer
                from .config import ThreeGAgentConfig
                initialized = AgentClientInitializer.initialize(ThreeGAgentConfig(), interactive_prompt=False)
                sdk_client = cls._extract_client(initialized)
            except Exception as e:
                logger.debug("Auto client initialization skipped in get_agent: %s", e)

        if not sdk_client or not hasattr(sdk_client, "agents") or not hasattr(sdk_client.agents, "get"):
            return None

        clean_id = validate_agent_id(agent_id) if agent_id else agent_id
        try:
            return sdk_client.agents.get(id=clean_id)
        except Exception as err:
            logger.debug("Antigravity SDK API client.agents.get('%s') error: %s", clean_id, err)
            return None

    @classmethod
    def delete_agent(cls, agent_id: str, client_handle: Optional[Any] = None) -> Any:
        """Deletes an agent directly on the Antigravity SDK API (`client.agents.delete`)."""
        sdk_client = cls._extract_client(client_handle)
        if sdk_client is None:
            try:
                from .initializer import AgentClientInitializer
                from .config import ThreeGAgentConfig
                initialized = AgentClientInitializer.initialize(ThreeGAgentConfig(), interactive_prompt=False)
                sdk_client = cls._extract_client(initialized)
            except Exception as e:
                logger.debug("Auto client initialization skipped in delete_agent: %s", e)

        if not sdk_client or not hasattr(sdk_client, "agents") or not hasattr(sdk_client.agents, "delete"):
            raise RuntimeError("SDK client does not provide client.agents.delete")

        clean_id = validate_agent_id(agent_id) if agent_id else agent_id
        logger.info("Calling Antigravity SDK API -> client.agents.delete(id='%s')...", clean_id)
        return sdk_client.agents.delete(id=clean_id)
