"""3G-agent: Custom Reusable Antigravity Agent Package.

Provides an autonomous agent using the Antigravity SDK with:
- Dedicated skill loading from folders (single skill or group of skills)
- Remote sandbox execution environment ("environment": "remote")
- Secure persistence and reuse of Environment IDs across turns
- Strict separation of parameter collection, model initialization, and execution
- Full local file accessibility and artifact management
"""

from .agent import ThreeGAgent, ThreeGAgentResponse
from .config import ClientParameterCollector, ThreeGAgentConfig
from .environment import EnvironmentState, EnvironmentStore
from .initializer import InitializedClient, ModelInitializer
from .skills import Skill, SkillFile, SkillLoader
from .storage import FileStorageManager, SavedFile

__all__ = [
    "ThreeGAgent",
    "ThreeGAgentConfig",
    "ThreeGAgentResponse",
    "ClientParameterCollector",
    "ModelInitializer",
    "InitializedClient",
    "EnvironmentStore",
    "EnvironmentState",
    "SkillLoader",
    "Skill",
    "SkillFile",
    "FileStorageManager",
    "SavedFile",
]

__version__ = "1.0.0"
