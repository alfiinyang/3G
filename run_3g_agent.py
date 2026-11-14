"""Run Script and Demonstration for 3G-agent Architecture.

Demonstrates:
1. Four Agents: 1 Orchestrator (Parent Agent) + 3 Subagents:
   - Pedagogy Engineer Subagent (PEDA): pedagogical curricula, objectives, rubrics
   - Learning Experience Engineer Subagent (LX): learner journey, scenes, tasks, narrative
   - Software Product Manager Subagent (PM): PRD, technical contracts, data models, state flow
2. Remote Preloaded Agents:
   - All agents sit in Antigravity SDK remote environment with instructions preloaded.
   - No skills employed (skills folder kept).
3. Shared Remote Environment Persistence:
   - Once environment id is obtained from orchestrator after first turn, it persists
     across turns and agents (environment = previous_turn.environment_id).
4. Turn ID Registry & Conversational Continuity:
   - Captures conversation id of each turn (turn.id) for each agent.
   - Used for continuity in next turn (previous_interaction_id = previous_turn.id).
   - Registry maintains continuity:
     * User <-> Orchestrator
     * Orchestrator <-> Pedagogy Engineer
     * Orchestrator <-> Learning Experience Engineer
     * Orchestrator <-> Software Product Manager
     * Always points to the last saved ID when continuing a conversation.
5. Structured Outputs & Clickable Local Links.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from three_g_agent import (
    AGENT_LEARNING_EXPERIENCE,
    AGENT_ORCHESTRATOR,
    AGENT_PEDAGOGY,
    AGENT_PRODUCT_MANAGER,
    MODEL_BUILDER,
    MODEL_DESIGNER,
    MODEL_ORCHESTRATOR,
    AgentClientInitializer,
    AgentCreationSpec,
    AgentCreator,
    AgentDeletionManager,
    AgentRegistry,
    EnvironmentStore,
    FileStorageManager,
    LearningExperienceSubagent,
    PedagogySubagent,
    ProductManagerSubagent,
    SubagentConfig,
    SubagentYamlLoader,
    ThreeGAgent,
    ThreeGAgentConfig,
    ThreeGAgentResponse,
    ThreeGOrchestrator,
    TurnIdRegistry,
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
    print("=" * 80)
    print("  3G-agent: Multi-Agent Architecture (Orchestrator + 3 Subagents: PEDA / LX / PM)")
    print("=" * 80)

    # Base paths
    skills_folder = Path("./skills")
    common_instr_dir = Path("./instructions")
    subagents_dir = Path("./subagents")
    state_dir = Path("./.3g_agent")
    outputs_dir = Path("./outputs")
    peda_outputs_dir = outputs_dir / "pedagogical_design"
    lx_outputs_dir = outputs_dir / "learning_experience_design"
    pm_outputs_dir = outputs_dir / "product_requirements"

    # -------------------------------------------------------------
    # 1. INITIALIZE ORCHESTRATOR AGENT IN CURRENT PROCESS
    # -------------------------------------------------------------
    print(f"\n[Step 1] Initializing Parent Orchestrator Agent in Current Process...")
    print(f"  - Orchestrator Agent ID : {AGENT_ORCHESTRATOR}")
    print(f"  - Orchestrator Brain    : {MODEL_ORCHESTRATOR}")
    print(f"  - Instructions Preloaded: Remote ({common_instr_dir / 'orch_instruction.md'})")
    print(f"  - Skills Status         : None employed (skills folder kept at {skills_folder})")
    print(f"  - Conversational Role   : Sole user-facing interface & coordinator")

    orchestrator = ThreeGOrchestrator(
        skills_dir=skills_folder,
        instructions_file=common_instr_dir / "orch_instruction.md",
        subagents_dir=subagents_dir,
        output_dir=outputs_dir,
        state_dir=state_dir,
        brain=MODEL_ORCHESTRATOR,
    )
    print(f"  [+] Orchestrator agent initialized successfully!")
    print(f"  [+] Shared Environment Store configured at: {state_dir}")
    print(f"  [+] Turn ID Continuity Registry configured at: {orchestrator.turn_registry.registry_file}")

    # -------------------------------------------------------------
    # 2. DISCOVER SUBAGENT YAML SPECIFICATIONS
    # -------------------------------------------------------------
    print(f"\n[Step 2] Discovering Declarative Subagent YAML Definitions in {subagents_dir}...")
    yaml_specs = SubagentYamlLoader.load_all(subagents_dir)
    print(f"  Found {len(yaml_specs)} subagent specification(s):")
    for name, spec in yaml_specs.items():
        instr_summary = spec.system_instruction_file.name if spec.system_instruction_file else "Preloaded Remotely"
        print(f"    - Agent: {name:30} | Brain: {spec.brain:15} | Instr: {instr_summary:25} | Skills: None")

    # -------------------------------------------------------------
    # 3. VERIFY INITIAL SUBAGENT LAZY ON-DEMAND STATUS
    # -------------------------------------------------------------
    print(f"\n[Step 3] Checking Initial Subagent Lifecycle State (Lazy Spin Up)...")
    print(f"  - Pedagogy Subagent Spun Up?           : {orchestrator.is_pedagogy_spun_up} (Decline premature spinup)")
    print(f"  - Learning Experience Subagent Spun Up?: {orchestrator.is_learning_experience_spun_up} (Decline premature spinup)")
    print(f"  - Product Manager Subagent Spun Up?    : {orchestrator.is_product_manager_spun_up} (Decline premature spinup)")

    # -------------------------------------------------------------
    # 4. SHARED ENVIRONMENT PERSISTENCE ACROSS AGENTS
    # -------------------------------------------------------------
    print(f"\n[Step 4] Simulating Turn 1: Orchestrator Establishes Shared Remote Environment...")
    turn1_env_id = "env_remote_gbl_sandbox_shared_001"
    orchestrator.environment.save_environment_id(turn1_env_id, metadata={"origin": "orchestrator_turn_1"})
    print(f"  [+] Turn 1 Environment ID captured from Orchestrator: {turn1_env_id}")

    # Spin up all 3 subagents on demand
    pedagogy = orchestrator.get_pedagogy_subagent()
    lx = orchestrator.get_learning_experience_subagent()
    pm = orchestrator.get_product_manager_subagent()

    print(f"\n  Checking Environment Persistence Across All 4 Agents:")
    print(f"    - Orchestrator        env_id: {orchestrator.environment.get_environment_id()}")
    print(f"    - Pedagogy Subagent   env_id: {pedagogy.environment.get_environment_id()}")
    print(f"    - LX Subagent         env_id: {lx.environment.get_environment_id()}")
    print(f"    - PM Subagent         env_id: {pm.environment.get_environment_id()}")

    assert (
        orchestrator.environment.get_environment_id()
        == pedagogy.environment.get_environment_id()
        == lx.environment.get_environment_id()
        == pm.environment.get_environment_id()
        == turn1_env_id
    ), "All agents must share the exact same remote environment ID!"
    print(f"  [+] Verified: Environment persisted across turns and all agents (environment = previous_turn.environment_id)!")

    # -------------------------------------------------------------
    # 5. TURN ID REGISTRY & CONVERSATIONAL CONTINUITY
    # -------------------------------------------------------------
    print(f"\n[Step 5] Demonstrating Turn ID Registry & Conversational Continuity (previous_interaction_id = previous_turn.id)...")
    turn_registry = orchestrator.turn_registry

    # 1. User <-> Orchestrator conversation
    orch_turn_1_id = "turn_orch_usr_1001"
    turn_registry.save_turn_id(AGENT_ORCHESTRATOR, orch_turn_1_id, metadata={"prompt": "User turn 1"})
    print(f"  [+] Captured User <-> Orchestrator Turn 1 ID: {orch_turn_1_id}")
    next_orch_prior_id = turn_registry.get_last_turn_id(AGENT_ORCHESTRATOR)
    print(f"      -> Next Orchestrator Turn will use previous_interaction_id = {next_orch_prior_id}")
    assert next_orch_prior_id == orch_turn_1_id

    # 2. Orchestrator <-> Pedagogy Engineer conversation
    peda_turn_1_id = "turn_peda_orch_2001"
    turn_registry.save_turn_id(AGENT_PEDAGOGY, peda_turn_1_id, metadata={"prompt": "Pedagogical curriculum request"})
    print(f"  [+] Captured Orchestrator <-> Pedagogy Turn 1 ID: {peda_turn_1_id}")
    next_peda_prior_id = turn_registry.get_last_turn_id(AGENT_PEDAGOGY)
    print(f"      -> Next Pedagogy Turn will use previous_interaction_id = {next_peda_prior_id}")
    assert next_peda_prior_id == peda_turn_1_id

    # 3. Orchestrator <-> Learning Experience Engineer conversation
    lx_turn_1_id = "turn_lx_orch_3001"
    turn_registry.save_turn_id(AGENT_LEARNING_EXPERIENCE, lx_turn_1_id, metadata={"prompt": "LX specification request"})
    print(f"  [+] Captured Orchestrator <-> LX Turn 1 ID: {lx_turn_1_id}")
    next_lx_prior_id = turn_registry.get_last_turn_id(AGENT_LEARNING_EXPERIENCE)
    print(f"      -> Next LX Turn will use previous_interaction_id = {next_lx_prior_id}")
    assert next_lx_prior_id == lx_turn_1_id

    # 4. Orchestrator <-> Software Product Manager conversation
    pm_turn_1_id = "turn_pm_orch_4001"
    turn_registry.save_turn_id(AGENT_PRODUCT_MANAGER, pm_turn_1_id, metadata={"prompt": "PRD specification request"})
    print(f"  [+] Captured Orchestrator <-> PM Turn 1 ID: {pm_turn_1_id}")
    next_pm_prior_id = turn_registry.get_last_turn_id(AGENT_PRODUCT_MANAGER)
    print(f"      -> Next PM Turn will use previous_interaction_id = {next_pm_prior_id}")
    assert next_pm_prior_id == pm_turn_1_id

    # Verify second turn continuity
    peda_turn_2_id = "turn_peda_orch_2002"
    turn_registry.save_turn_id(AGENT_PEDAGOGY, peda_turn_2_id, metadata={"prompt": "Refine Bloom objectives"})
    updated_peda_id = turn_registry.get_last_turn_id(AGENT_PEDAGOGY)
    print(f"  [+] Turn 2 for Pedagogy completed -> Registry now points to latest: {updated_peda_id}")
    assert updated_peda_id == peda_turn_2_id

    # -------------------------------------------------------------
    # 6. SIMULATED DELIVERABLES ACROSS 3 SUBAGENTS
    # -------------------------------------------------------------
    print(f"\n[Step 6] Storing & Validating Subagent Deliverables Locally...")

    # 1. Pedagogy deliverable
    peda_mgr = FileStorageManager(output_dir=peda_outputs_dir)
    sample_peda = (
        "# Pedagogical Architecture: Industrial Milling Automation\n"
        "## Section A: Learning Plan Metadata\n"
        "- Audience: Industrial Milling Operators\n"
        "## Section E: Learning Objectives\n"
        "- LO-01: Calibrate feed-rate anomalies under variable flour density.\n"
    )
    saved_peda = peda_mgr.save_file("industrial_milling_pedagogy_spec.md", sample_peda)
    print(f"  [+] Pedagogy Deliverable: {saved_peda.local_path} ({saved_peda.file_uri})")

    # 2. LX deliverable
    lx_mgr = FileStorageManager(output_dir=lx_outputs_dir)
    sample_lx = (
        "# Learner-Experience Specification: Industrial Milling Simulation\n"
        "## Section 1: Document Metadata\n"
        "## Section 5: Learner Journey and Scene Structure\n"
        "- SC-01: Mill Intake Station\n"
        "- SC-02: Roller Calibration Chamber\n"
    )
    saved_lx = lx_mgr.save_file("industrial_milling_lx_spec.md", sample_lx)
    print(f"  [+] LX Deliverable       : {saved_lx.local_path} ({saved_lx.file_uri})")

    # 3. PM deliverable
    pm_mgr = FileStorageManager(output_dir=pm_outputs_dir)
    sample_pm = (
        "# Software Engineering PRD: Industrial Milling Simulation\n"
        "## Section 1: Document Metadata\n"
        "## Section 5: Functional Requirements\n"
        "- FR-001: Roller Gap Valve Feedback Controller\n"
        "## Section 14: Acceptance Criteria\n"
        "- AC-001: Feed rate regulates within 2% variance.\n"
    )
    saved_pm = pm_mgr.save_file("industrial_milling_prd.md", sample_pm)
    print(f"  [+] PM Deliverable       : {saved_pm.local_path} ({saved_pm.file_uri})")

    # -------------------------------------------------------------
    # 7. ORCHESTRATOR VALIDATION & CLICKABLE LINKS
    # -------------------------------------------------------------
    print(f"\n[Step 7] Orchestrator Output Validation across All 3 Subagents...")
    mock_peda_resp = ThreeGAgentResponse(
        output_text=sample_peda,
        environment_id=turn1_env_id,
        interaction_id=peda_turn_2_id,
        saved_files=[saved_peda],
    )
    mock_lx_resp = ThreeGAgentResponse(
        output_text=sample_lx,
        environment_id=turn1_env_id,
        interaction_id=lx_turn_1_id,
        saved_files=[saved_lx],
    )
    mock_pm_resp = ThreeGAgentResponse(
        output_text=sample_pm,
        environment_id=turn1_env_id,
        interaction_id=pm_turn_1_id,
        saved_files=[saved_pm],
    )

    val_peda = orchestrator.validate_output("pedagogical objectives", mock_peda_resp, "pedagogy")
    val_lx = orchestrator.validate_output("learner experience journey", mock_lx_resp, "lx")
    val_pm = orchestrator.validate_output("software PRD requirements", mock_pm_resp, "pm")

    print(f"  - Pedagogy Validation: {val_peda.summary()}")
    print(f"  - LX Validation      : {val_lx.summary()}")
    print(f"  - PM Validation      : {val_pm.summary()}")

    assert val_peda.is_valid and val_lx.is_valid and val_pm.is_valid

    # -------------------------------------------------------------
    # 8. REGISTRY STATE SUMMARY
    # -------------------------------------------------------------
    print(f"\n[Step 8] Turn ID Registry Inspection:")
    all_turns = turn_registry.get_all_records()
    for agent_name, record in all_turns.items():
        print(f"  - Agent: {agent_name:30} | Last Turn ID: {record.last_turn_id:25} | Turns: {record.turn_count}")

    print("\n" + "=" * 80)
    print("  All Architectural Requirements Verified Successfully! [OK]")
    print("=" * 80)


if __name__ == "__main__":
    run_demonstration()
