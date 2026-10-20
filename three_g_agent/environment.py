"""Secure Remote Environment & Environment ID Management for 3G-agent.

Requirement:
"set environment to remote: securely keep the environment ID for future use."

This module manages the lifecycle and persistent storage of remote environment IDs,
enabling stateful multi-turn interactions and container reuse while enforcing
secure local storage policies.
"""

from __future__ import annotations

import json
import logging
import os
import stat
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("3G-agent.environment")


@dataclass
class EnvironmentState:
    """State record for a remote Antigravity sandbox environment."""
    environment_id: str
    agent_name: str
    created_at: str
    updated_at: str
    turn_count: int = 1
    status: str = "active"
    skills_signature: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data["metadata"] is None:
            data["metadata"] = {}
        return data


class EnvironmentStore:
    """Secure local manager for keeping remote sandbox Environment IDs."""

    def __init__(self, state_dir: Path | str = "./.3g_agent", agent_name: str = "3G-agent") -> None:
        self.state_dir = Path(state_dir)
        self.agent_name = agent_name
        self.state_file = self.state_dir / "environment_state.json"
        self._ensure_secure_state_dir()

    def _ensure_secure_state_dir(self) -> None:
        """Creates the state directory if missing and applies restricted permissions."""
        if not self.state_dir.exists():
            self.state_dir.mkdir(parents=True, exist_ok=True)
            # On POSIX, restrict access to owner only (rwx------)
            try:
                if os.name != "nt":
                    os.chmod(self.state_dir, stat.S_IRWXU)
            except Exception as e:
                logger.debug("Failed setting directory permissions: %s", e)

    def _apply_file_security(self, file_path: Path) -> None:
        """Restricts read/write access to the current user."""
        try:
            if os.name != "nt":
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception as e:
            logger.debug("Failed setting secure file permissions on %s: %s", file_path, e)

    def get_environment_id(self) -> Optional[str]:
        """Retrieves the active environment ID if present and active."""
        state = self.load_state()
        if state and state.status == "active":
            return state.environment_id
        return None

    def load_state(self) -> Optional[EnvironmentState]:
        """Loads and parses the persisted environment state from secure storage."""
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return EnvironmentState(
                environment_id=data["environment_id"],
                agent_name=data.get("agent_name", self.agent_name),
                created_at=data.get("created_at", ""),
                updated_at=data.get("updated_at", ""),
                turn_count=data.get("turn_count", 1),
                status=data.get("status", "active"),
                skills_signature=data.get("skills_signature"),
                metadata=data.get("metadata", {}),
            )
        except Exception as err:
            logger.error("Failed to load environment state from %s: %s", self.state_file, err)
            return None

    def save_environment_id(
        self,
        environment_id: str,
        skills_signature: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EnvironmentState:
        """Securely persists a remote environment ID for future use across turns.
        
        Args:
            environment_id: The remote container environment ID returned by the API.
            skills_signature: Optional hash/signature of loaded skills.
            metadata: Additional contextual metadata.
            
        Returns:
            The saved EnvironmentState object.
        """
        now = datetime.now(timezone.utc).isoformat()
        current_state = self.load_state()

        if current_state and current_state.environment_id == environment_id:
            # Updating existing environment turn
            state = EnvironmentState(
                environment_id=environment_id,
                agent_name=self.agent_name,
                created_at=current_state.created_at,
                updated_at=now,
                turn_count=current_state.turn_count + 1,
                status="active",
                skills_signature=skills_signature or current_state.skills_signature,
                metadata=metadata or current_state.metadata or {},
            )
        else:
            # New environment provisioned
            state = EnvironmentState(
                environment_id=environment_id,
                agent_name=self.agent_name,
                created_at=now,
                updated_at=now,
                turn_count=1,
                status="active",
                skills_signature=skills_signature,
                metadata=metadata or {},
            )

        # Secure write to disk
        self._ensure_secure_state_dir()
        temp_file = self.state_dir / "environment_state.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)

        self._apply_file_security(temp_file)
        temp_file.replace(self.state_file)
        self._apply_file_security(self.state_file)

        logger.info(
            "Securely stored remote Environment ID '%s' (turn %d) in %s",
            environment_id,
            state.turn_count,
            self.state_file,
        )
        return state

    def reset_environment(self) -> None:
        """Marks the current environment as reset so a new container is provisioned on next call."""
        state = self.load_state()
        if state:
            state.status = "reset"
            state.updated_at = datetime.now(timezone.utc).isoformat()
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state.to_dict(), f, indent=2)
            self._apply_file_security(self.state_file)
            logger.info("Environment '%s' marked as reset.", state.environment_id)
        elif self.state_file.exists():
            self.state_file.unlink()

    def build_environment_payload(
        self,
        sources: Optional[List[Dict[str, Any]]] = None,
        force_fresh: bool = False,
    ) -> Any:
        """Constructs the remote environment configuration payload for client.interactions.create.
        
        If an active environment ID already exists and force_fresh is False:
            Reuses the existing remote sandbox container to maintain state.
        Otherwise:
            Provisions a fresh remote container with initial sources mounted.
            
        Returns:
            Either an environment dictionary or environment ID string.
        """
        active_id = self.get_environment_id()

        if active_id and not force_fresh:
            logger.info("Reusing existing remote environment: %s", active_id)
            return active_id

        logger.info("Requesting fresh remote sandbox environment...")
        env_config: Dict[str, Any] = {"type": "remote"}
        if sources:
            env_config["sources"] = sources

        return env_config
