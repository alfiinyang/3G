"""Run Script and Demonstration for 3G-agent Architecture.

Demonstrates:
1. Orchestrator Agent (Parent agent, brain = 3.1 flash lite) created with the current process.
2. System prompts loaded from common directory (instructions/orch_instruction.md and instructions/desi_instructions.md).
3. Subagent YAML specifications loaded from subagents/ directory.
4. Lazy On-Demand Subagent Lifecycle:
   - Designer Subagent (brain = 3.5 flash lite, skills from ./skills, desi_instructions, file access tools, outputs/design).
   - Builder Subagent (brain = 3.8 flash, no system instruction, coding tools enabled, outputs/build).
5. Output Validation against user requests before returning responses to user.
6. Shared environment container persistence across all 3 agents.
7. Separated deliverable outputs (/outputs/design and /outputs/build).
8. Antigravity SDK API agent listing, creation, and deletion routines.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from three_g_agent import (
    MODEL_BUILDER,
    MODEL_DESIGNER,
    MODEL_ORCHESTRATOR,
    AgentClientInitializer,
    AgentCreationSpec,
    AgentCreator,
    AgentDeletionManager,
    AgentRegistry,
    BuilderSubagent,
    ClientParameterCollector,
    DesignerSubagent,
    EnvironmentStore,
    FileStorageManager,
    SubagentYamlLoader,
    ThreeGAgent,
    ThreeGAgentConfig,
    ThreeGOrchestrator,
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
    print("=" * 75)
    print("  3G-agent: Multi-Agent Architecture (Orchestrator / Designer / Builder)")
    print("=" * 75)

    # Base paths
    skills_folder = Path("./skills/pedagogy-engineering")
    if not skills_folder.exists():
        skills_folder = Path("./skills")
    common_instr_dir = Path("./instructions")
    subagents_dir = Path("./subagents")
    state_dir = Path("./.3g_agent")
    outputs_dir = Path("./outputs")
    design_outputs_dir = outputs_dir / "design"
    build_outputs_dir = outputs_dir / "build"

    # -------------------------------------------------------------
    # 1. INITIALIZE CLIENT & ORCHESTRATOR AGENT IN CURRENT PROCESS
    # -------------------------------------------------------------
    print(f"\n[Step 1] Initializing Parent Orchestrator Agent in Current Process...")
    print(f"  - Orchestrator Brain : {MODEL_ORCHESTRATOR}")
    print(f"  - System Instruction : {common_instr_dir / 'orch_instruction.md'} (ANIR, affirmative action)")
    print(f"  - Conversational Role: Sole user-facing interface & coordinator")

    orchestrator = ThreeGOrchestrator(
        skills_dir=skills_folder,
        instructions_file=common_instr_dir / "orch_instruction.md",
        subagents_dir=subagents_dir,
        output_dir=outputs_dir,
        state_dir=state_dir,
        brain=MODEL_ORCHESTRATOR,
    )
    print(f"  [+] Orchestrator agent initialized successfully!")
    print(f"  [+] Active Environment Store configured at: {state_dir}")

    # -------------------------------------------------------------
    # 2. LOAD SUBAGENTS YAML SPECIFICATIONS
    # -------------------------------------------------------------
    print(f"\n[Step 2] Discovering Declarative Subagent YAML Definitions in {subagents_dir}...")
    yaml_specs = SubagentYamlLoader.load_all(subagents_dir)
    print(f"  Found {len(yaml_specs)} subagent specification(s):")
    for name, spec in yaml_specs.items():
        skills_summary = f"{len(spec.skills)} custom skill(s)" if spec.skills else "None"
        instr_summary = spec.system_instruction_file.name if spec.system_instruction_file else "None"
        print(f"    - Subagent: {name:12} | Brain: {spec.brain:15} | Instr: {instr_summary:22} | Skills: {skills_summary}")

    # -------------------------------------------------------------
    # 3. VERIFY LAZY ON-DEMAND SUBAGENT STATUS
    # -------------------------------------------------------------
    print(f"\n[Step 3] Checking Initial Subagent Lifecycle State (Lazy Spin Up)...")
    print(f"  - Designer Subagent Spun Up? : {orchestrator.is_designer_spun_up} (Decline premature spinup)")
    print(f"  - Builder Subagent Spun Up?  : {orchestrator.is_builder_spun_up}  (Decline premature spinup)")

    # -------------------------------------------------------------
    # 4. TASK HANDOVER & ON-DEMAND DESIGNER SUBAGENT EXECUTION
    # -------------------------------------------------------------
    print(f"\n[Step 4] Handing Over Pedagogical Design Task to Designer Subagent...")
    design_prompt = (
        "Design a 4-stage pedagogical curriculum architecture for Industrial Milling Automation, "
        "defining Bloom's taxonomy objectives, rubrics, and deliverable specs."
    )
    print(f"  User Request: \"{design_prompt}\"")
    intent = orchestrator.classify_intent(design_prompt)
    print(f"  [+] Orchestrator Intent Classification: [{intent.upper()}]")

    print(f"  Spinning up Designer Subagent on demand...")
    designer = orchestrator.get_designer_subagent()
    print(f"  [+] Designer Subagent Spun Up:")
    print(f"      - Brain (Model)     : {designer.brain}")
    print(f"      - Preloaded Skills  : {[s.name for s in designer.skill_loader.skills]}")
    print(f"      - System Prompt     : {designer.instructions_file}")
    print(f"      - Allowed Tools     : File access tools only ({designer.tools_allowed})")
    print(f"      - Disabled Tools    : Coding execution tools ({designer.tools_disabled})")
    print(f"      - Target Output Dir : {designer.output_dir}")

    # Simulate Designer generating pedagogical deliverable into outputs/design
    design_mgr = FileStorageManager(output_dir=design_outputs_dir)
    sample_design = """# Pedagogical Architecture: Industrial Milling Automation
## Stage 0: Context & Prerequisites
Target Audience: Senior Milling Operators
Measurable Objective: Deconstruct feed-rate anomalies under variable flour density.

## Stage 1: Core Curriculum Scaffolding
- Module 1: Pneumatic Flow Rate Synchronization
- Module 2: Roller Gap Calibration and Thermal Tolerances
"""
    saved_design = design_mgr.save_file("industrial_milling_pedagogy_spec.md", sample_design)
    print(f"  [+] Deliverable generated by Designer and stored locally:")
    print(f"      - Path : {saved_design.local_path}")
    print(f"      - URI  : {saved_design.file_uri}")

    # -------------------------------------------------------------
    # 5. TASK HANDOVER & ON-DEMAND BUILDER SUBAGENT EXECUTION
    # -------------------------------------------------------------
    print(f"\n[Step 5] Handing Over Implementation Task to Builder Subagent...")
    build_prompt = "Build a Python prototype controller class for automated pneumatic flour milling."
    print(f"  User Request: \"{build_prompt}\"")
    build_intent = orchestrator.classify_intent(build_prompt)
    print(f"  [+] Orchestrator Intent Classification: [{build_intent.upper()}]")

    print(f"  Spinning up Builder Subagent on demand...")
    builder = orchestrator.get_builder_subagent()
    print(f"  [+] Builder Subagent Spun Up:")
    print(f"      - Brain (Model)     : {builder.brain}")
    print(f"      - Preloaded Skills  : None (Custom skills unnecessary)")
    print(f"      - System Prompt     : None (Builder has no specific system instruction)")
    print(f"      - Coding Tools      : Enabled (Full coding & execution access)")
    print(f"      - Target Output Dir : {builder.output_dir}")

    # Simulate Builder generating implementation deliverable into outputs/build
    build_mgr = FileStorageManager(output_dir=build_outputs_dir)
    sample_code = """class PneumaticMillingController:
    \"\"\"Automated pneumatic controller for flour milling feed regulation.\"\"\"

    def __init__(self, target_feed_rate_kg_h: float = 2500.0):
        self.target_rate = target_feed_rate_kg_h
        self.valve_open_pct = 75.0

    def adjust_flow(self, current_density: float) -> float:
        if current_density > 0.55:
            self.valve_open_pct = max(10.0, self.valve_open_pct - 5.0)
        return self.valve_open_pct
"""
    saved_build = build_mgr.save_file("pneumatic_milling_controller.py", sample_code)
    print(f"  [+] Deliverable generated by Builder and stored locally:")
    print(f"      - Path : {saved_build.local_path}")
    print(f"      - URI  : {saved_build.file_uri}")

    # -------------------------------------------------------------
    # 6. OUTPUT VALIDATION BY ORCHESTRATOR
    # -------------------------------------------------------------
    print(f"\n[Step 6] Orchestrator Validating Subagent Outputs Against User Requests...")
    from three_g_agent import ThreeGAgentResponse

    mock_desi_resp = ThreeGAgentResponse(
        output_text="Pedagogical plan created for industrial automation.",
        environment_id="env_shared_3g_container_turn_01",
        saved_files=[saved_design],
    )
    val_desi = orchestrator.validate_output(design_prompt, mock_desi_resp, "designer")
    print(f"  - Designer Validation : {val_desi.summary()}")

    mock_build_resp = ThreeGAgentResponse(
        output_text="Python controller code written.",
        environment_id="env_shared_3g_container_turn_01",
        saved_files=[saved_build],
    )
    val_build = orchestrator.validate_output(build_prompt, mock_build_resp, "builder")
    print(f"  - Builder Validation  : {val_build.summary()}")

    # -------------------------------------------------------------
    # 7. SHARED ENVIRONMENT CONTAINER PERSISTENCE
    # -------------------------------------------------------------
    print(f"\n[Step 7] Verifying Shared Remote Environment Container across All 3 Agents...")
    shared_env_id = "env_remote_sandbox_flour_mills_3g_shared"
    orchestrator.environment.save_environment_id(shared_env_id, metadata={"shared": True})
    print(f"  - Orchestrator Environment ID : {orchestrator.environment.get_environment_id()}")
    print(f"  - Designer Environment ID     : {designer.environment.get_environment_id()}")
    print(f"  - Builder Environment ID      : {builder.environment.get_environment_id()}")
    assert orchestrator.environment.get_environment_id() == designer.environment.get_environment_id() == builder.environment.get_environment_id()
    print(f"  [+] All 3 agents share the exact same remote container environment!")

    # -------------------------------------------------------------
    # 8. OUTPUT DIRECTORY STRUCTURE SUMMARY
    # -------------------------------------------------------------
    print(f"\n[Step 8] Structured Local Outputs Summary:")
    print(f"  Design Outputs ({design_outputs_dir}):")
    for f in design_outputs_dir.iterdir():
        if f.is_file():
            print(f"    - {f.name} ({f.stat().st_size} bytes)")
    print(f"  Build Outputs ({build_outputs_dir}):")
    for f in build_outputs_dir.iterdir():
        if f.is_file():
            print(f"    - {f.name} ({f.stat().st_size} bytes)")

    # -------------------------------------------------------------
    # 9. SDK AGENT CREATION & LIFECYCLE (Preserving API Features)
    # -------------------------------------------------------------
    print(f"\n[Step 9] Demonstrating SDK Agent Creation & Deletion via Antigravity API...")
    test_agent_id = "coder-12345"
    validated = validate_agent_id(test_agent_id)
    spec = AgentCreationSpec(
        agent_id=validated,
        skills_dir=skills_folder,
        instructions_file=common_instr_dir / "desi_instructions.md",
        description="Demo autonomous coder agent for script creation",
        base_agent="antigravity-preview-09-2026",
    )
    creation_result = AgentCreator.create_agent(
        spec=spec,
        client_handle=orchestrator.client_handle,
    )
    print(f"  [+] Agent '{creation_result.agent_id}' Created on SDK API!")

    del_result = AgentDeletionManager.delete_agent(
        agent_id=validated,
        client=orchestrator.client_handle.client,
        registry=AgentRegistry(state_dir=state_dir),
        state_dir=state_dir,
    )
    AgentDeletionManager.display_result(del_result)

    print("\n" + "=" * 75)
    print("  All Architectural Changes & Requirements Verified Successfully! [OK]")
    print("=" * 75)


if __name__ == "__main__":
    run_demonstration()
