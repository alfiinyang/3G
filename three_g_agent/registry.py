"""Agent Registry and Session Persistence Store for 3G-agent.

Maintains metadata of all created and existing Antigravity agents, along with
their associated remote environment IDs and conversation sessions.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("3G-agent.registry")

# Format requirement: [name-id_num] e.g. coder-12345
AGENT_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]+-[a-zA-Z0-9]+$")


def validate_agent_id(raw_id: str) -> str:
    """Validates and normalizes an agent_id to adhere to [name-id_num] format.
    
    Examples of valid IDs:
        - coder-12345
        - [coder-12345]
        - pedagogy-001
        - 3g-agent-99
    
    Raises:
        ValueError: If raw_id does not conform to the [name-id_num] format.
    """
    clean_id = raw_id.strip()
    if clean_id.startswith("[") and clean_id.endswith("]"):
        clean_id = clean_id[1:-1].strip()

    if not clean_id:
        raise ValueError("Agent ID cannot be empty. Must follow format [name-id_num] e.g. coder-12345.")

    if not AGENT_ID_REGEX.match(clean_id):
        raise ValueError(
            f"Invalid agent ID '{clean_id}'. Agent IDs must follow the format [name-id_num] "
            f"(e.g. coder-12345, pedagogy-001) containing alphanumeric characters and a hyphen."
        )

    return clean_id


@dataclass
class ConversationSession:
    """Represents a conversation session tied to an agent and remote environment."""
    session_id: str
    agent_id: str
    environment_id: str
    created_at: str
    updated_at: str
    last_interaction_id: Optional[str] = None
    turn_count: int = 0
    title: str = "New Conversation"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConversationSession:
        return cls(**data)


@dataclass
class AgentRecord:
    """Metadata record for a registered agent."""
    agent_id: str
    created_at: str
    base_agent: str = "antigravity-preview-09-2026"
    description: str = ""
    skills_names: List[str] = field(default_factory=list)
    has_instructions: bool = False
    instructions_preview: str = ""
    conversations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentRecord:
        return cls(**data)


class AgentRegistry:
    """Local persistent store for agents, their skills, and their remote environments."""

    def __init__(self, state_dir: Union[str, Path] = "./.3g_agent") -> None:
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.state_dir / "agents_registry.json"
        self._ensure_registry()

    def _ensure_registry(self) -> None:
        """Initializes empty registry file if missing."""
        if not self.registry_file.exists():
            default_data = {
                "version": "1.0",
                "agents": {},
                "last_active_agent_id": None,
            }
            self._save_raw(default_data)

    def _load_raw(self) -> Dict[str, Any]:
        try:
            return json.loads(self.registry_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Error reading registry file: %s. Reinitializing.", e)
            return {"version": "1.0", "agents": {}, "last_active_agent_id": None}

    def _save_raw(self, data: Dict[str, Any]) -> None:
        self.registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def register_agent(
        self,
        agent_id: str,
        base_agent: str = "antigravity-preview-09-2026",
        description: str = "",
        skills_names: Optional[List[str]] = None,
        has_instructions: bool = False,
        instructions_preview: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentRecord:
        """Registers a newly created or discovered agent."""
        clean_id = validate_agent_id(agent_id)
        raw_data = self._load_raw()

        existing = raw_data.get("agents", {}).get(clean_id)
        conversations = existing.get("conversations", {}) if existing else {}

        record = AgentRecord(
            agent_id=clean_id,
            created_at=existing.get("created_at") if existing else datetime.now().isoformat(),
            base_agent=base_agent,
            description=description,
            skills_names=skills_names or [],
            has_instructions=has_instructions,
            instructions_preview=instructions_preview[:120],
            conversations=conversations,
            metadata=metadata or {},
        )

        raw_data.setdefault("agents", {})[clean_id] = record.to_dict()
        raw_data["last_active_agent_id"] = clean_id
        self._save_raw(raw_data)
        logger.info("Registered agent '%s' in local registry.", clean_id)
        return record

    def list_agents(self) -> List[AgentRecord]:
        """Lists all registered agents."""
        raw_data = self._load_raw()
        agents = []
        for agent_data in raw_data.get("agents", {}).values():
            try:
                agents.append(AgentRecord.from_dict(agent_data))
            except Exception as e:
                logger.warning("Failed to deserialize agent record: %s", e)
        return agents

    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        """Retrieves an agent by ID."""
        try:
            clean_id = validate_agent_id(agent_id)
        except ValueError:
            clean_id = agent_id.strip()

        raw_data = self._load_raw()
        data = raw_data.get("agents", {}).get(clean_id)
        if data:
            return AgentRecord.from_dict(data)
        return None

    def get_last_active_agent_id(self) -> Optional[str]:
        """Returns the ID of the last active agent, if any."""
        raw_data = self._load_raw()
        return raw_data.get("last_active_agent_id")

    def create_conversation_session(
        self,
        agent_id: str,
        environment_id: str,
        title: str = "New Chat",
    ) -> ConversationSession:
        """Creates and persists a new conversation session for an agent."""
        clean_id = validate_agent_id(agent_id)
        raw_data = self._load_raw()
        agent_data = raw_data.get("agents", {}).get(clean_id)
        if not agent_data:
            # Register placeholder agent record if not present
            self.register_agent(clean_id)
            raw_data = self._load_raw()
            agent_data = raw_data["agents"][clean_id]

        now_str = datetime.now().isoformat()
        session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        session = ConversationSession(
            session_id=session_id,
            agent_id=clean_id,
            environment_id=environment_id,
            created_at=now_str,
            updated_at=now_str,
            turn_count=0,
            title=title,
        )

        agent_data.setdefault("conversations", {})[session_id] = session.to_dict()
        self._save_raw(raw_data)
        logger.info("Created conversation session '%s' (env: %s) for agent '%s'", session_id, environment_id, clean_id)
        return session

    def update_conversation_session(
        self,
        agent_id: str,
        session_id: str,
        environment_id: Optional[str] = None,
        last_interaction_id: Optional[str] = None,
        increment_turn: bool = True,
        title: Optional[str] = None,
    ) -> Optional[ConversationSession]:
        """Updates turn count, environment_id, and interaction_id for an active session."""
        try:
            clean_id = validate_agent_id(agent_id)
        except ValueError:
            clean_id = agent_id

        raw_data = self._load_raw()
        agent_data = raw_data.get("agents", {}).get(clean_id)
        if not agent_data:
            return None

        conv_dict = agent_data.get("conversations", {}).get(session_id)
        if not conv_dict:
            return None

        session = ConversationSession.from_dict(conv_dict)
        if environment_id:
            session.environment_id = environment_id
        if last_interaction_id:
            session.last_interaction_id = last_interaction_id
        if increment_turn:
            session.turn_count += 1
        if title:
            session.title = title
        session.updated_at = datetime.now().isoformat()

        agent_data["conversations"][session_id] = session.to_dict()
        self._save_raw(raw_data)
        return session

    def list_conversations(self, agent_id: str) -> List[ConversationSession]:
        """Lists all conversation sessions for a given agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            return []
        sessions = []
        for s_data in agent.conversations.values():
            try:
                sessions.append(ConversationSession.from_dict(s_data))
            except Exception:
                pass
        # Sort by updated_at descending
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions
