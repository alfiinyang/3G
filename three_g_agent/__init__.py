"""3G-agent: Custom Reusable Antigravity Agent Package.

Provides an autonomous agent using the Antigravity SDK with:
- Dedicated skill loading from folders (single skill or group of skills)
- Remote sandbox execution environment ("environment": "remote")
- Secure persistence and reuse of Environment IDs across turns
- Strict separation of parameter collection, model initialization, and execution
- Full local file accessibility and artifact management
"""

from .agent import ThreeGAgent, ThreeGAgentResponse
from .config import ClientParameterCollector, ThreeGAgentConfig, resolve_default_agent_id
from .creator import AgentCreationResult, AgentCreationSpec, AgentCreator
from .environment import EnvironmentState, EnvironmentStore
from .initializer import AgentClientInitializer, InitializedClient, ModelInitializer
from .registry import AgentRecord, AgentRegistry, ConversationSession, validate_agent_id
from .skills import Skill, SkillFile, SkillLoader
from .storage import FileStorageManager, SavedFile

__all__ = [
    "ThreeGAgent",
    "ThreeGAgentConfig",
    "ThreeGAgentResponse",
    "ClientParameterCollector",
    "AgentClientInitializer",
    "ModelInitializer",
    "InitializedClient",
    "AgentCreator",
    "AgentCreationSpec",
    "AgentCreationResult",
    "AgentRegistry",
    "AgentRecord",
    "ConversationSession",
    "validate_agent_id",
    "EnvironmentStore",
    "EnvironmentState",
    "SkillLoader",
    "Skill",
    "SkillFile",
    "FileStorageManager",
    "SavedFile",
    "resolve_default_agent_id",
]

__version__ = "1.0.0"
