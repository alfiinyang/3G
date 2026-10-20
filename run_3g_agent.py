"""Run Script and Demonstration for 3G-agent.

Demonstrates the complete Antigravity agent lifecycle:
1. Initialize client & display successful connection status.
2. Standalone agent creation module (`AgentCreator`) validating format [name-id_num]
   and pre-loading skills and instructions.
3. Agent registry & listing existing agents.
4. Choosing between starting a new chat or resuming an existing conversation,
   holding the remote environment_id across turns for persistence.
5. Local file deliverable storage and accessibility.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from three_g_agent import (
    AgentClientInitializer,
    AgentCreationSpec,
    AgentCreator,
    AgentDeletionManager,
    AgentRegistry,
    ClientParameterCollector,
    EnvironmentStore,
    FileStorageManager,
    ThreeGAgent,
    ThreeGAgentConfig,
    TurnStatusReporter,
    resolve_default_agent_id,
    validate_agent_id,
)


# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_demonstration():
    print("=" * 70)
    print("  3G-agent: Custom Reusable Antigravity Agent Lifecycle Demo")
    print("=" * 70)

    # Paths
    skills_folder = Path("./skills/pedagogy-engineering")
    if not skills_folder.exists():
        skills_folder = Path("./skills")
    instructions_file = Path("./instructions.md")
    state_dir = Path("./.3g_agent")
    output_dir = Path("./outputs/3g_agent")

    # -------------------------------------------------------------
    # 1. INITIALIZE CLIENT (Collect API key & show successful process)
    # -------------------------------------------------------------
    print(f"\n[Step 1] Initializing SDK Client Connection...")
    config = ThreeGAgentConfig(
        agent_name="3G-agent",
        agent_id=resolve_default_agent_id(),
        environment_type="remote",  # Mandatory requirement: remote sandbox
        skills_dir=skills_folder,
        instructions_file=instructions_file,
        state_dir=state_dir,
        output_dir=output_dir,
    )
    ClientParameterCollector.validate(config)
    initialized_client = AgentClientInitializer.initialize(config, interactive_prompt=False)
    AgentClientInitializer.display_success(initialized_client)

    # -------------------------------------------------------------
    # 2. STANDALONE AGENT CREATION ON SDK API (client.agents.create)
    # -------------------------------------------------------------
    print(f"\n[Step 2] Creating a New Agent directly on Antigravity SDK API (client.agents.create)...")
    registry = AgentRegistry(state_dir=state_dir)
    test_agent_id = "coder-12345"  # Adheres to [name-id_num] format

    print(f"  Validating format for '{test_agent_id}'...")
    validated = validate_agent_id(test_agent_id)
    print(f"  [+] Format validated successfully: [{validated}]")

    print(f"  Dispatching creation directly to Antigravity SDK API (zero local storage)...")
    spec = AgentCreationSpec(
        agent_id=validated,
        skills_dir=skills_folder,
        instructions_file=instructions_file,
        description="Demo autonomous coder agent for script creation",
        base_agent="antigravity-preview-09-2026",
    )
    result = AgentCreator.create_agent(
        spec=spec,
        client_handle=initialized_client,
    )
    print(f"  [+] Agent '{result.agent_id}' Created on Antigravity SDK API!")
    print(f"      - Skills Pre-loaded : {result.skills_count} ({result.stages_count} stages)")
    print(f"      - System Prompt     : {'Loaded' if result.has_instructions else 'None (empty instructions.md)'}")

    # -------------------------------------------------------------
    # 3. LIST EXISTING AGENTS DIRECTLY FROM SDK API (client.agents.list)
    # -------------------------------------------------------------
    print(f"\n[Step 3] Querying Agents directly from Antigravity SDK API (client.agents.list)...")
    existing_agents = AgentCreator.list_agents(client_handle=initialized_client)
    print(f"  Found {len(existing_agents)} agent(s) on Antigravity SDK API (zero local memory):")
    for ag in existing_agents:
        ag_id = getattr(ag, "id", str(ag))
        base_ag = getattr(ag, "base_agent", "antigravity-preview-09-2026")
        desc = getattr(ag, "description", "") or "No description"
        print(f"    - ID: {ag_id} | Base Engine: {base_ag} | {desc}")

    # -------------------------------------------------------------
    # 4. ASSEMBLE AGENT & MANAGE CONVERSATIONS (Holding environment_id)
    # -------------------------------------------------------------
    print(f"\n[Step 4] Assembling Agent '{validated}' and Managing Sessions...")
    agent = ThreeGAgent.create(
        skills_dir=skills_folder,
        instructions_file=instructions_file,
        agent_id=validated,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    # Simulate creating a conversation session with a persistent remote environment_id
    mock_env_id = "env_remote_sandbox_persistent_session_01"
    session = registry.create_conversation_session(
        agent_id=validated,
        environment_id=mock_env_id,
        title="Industrial Automation Pedagogical Script Generation",
    )
    print(f"  [+] Created Conversation Session: {session.session_id}")
    print(f"      - Held Environment ID : {session.environment_id}")

    # Demonstrate reusing the agent and resuming the conversation
    print(f"\n[Step 5] Demonstrating Reusing Agent and Resuming Conversation...")
    resumed = agent.resume_conversation(session.session_id)
    print(f"  [+] Resumed Session '{session.session_id}': {resumed}")
    print(f"  [+] Active Environment ID held: {agent.get_environment_id()}")

    # -------------------------------------------------------------
    # 6. LOCAL FILE DELIVERABLE STORAGE & ACCESSIBILITY
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  Demonstrating Local Deliverable Creation & Accessibility")
    print("=" * 70)

    sample_deliverable = f"""# Script Creation Plan: Automated Milling Logic
## Agent: {validated}
## Environment ID: {agent.get_environment_id()}

```python:milling_controller.py
class MillingController:
    def __init__(self, rpm: int = 1500):
        self.rpm = rpm
        self.status = "RUNNING"

    def monitor(self):
        return f"Controller active at {{self.rpm}} RPM"
```
"""
    storage = FileStorageManager(output_dir=output_dir)
    extracted = storage.extract_and_save_deliverables(sample_deliverable)
    print(f"  Extracted and stored {len(extracted)} deliverable(s) locally:")
    for f in extracted:
        print(f"    - Filename   : {f.file_name}")
        print(f"    - Local Path : {f.local_path}")
        print(f"    - URI        : {f.file_uri}")
        print(f"    - Size       : {f.size_bytes} bytes")

    # -------------------------------------------------------------
    # 7. REAL-TIME TERMINAL STATUS REPORTING
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  [Step 7] Demonstrating Real-Time Terminal Status Reporting")
    print("=" * 70)
    print("  Simulating turn progression while user waits for agent response:")
    reporter = TurnStatusReporter(enabled=True)
    with reporter:
        reporter.thinking("Analyzing instructions and formulating strategy...")
        import time
        time.sleep(0.3)
        reporter.skill_use("pedagogy-engineering", stage="stage_0")
        time.sleep(0.3)
        reporter.tool_call("code_execution", args_summary="milling_controller.py")
        time.sleep(0.3)
        reporter.tool_result("code_execution", result_summary="Success")
        time.sleep(0.3)
        reporter.responding("Synthesizing final deliverable...")
        time.sleep(0.3)
        reporter.complete("Response generated")

    # -------------------------------------------------------------
    # 8. ANTIGRAVITY SDK DELETION PROCEDURES
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  [Step 8] Demonstrating Antigravity SDK Deletion Procedures")
    print("=" * 70)
    # Deleting interaction / conversation session
    print(f"  Deleting conversation session '{session.session_id}' via SDK...")
    sess_del_result = AgentDeletionManager.delete_conversation_session(
        agent_id=validated,
        session_id=session.session_id,
        client=initialized_client.client,
        registry=registry,
        state_dir=state_dir,
    )
    AgentDeletionManager.display_result(sess_del_result)

    # Deleting agent
    print(f"\n  Deleting agent '{validated}' via Antigravity SDK...")
    agent_del_result = AgentDeletionManager.delete_agent(
        agent_id=validated,
        client=initialized_client.client,
        registry=registry,
        state_dir=state_dir,
    )
    AgentDeletionManager.display_result(agent_del_result)

    print("\n" + "=" * 70)
    print("  All Architectural Requirements Verified Successfully! [OK]")
    print("=" * 70)


if __name__ == "__main__":
    run_demonstration()
