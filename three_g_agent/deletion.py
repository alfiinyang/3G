"""Antigravity SDK Deletion Procedures for Agents and Interactions.

Provides standardized deletion workflows adhering strictly to the Google Antigravity SDK:
- Agent Deletion: invokes `client.agents.delete(id=agent_id)` and purges local registry definitions.
- Interaction Deletion: invokes `client.interactions.delete(id=interaction_id)` and clears session records.
- Session Deletion: manages the full teardown of conversation sessions, holding environment IDs,
  and associated interaction IDs.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .registry import AgentRegistry, validate_agent_id

logger = logging.getLogger("3G-agent.deletion")


@dataclass
class DeletionResult:
    """Encapsulates the outcome of an Antigravity deletion operation.

    Attributes:
        success: Whether the operation completed successfully (local and/or remote).
        target_type: "agent", "interaction", or "session".
        target_id: The identifier of the deleted entity.
        remote_deleted: Whether the Antigravity SDK remote deletion succeeded.
        local_deleted: Whether the local store/registry entry was removed.
        message: Human-readable summary of actions taken.
        warning: Optional details if remote SDK call encountered a notice (e.g. 404 Not Found).
    """
    success: bool
    target_type: str
    target_id: str
    remote_deleted: bool
    local_deleted: bool
    message: str
    warning: Optional[str] = None


class AgentDeletionManager:
    """Manages agent and interaction deletion following Antigravity SDK procedures."""

    @classmethod
    def _extract_sdk_client(cls, client_handle: Any) -> Optional[Any]:
        """Extracts the underlying SDK client object from an InitializedClient or raw client."""
        if hasattr(client_handle, "client"):
            return client_handle.client
        return client_handle

    @classmethod
    def delete_agent(
        cls,
        agent_id: str,
        client: Optional[Any] = None,
        registry: Optional[AgentRegistry] = None,
        state_dir: Optional[Union[str, Path]] = None,
    ) -> DeletionResult:
        """Deletes an Antigravity agent adhering to the SDK procedure.

        Steps:
        1. Validates and normalizes agent_id format [name-id_num].
        2. Calls Antigravity SDK `client.agents.delete(id=agent_id)` if live connection exists.
        3. Purges agent and associated conversation records from AgentRegistry.
        4. Cleans up associated local state records if present.

        Args:
            agent_id: The ID of the agent to delete.
            client: Optional InitializedClient or raw SDK client.
            registry: Optional AgentRegistry instance.
            state_dir: Optional state directory to resolve registry if none passed.

        Returns:
            DeletionResult with detailed status.
        """
        try:
            clean_id = validate_agent_id(agent_id)
        except ValueError:
            clean_id = agent_id.strip()

        logger.info("Initiating Antigravity SDK deletion procedure for agent '%s'...", clean_id)
        active_registry = registry or AgentRegistry(state_dir=state_dir or "./.3g_agent")

        remote_deleted = False
        warning = None

        # 1. Antigravity SDK Procedure: Delete remote agent
        sdk_client = cls._extract_sdk_client(client)
        if sdk_client and hasattr(sdk_client, "agents") and hasattr(sdk_client.agents, "delete"):
            try:
                logger.info("Executing client.agents.delete(id='%s')...", clean_id)
                sdk_client.agents.delete(id=clean_id)
                remote_deleted = True
                logger.info("Successfully deleted remote agent '%s' via Antigravity SDK.", clean_id)
            except Exception as sdk_err:
                err_msg = str(sdk_err)
                warning = f"SDK remote call: {err_msg}"
                logger.warning(
                    "Antigravity SDK remote deletion for agent '%s' returned: %s. "
                    "Proceeding with local registry purge.",
                    clean_id,
                    err_msg,
                )

        # 2. Local Registry Deletion
        local_deleted = active_registry.delete_agent(clean_id)

        success = local_deleted or remote_deleted
        message = (
            f"Agent '{clean_id}' successfully removed from registry."
            if local_deleted
            else f"Agent '{clean_id}' processed (remote: {remote_deleted}, local found: {local_deleted})."
        )

        return DeletionResult(
            success=success,
            target_type="agent",
            target_id=clean_id,
            remote_deleted=remote_deleted,
            local_deleted=local_deleted,
            message=message,
            warning=warning,
        )

    @classmethod
    def delete_interaction(
        cls,
        interaction_id: str,
        client: Optional[Any] = None,
        registry: Optional[AgentRegistry] = None,
        state_dir: Optional[Union[str, Path]] = None,
    ) -> DeletionResult:
        """Deletes an interaction according to Antigravity SDK procedure.

        Procedure:
        1. Calls Antigravity SDK `client.interactions.delete(id=interaction_id)`.
        2. Locates any conversation sessions holding this interaction ID and clears them.

        Args:
            interaction_id: The unique interaction ID to delete.
            client: Optional InitializedClient or raw SDK client.
            registry: Optional AgentRegistry instance.
            state_dir: Optional state directory.

        Returns:
            DeletionResult with outcome.
        """
        clean_inter_id = interaction_id.strip()
        logger.info("Initiating Antigravity SDK deletion for interaction '%s'...", clean_inter_id)
        active_registry = registry or AgentRegistry(state_dir=state_dir or "./.3g_agent")

        remote_deleted = False
        warning = None

        # 1. Antigravity SDK Procedure: Delete remote interaction
        sdk_client = cls._extract_sdk_client(client)
        if sdk_client and hasattr(sdk_client, "interactions") and hasattr(sdk_client.interactions, "delete"):
            try:
                logger.info("Executing client.interactions.delete(id='%s')...", clean_inter_id)
                sdk_client.interactions.delete(id=clean_inter_id)
                remote_deleted = True
                logger.info("Successfully deleted remote interaction '%s' via Antigravity SDK.", clean_inter_id)
            except Exception as sdk_err:
                err_msg = str(sdk_err)
                warning = f"SDK remote call: {err_msg}"
                logger.warning(
                    "Antigravity SDK remote deletion for interaction '%s' returned: %s.",
                    clean_inter_id,
                    err_msg,
                )

        # 2. Local session cleanup
        match = active_registry.find_session_by_interaction_id(clean_inter_id)
        local_deleted = False
        if match:
            agent_id, session = match
            local_deleted = active_registry.delete_conversation_session(agent_id, session.session_id)

        success = remote_deleted or local_deleted
        message = (
            f"Interaction '{clean_inter_id}' deleted."
            if success
            else f"Interaction '{clean_inter_id}' could not be found locally or remotely."
        )

        return DeletionResult(
            success=success,
            target_type="interaction",
            target_id=clean_inter_id,
            remote_deleted=remote_deleted,
            local_deleted=local_deleted,
            message=message,
            warning=warning,
        )

    @classmethod
    def delete_conversation_session(
        cls,
        agent_id: str,
        session_id: str,
        client: Optional[Any] = None,
        registry: Optional[AgentRegistry] = None,
        state_dir: Optional[Union[str, Path]] = None,
    ) -> DeletionResult:
        """Deletes a conversation session, its held remote interaction, and environment."""
        active_registry = registry or AgentRegistry(state_dir=state_dir or "./.3g_agent")
        session = active_registry.get_conversation_session(agent_id, session_id)

        sdk_client = cls._extract_sdk_client(client)
        remote_interaction_deleted = False
        remote_env_deleted = False
        warnings = []

        if session:
            # Delete remote interaction if held
            if session.last_interaction_id and sdk_client and hasattr(sdk_client, "interactions"):
                try:
                    sdk_client.interactions.delete(id=session.last_interaction_id)
                    remote_interaction_deleted = True
                except Exception as e:
                    warnings.append(f"Interaction delete: {e}")

            # Delete remote environment container if held
            if session.environment_id and sdk_client and hasattr(sdk_client, "environments") and hasattr(sdk_client.environments, "delete"):
                try:
                    sdk_client.environments.delete(id=session.environment_id)
                    remote_env_deleted = True
                except Exception as e:
                    warnings.append(f"Environment delete: {e}")

        local_deleted = active_registry.delete_conversation_session(agent_id, session_id)

        warning_str = "; ".join(warnings) if warnings else None
        return DeletionResult(
            success=local_deleted or remote_interaction_deleted,
            target_type="session",
            target_id=session_id,
            remote_deleted=remote_interaction_deleted or remote_env_deleted,
            local_deleted=local_deleted,
            message=f"Session '{session_id}' for agent '{agent_id}' deleted.",
            warning=warning_str,
        )

    @classmethod
    def display_result(cls, result: DeletionResult) -> None:
        """Displays formatted summary of deletion results in terminal."""
        print("\n" + "=" * 65)
        if result.success:
            print(f"  [+] {result.target_type.capitalize()} Deletion Successful")
        else:
            print(f"  [-] {result.target_type.capitalize()} Deletion Not Completed")
        print("=" * 65)
        print(f"  Target ID       : {result.target_id}")
        print(f"  Type            : {result.target_type}")
        print(f"  Remote SDK Call : {'✔ Succeeded (client.{result.target_type}s.delete)' if result.remote_deleted else 'Omitted / Not Found'}")
        print(f"  Local Registry  : {'✔ Record purged' if result.local_deleted else 'Not found in registry'}")
        if result.warning:
            print(f"  Note            : {result.warning}")
        print("=" * 65)
