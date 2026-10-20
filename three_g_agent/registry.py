"""Session Persistence and Environment Store for 3G-agent.

STRICT REMOTE AGENT ARCHITECTURE:
- Agents are created and listed exclusively via the Antigravity SDK API (`client.agents`).
- No agent definitions or agent catalogs are stored in local memory or local JSON files.
- This module strictly persists multi-turn conversation sessions and holds their associated
  remote environment IDs across turns.
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
    """Represents a conversation session holding a remote sandbox environment ID."""
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


class SessionRegistry:
    """Persistent store strictly for conversation sessions and held remote environment IDs.
    
    Agents themselves are NOT stored locally; agent listing and creation query
    the Antigravity SDK API directly.
    """

    def __init__(self, state_dir: Union[str, Path] = "./.3g_agent") -> None:
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.state_dir / "sessions_registry.json"
        self._ensure_sessions_file()

    def _ensure_sessions_file(self) -> None:
        """Initializes empty sessions file if missing."""
        if not self.sessions_file.exists():
            default_data = {
                "version": "2.0",
                "sessions": {},
                "last_active_session_id": None,
            }
            self._save_raw(default_data)

    def _load_raw(self) -> Dict[str, Any]:
        try:
            return json.loads(self.sessions_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Error reading sessions registry file: %s. Reinitializing.", e)
            return {"version": "2.0", "sessions": {}, "last_active_session_id": None}

    def _save_raw(self, data: Dict[str, Any]) -> None:
        self.sessions_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # -------------------------------------------------------------------------
    # AGENT OPERATIONS: QUERIED FROM ANTIGRAVITY SDK API (ZERO LOCAL MEMORY)
    # -------------------------------------------------------------------------

    def list_agents(self, client: Optional[Any] = None) -> List[Any]:
        """Lists agents directly from the Antigravity SDK API (`client.agents.list`).
        
        Zero local memory is used.
        """
        if not client:
            logger.debug("list_agents called without client; returning empty list.")
            return []

        sdk_client = getattr(client, "client", client)
        if hasattr(sdk_client, "agents") and hasattr(sdk_client.agents, "list"):
            try:
                res = sdk_client.agents.list()
                if hasattr(res, "agents"):
                    return list(res.agents)
                if isinstance(res, list):
                    return res
            except Exception as e:
                logger.error("SDK API client.agents.list error: %s", e)
        return []

    def get_agent(self, agent_id: str, client: Optional[Any] = None) -> Optional[Any]:
        """Retrieves an agent directly from the Antigravity SDK API (`client.agents.get`)."""
        if not client:
            return None

        sdk_client = getattr(client, "client", client)
        if hasattr(sdk_client, "agents") and hasattr(sdk_client.agents, "get"):
            try:
                clean_id = validate_agent_id(agent_id)
                return sdk_client.agents.get(id=clean_id)
            except Exception as e:
                logger.debug("SDK API client.agents.get error: %s", e)
        return None

    def register_agent(self, agent_id: str, **kwargs: Any) -> Any:
        """Deprecated: Agent definitions are created directly on the Antigravity SDK API."""
        clean_id = validate_agent_id(agent_id)
        logger.info("register_agent note: Agent '%s' is managed via Antigravity SDK API, not stored locally.", clean_id)
        return clean_id

    def delete_agent(self, agent_id: str, client: Optional[Any] = None) -> bool:
        """Deletes an agent via Antigravity SDK API and cleans up associated session records."""
        clean_id = validate_agent_id(agent_id)
        remote_deleted = False

        if client:
            sdk_client = getattr(client, "client", client)
            if hasattr(sdk_client, "agents") and hasattr(sdk_client.agents, "delete"):
                try:
                    sdk_client.agents.delete(id=clean_id)
                    remote_deleted = True
                except Exception as e:
                    logger.warning("Remote SDK delete agent error: %s", e)

        # Clear any local session records for this agent
        raw = self._load_raw()
        sessions = raw.get("sessions", {})
        to_del = [sid for sid, sdata in sessions.items() if sdata.get("agent_id") == clean_id]
        for sid in to_del:
            del sessions[sid]
        self._save_raw(raw)
        return remote_deleted or bool(to_del)

    # -------------------------------------------------------------------------
    # CONVERSATION SESSION PERSISTENCE (Holding remote environment_id across turns)
    # -------------------------------------------------------------------------

    def create_conversation_session(
        self,
        agent_id: str,
        environment_id: str,
        title: str = "New Chat",
    ) -> ConversationSession:
        """Creates and persists a new conversation session for an agent, holding the remote environment ID."""
        clean_id = validate_agent_id(agent_id)
        raw_data = self._load_raw()

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

        raw_data.setdefault("sessions", {})[session_id] = session.to_dict()
        raw_data["last_active_session_id"] = session_id
        self._save_raw(raw_data)
        logger.info(
            "Created conversation session '%s' (holding env: %s) for agent '%s'",
            session_id,
            environment_id,
            clean_id,
        )
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
        conv_dict = raw_data.get("sessions", {}).get(session_id)
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

        raw_data["sessions"][session_id] = session.to_dict()
        self._save_raw(raw_data)
        return session

    def get_conversation_session(self, agent_id: str, session_id: str) -> Optional[ConversationSession]:
        """Retrieves a specific conversation session."""
        raw_data = self._load_raw()
        conv_dict = raw_data.get("sessions", {}).get(session_id)
        if conv_dict:
            return ConversationSession.from_dict(conv_dict)
        return None

    def delete_conversation_session(self, agent_id: str, session_id: str) -> bool:
        """Deletes a conversation session from the local store."""
        raw_data = self._load_raw()
        sessions = raw_data.get("sessions", {})
        if session_id in sessions:
            del sessions[session_id]
            if raw_data.get("last_active_session_id") == session_id:
                raw_data["last_active_session_id"] = next(iter(sessions.keys())) if sessions else None
            self._save_raw(raw_data)
            logger.info("Deleted conversation session '%s'.", session_id)
            return True
        return False

    def list_conversations(self, agent_id: str) -> List[ConversationSession]:
        """Lists all conversation sessions for a given agent."""
        try:
            clean_id = validate_agent_id(agent_id)
        except ValueError:
            clean_id = agent_id

        raw_data = self._load_raw()
        sessions = []
        for s_data in raw_data.get("sessions", {}).values():
            if s_data.get("agent_id") == clean_id:
                try:
                    sessions.append(ConversationSession.from_dict(s_data))
                except Exception:
                    pass
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def list_all_sessions(self) -> List[ConversationSession]:
        """Lists all conversation sessions across all agents."""
        raw_data = self._load_raw()
        sessions = []
        for s_data in raw_data.get("sessions", {}).values():
            try:
                sessions.append(ConversationSession.from_dict(s_data))
            except Exception:
                pass
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def find_session_by_interaction_id(self, interaction_id: str) -> Optional[tuple[str, ConversationSession]]:
        """Finds (agent_id, session) across all sessions by interaction_id."""
        raw_data = self._load_raw()
        for s_data in raw_data.get("sessions", {}).values():
            if s_data.get("last_interaction_id") == interaction_id:
                return s_data.get("agent_id"), ConversationSession.from_dict(s_data)
        return None


# Backward-compatible alias
AgentRegistry = SessionRegistry
