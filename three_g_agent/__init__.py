"""3G-agent: Custom Reusable Antigravity Agent Package.

Provides an autonomous agent using the Antigravity SDK with:
- Dedicated skill loading from folders (single skill or group of skills)
- Remote sandbox execution environment ("environment": "remote")
- Secure persistence and reuse of Environment IDs across turns
- Strict separation of parameter collection, model initialization, and execution
- Full local file accessibility and artifact management
"""

from .agent import ThreeGAgent, ThreeGAgentResponse, extract_interaction_text
from .config import (
    MODEL_BUILDER,
    MODEL_DESIGNER,
    MODEL_ORCHESTRATOR,
    ClientParameterCollector,
    ThreeGAgentConfig,
    canonicalize_model_name,
    resolve_default_agent_id,
)
from .creator import AgentCreationResult, AgentCreationSpec, AgentCreator
from .deletion import AgentDeletionManager, DeletionResult
from .environment import EnvironmentState, EnvironmentStore
from .initializer import AgentClientInitializer, InitializedClient, ModelInitializer
from .orchestrator import OrchestratorResponse, ThreeGOrchestrator, ValidationResult
from .registry import AgentRegistry, ConversationSession, SessionRegistry, validate_agent_id
from .skills import Skill, SkillFile, SkillLoader
from .status import TurnStatusReporter
from .storage import FileStorageManager, SavedFile
from .subagents import (
    BuilderSubagent,
    DesignerSubagent,
    SubagentConfig,
    SubagentYamlLoader,
)

__all__ = [
    "ThreeGAgent",
    "ThreeGAgentConfig",
    "ThreeGAgentResponse",
    "extract_interaction_text",
    "ThreeGOrchestrator",
    "OrchestratorResponse",
    "ValidationResult",
    "DesignerSubagent",
    "BuilderSubagent",
    "SubagentConfig",
    "SubagentYamlLoader",
    "MODEL_ORCHESTRATOR",
    "MODEL_DESIGNER",
    "MODEL_BUILDER",
    "canonicalize_model_name",
    "ClientParameterCollector",
    "AgentClientInitializer",
    "ModelInitializer",
    "InitializedClient",
    "AgentCreator",
    "AgentCreationSpec",
    "AgentCreationResult",
    "AgentRegistry",
    "SessionRegistry",
    "ConversationSession",
    "validate_agent_id",
    "AgentDeletionManager",
    "DeletionResult",
    "TurnStatusReporter",
    "EnvironmentStore",
    "EnvironmentState",
    "SkillLoader",
    "Skill",
    "SkillFile",
    "FileStorageManager",
    "SavedFile",
    "resolve_default_agent_id",
]

__version__ = "2.0.0"

