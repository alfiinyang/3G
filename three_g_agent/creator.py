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


def _field(obj: Any, name: str) -> Any:
    """Reads a field from an SDK model object or a plain dict."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


@dataclass
class AgentCreationSpec:
    """Specification required to create a new Antigravity agent on the SDK API.
    
    Attributes:
        agent_id: Identifier following [name-id_num] format (e.g. "coder-12345").
        skills_dir: Directory containing skills to pre-load into the agent (None if no skills).
        instructions_file: Optional path to instructions file holding the system prompt.
        description: Developer-facing description of the agent.
        base_agent: Base Antigravity coding engine ("antigravity-preview-09-2026").
        tools: Optional list of tool definitions or restrictions.
        metadata: Arbitrary additional metadata.
    """
    agent_id: str
    skills_dir: Optional[Union[str, Path]] = "./skills"
    instructions_file: Optional[Union[str, Path]] = "./desi_instructions.md"
    description: Optional[str] = None
    base_agent: str = "antigravity-preview-09-2026"
    tools: Optional[List[Any]] = None
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

        # 2. Pre-load skills (if skills_dir provided)
        if spec.skills_dir and Path(spec.skills_dir).exists():
            skills_path = Path(spec.skills_dir).resolve()
            loader = SkillLoader(skills_path)
            skill_names = [s.name for s in loader.skills]
            total_stages = sum(len(s.auxiliary_files) for s in loader.skills)
        else:
            loader = SkillLoader.empty()
            skill_names = []
            total_stages = 0
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
        candidate_files.extend([
            Path("./instructions/desi_instructions.md").resolve(),
            Path("./desi_instructions.md").resolve(),
            Path("./instructions/orch_instruction.md").resolve(),
            Path("./instructions.md").resolve(),
        ])

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
                    ThreeGAgentConfig(skills_dir=spec.skills_dir if spec.skills_dir else None),
                    interactive_prompt=False,
                )
                sdk_client = cls._extract_client(initialized)
            except Exception as auto_err:
                logger.debug("Auto-initialization of SDK client skipped: %s", auto_err)

        if not sdk_client or not hasattr(sdk_client, "agents") or not hasattr(sdk_client.agents, "create"):
            raise RuntimeError(
                "Antigravity SDK client is required to create an agent via the SDK API (client.agents.create)."
            )

        # Persist skills + instructions in the agent's remote base environment.
        # This is the ONLY time local skills/instructions are uploaded; existing
        # agents rely on what persists in their remote environment.
        base_sources: List[Dict[str, Any]] = loader.build_remote_sources()
        if instructions_content:
            for target in (".agents/instructions.md", ".agents/AGENTS.md"):
                base_sources.append({"type": "inline", "target": target, "content": instructions_content})

        create_kwargs: Dict[str, Any] = {
            "id": clean_id,
            "base_agent": spec.base_agent,
            "description": description,
            "base_environment": {"type": "remote", "sources": base_sources},
        }
        if instructions_content:
            create_kwargs["system_instruction"] = instructions_content
        if spec.tools is not None:
            create_kwargs["tools"] = spec.tools


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
    def describe_agent_capabilities(cls, agent_id: str, client_handle: Optional[Any] = None) -> Dict[str, Any]:
        """Fetches an agent from the SDK API and extracts its custom skills and tools.

        Skills are discovered from `base_environment.sources` entries targeting
        `.agents/skills/<name>/SKILL.md`; tools come from `agent.tools`.
        Returns {"found", "skills": [{name, description, files}], "tools": [{type, name, detail}],
                 "has_instructions": bool}.
        """
        result: Dict[str, Any] = {"found": False, "skills": [], "tools": [], "has_instructions": False}
        agent = cls.get_agent(agent_id, client_handle)
        if agent is None:
            return result
        result["found"] = True
        result["has_instructions"] = bool(_field(agent, "system_instruction"))

        # --- Skills from the persisted remote base environment ---
        env = _field(agent, "base_environment")
        sources = _field(env, "sources") if env is not None and not isinstance(env, str) else None
        skills: Dict[str, Dict[str, Any]] = {}
        for src in sources or []:
            target = str(_field(src, "target") or "")
            parts = target.replace("\\", "/").split("/")
            if len(parts) >= 4 and parts[0] == ".agents" and parts[1] == "skills":
                name = parts[2]
                entry = skills.setdefault(name, {"name": name, "description": "", "files": 0})
                entry["files"] += 1
                if parts[-1] == "SKILL.md" and len(parts) == 4:
                    content = str(_field(src, "content") or "")
                    fm_name, fm_desc, _ = SkillLoader(Path("."), autoload=False)._extract_frontmatter(content)
                    if fm_desc:
                        entry["description"] = fm_desc
                    if fm_name:
                        entry["name"] = fm_name
            elif parts[-1] in ("AGENTS.md", "instructions.md") and parts[0] == ".agents":
                result["has_instructions"] = True
        result["skills"] = list(skills.values())

        # --- Custom tools ---
        for tool in _field(agent, "tools") or []:
            t_type = str(_field(tool, "type") or type(tool).__name__)
            t_name = _field(tool, "name") or ""
            detail = _field(tool, "description") or _field(tool, "url") or ""
            result["tools"].append({"type": t_type, "name": str(t_name), "detail": str(detail)})

        return result

    @classmethod
    def display_agent_capabilities(cls, agent_id: str, client_handle: Optional[Any] = None) -> Dict[str, Any]:
        """Fetches (from the API) and prints the agent's custom skills and tools."""
        caps = cls.describe_agent_capabilities(agent_id, client_handle)
        print("\n" + "-" * 65)
        print(f"  Agent '{agent_id}' Capabilities (fetched via client.agents.get)")
        print("-" * 65)
        if not caps["found"]:
            print("  [!] Could not fetch agent details from the API.")
            return caps

        print(f"  System Instructions : {'Persisted' if caps['has_instructions'] else 'None'}")
        print(f"  Custom Skills ({len(caps['skills'])}):")
        if caps["skills"]:
            for s in caps["skills"]:
                desc = f" - {s['description']}" if s["description"] else ""
                print(f"    - {s['name']} ({s['files']} file(s)){desc}")
        else:
            print("    (none persisted in remote environment)")

        print(f"  Custom Tools ({len(caps['tools'])}):")
        if caps["tools"]:
            for t in caps["tools"]:
                label = t["name"] or t["type"]
                extra = f" - {t['detail']}" if t["detail"] else ""
                print(f"    - {label} [{t['type']}]{extra}")
        else:
            print("    (none)")
        print("-" * 65)
        return caps

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
