"""Standalone Agent Creation Module for 3G-agent.

STRICT STANDALONE MODULE REQUIREMENT:
Responsible solely for validating agent IDs (format: [name-id_num] e.g. [coder-12345]),
pre-loading skills and instructions (system prompt) at creation time, and registering
the agent with the client and local registry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .initializer import InitializedClient
from .registry import AgentRecord, AgentRegistry, validate_agent_id
from .skills import SkillLoader

logger = logging.getLogger("3G-agent.creator")


@dataclass
class AgentCreationSpec:
    """Specification required to create a new Antigravity agent.
    
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
    """Result of agent creation."""
    agent_id: str
    record: AgentRecord
    skills_count: int
    stages_count: int
    has_instructions: bool
    instructions_length: int
    remote_registered: bool = False
    warning: Optional[str] = None


class AgentCreator:
    """Standalone module responsible for creating and provisioning new Antigravity agents."""

    @classmethod
    def create_agent(
        cls,
        spec: AgentCreationSpec,
        client_handle: Optional[InitializedClient] = None,
        registry: Optional[AgentRegistry] = None,
    ) -> AgentCreationResult:
        """Creates and registers a new Antigravity agent.
        
        Steps:
        1. Validates agent_id adheres strictly to format [name-id_num].
        2. Pre-loads all skills from the specified folder.
        3. Pre-loads system instructions (system prompt) from instructions.md.
        4. Registers agent with SDK client (via client.agents.create) if live connection exists.
        5. Persists the agent definition into the AgentRegistry.
        
        Args:
            spec: AgentCreationSpec parameters.
            client_handle: Optional authenticated InitializedClient.
            registry: Optional AgentRegistry instance.
            
        Returns:
            AgentCreationResult summarizing the created agent.
            
        Raises:
            ValueError: If agent_id fails format validation.
        """
        # 1. Format validation [name-id_num]
        clean_id = validate_agent_id(spec.agent_id)
        logger.info("Creating new Antigravity agent with ID: '%s'...", clean_id)

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
        preview = ""

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
                        preview = text[:120]
                        logger.info("Pre-loaded system instructions (%d chars) from %s", len(text), instr_path.name)
                        break
                except Exception as read_err:
                    logger.warning("Could not read instructions file %s: %s", instr_path, read_err)

        description = spec.description or f"Teaching Assistant Agent pre-loaded with skills: {', '.join(skill_names) or 'none'}"

        # 4. Attempt remote agent registration with Antigravity SDK
        remote_registered = False
        warning = None
        if client_handle and hasattr(client_handle, "client"):
            sdk_client = client_handle.client
            if hasattr(sdk_client, "agents") and hasattr(sdk_client.agents, "create"):
                try:
                    logger.info("Registering agent '%s' on Antigravity GAOS service...", clean_id)
                    # Prepare remote agent parameters
                    create_kwargs: Dict[str, Any] = {
                        "id": clean_id,
                        "base_agent": spec.base_agent,
                        "description": description,
                    }
                    if instructions_content:
                        create_kwargs["system_instruction"] = instructions_content

                    sdk_client.agents.create(**create_kwargs)
                    remote_registered = True
                    logger.info("Successfully registered agent '%s' on remote Antigravity service.", clean_id)
                except Exception as reg_err:
                    warning = str(reg_err)
                    logger.warning(
                        "Remote agent registration via client.agents.create not completed: %s. "
                        "The agent will operate seamlessly via direct Antigravity interactions execution.",
                        reg_err,
                    )

        # 5. Persist agent in local registry
        active_registry = registry or AgentRegistry()
        record = active_registry.register_agent(
            agent_id=clean_id,
            base_agent=spec.base_agent,
            description=description,
            skills_names=skill_names,
            has_instructions=has_instructions,
            instructions_preview=preview,
            metadata={
                **spec.metadata,
                "skills_count": len(skill_names),
                "stages_count": total_stages,
                "instructions_length": instructions_length,
                "remote_registered": remote_registered,
            },
        )

        return AgentCreationResult(
            agent_id=clean_id,
            record=record,
            skills_count=len(skill_names),
            stages_count=total_stages,
            has_instructions=has_instructions,
            instructions_length=instructions_length,
            remote_registered=remote_registered,
            warning=warning,
        )
