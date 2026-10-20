"""Command-Line Interface (CLI) for 3G-agent.

Features:
1. Client initialization with API key collection & status display.
2. Agent management: Options to either create a new agent or reuse an existing agent.
3. Standalone agent creation module integration with format validation ([name-id_num] e.g. [coder-12345])
   and pre-loaded skills & system instructions.
4. Conversation persistence: Reusing existing agents allows choosing between a new chat
   or an existing conversation, holding the remote environment_id across turns.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from .agent import ThreeGAgent
from .config import ClientParameterCollector, ThreeGAgentConfig, resolve_default_agent_id
from .creator import AgentCreationSpec, AgentCreator
from .initializer import AgentClientInitializer, InitializedClient
from .registry import AgentRecord, AgentRegistry, ConversationSession, validate_agent_id


# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def build_parser() -> argparse.ArgumentParser:
    """Builds argument parser for 3G-agent CLI."""
    parser = argparse.ArgumentParser(
        prog="3G-agent",
        description="3G-agent: Custom Reusable Antigravity Agent using Antigravity SDK",
    )
    parser.add_argument(
        "--skills",
        "-s",
        type=str,
        default="./skills",
        help="Path to folder containing a skill or group of skills (default: ./skills)",
    )
    parser.add_argument(
        "--agent",
        "-a",
        type=str,
        default=None,
        help="Antigravity agent identifier (format: [name-id_num] e.g. coder-12345)",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=None,
        help="Deprecated alias for --agent",
    )
    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        default=None,
        help="Gemini/Google Cloud API key (can also be set via GEMINI_API_KEY environment variable)",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        nargs="*",
        type=str,
        default=None,
        help="Prompt to execute without requiring quotation marks.",
    )
    parser.add_argument(
        "query",
        nargs="*",
        default=None,
        help="Optional prompt words passed directly on CLI without flags or quotation marks.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="./outputs/3g_agent",
        help="Directory where created files and artifacts are stored locally (default: ./outputs/3g_agent)",
    )
    parser.add_argument(
        "--instructions",
        "-i",
        type=str,
        default=None,
        help="Path to instructions.txt or instructions.md (default: auto-detected)",
    )
    parser.add_argument(
        "--state-dir",
        type=str,
        default="./.3g_agent",
        help="Directory to securely store environment IDs and session state (default: ./.3g_agent)",
    )
    parser.add_argument(
        "--reset-env",
        action="store_true",
        help="Reset any stored remote environment ID and start a fresh sandbox container.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show status of active environment ID and loaded skills without running a prompt.",
    )
    parser.add_argument(
        "--stage",
        type=str,
        help="Run a specific stage (e.g. --stage 0 or --stage stage_1) of a skill.",
    )
    parser.add_argument(
        "--skill-name",
        type=str,
        default="pedagogy-engineering",
        help="Name of skill when using --stage (default: pedagogy-engineering)",
    )
    return parser


def prompt_for_agent_creation(
    skills_path: Path,
    instructions_path: Optional[Path],
    client_handle: InitializedClient,
    registry: AgentRegistry,
) -> str:
    """Interactively prompts user to create a new agent with format validation."""
    print("\n" + "-" * 65)
    print("  [Step] Create a New Antigravity Agent")
    print("-" * 65)
    print("Requirement: Agent ID must follow format [name-id_num] e.g. coder-12345")

    while True:
        try:
            raw_input = input("\nEnter Agent ID (e.g. coder-12345): ").strip()
            if not raw_input:
                continue
            validated_id = validate_agent_id(raw_input)
            break
        except ValueError as val_err:
            print(f"[!] {val_err}")
            print("Please try again with a valid format (e.g. coder-12345, pedagogy-001).")

    description = input("Enter Agent Description (optional, press Enter to skip): ").strip() or None

    print(f"\n[>] Pre-loading skills from: {skills_path}...")
    print(f"[>] Pre-loading instructions from: {instructions_path}...")

    spec = AgentCreationSpec(
        agent_id=validated_id,
        skills_dir=skills_path,
        instructions_file=instructions_path,
        description=description,
        base_agent="antigravity-preview-09-2026",
    )

    result = AgentCreator.create_agent(
        spec=spec,
        client_handle=client_handle,
        registry=registry,
    )

    print("\n" + "=" * 65)
    print(f"  [+] Agent '{result.agent_id}' Successfully Created and Registered!")
    print("=" * 65)
    print(f"  Pre-loaded Skills      : {result.skills_count} package(s) ({result.stages_count} stages/auxiliary files)")
    print(f"  System Instructions    : {'Pre-loaded (' + str(result.instructions_length) + ' chars)' if result.has_instructions else 'None (empty instructions.md)'}")
    print(f"  Remote Engine          : antigravity-preview-09-2026")
    print(f"  Local Registry Record  : Confirmed in {registry.registry_file.name}")
    print("=" * 65)

    return result.agent_id


def prompt_for_agent_reuse(registry: AgentRegistry) -> Optional[str]:
    """Displays existing agents and prompts user to select one."""
    agents = registry.list_agents()
    if not agents:
        print("\n[-] No existing agents found in registry.")
        return None

    print("\n" + "-" * 65)
    print("  Existing Registered Antigravity Agents")
    print("-" * 65)
    for idx, ag in enumerate(agents, 1):
        conv_count = len(ag.conversations)
        skills_str = ", ".join(ag.skills_names) or "none"
        print(f"  [{idx}] ID: {ag.agent_id}")
        print(f"      - Created       : {ag.created_at[:19]}")
        print(f"      - Pre-loaded    : {len(ag.skills_names)} skill(s) [{skills_str}]")
        print(f"      - Conversations : {conv_count} recorded session(s)")

    while True:
        choice = input(f"\nSelect agent [1-{len(agents)}] or enter Agent ID: ").strip()
        if not choice:
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(agents):
            return agents[int(choice) - 1].agent_id
        # Check direct agent ID match
        clean_choice = choice.replace("[", "").replace("]", "").strip()
        matched = next((a for a in agents if a.agent_id == clean_choice), None)
        if matched:
            return matched.agent_id
        print(f"[!] Invalid selection '{choice}'. Please pick a number from 1 to {len(agents)}.")


def handle_conversation_selection(agent: ThreeGAgent) -> None:
    """Prompts user to choose between starting a new chat or resuming an existing conversation."""
    conversations = agent.list_conversations()
    print("\n" + "-" * 65)
    print(f"  Conversation Management for Agent: '{agent.config.agent_id}'")
    print("-" * 65)

    if not conversations:
        print("  [+] No existing conversations found for this agent.")
        print("  [+] Starting a fresh conversation (new remote sandbox environment will be provisioned).")
        agent.start_new_chat()
        return

    print("  [1] Start a New Chat (Provisions a fresh remote sandbox environment)")
    for idx, c in enumerate(conversations, 2):
        print(f"  [{idx}] Resume Conversation: {c.title}")
        print(f"      - Session ID     : {c.session_id}")
        print(f"      - Environment ID : {c.environment_id} (Holding for persistence)")
        print(f"      - Turns Recorded : {c.turn_count} turn(s)")
        print(f"      - Last Updated   : {c.updated_at[:19]}")

    while True:
        choice = input(f"\nSelect conversation option [1-{len(conversations) + 1}]: ").strip()
        if not choice:
            continue
        if choice == "1":
            print("\n[+] Starting a new chat session. Fresh environment will be created.")
            agent.start_new_chat()
            break
        if choice.isdigit() and 2 <= int(choice) <= len(conversations) + 1:
            selected_session = conversations[int(choice) - 2]
            success = agent.resume_conversation(selected_session.session_id)
            if success:
                print(f"\n[+] Successfully resumed conversation '{selected_session.session_id}'!")
                print(f"[+] Holding Environment ID '{selected_session.environment_id}' for persistence.")
            break
        print(f"[!] Please select a valid option between 1 and {len(conversations) + 1}.")


def main() -> int:
    """Main CLI execution routine."""
    parser = build_parser()
    args = parser.parse_args()

    # Parse prompt string from flags or positional tokens without requiring double quotes
    raw_prompt_tokens = args.prompt or args.query
    prompt_str = " ".join(raw_prompt_tokens).strip() if raw_prompt_tokens else None
    if prompt_str:
        if (prompt_str.startswith('"') and prompt_str.endswith('"')) or (prompt_str.startswith("'") and prompt_str.endswith("'")):
            prompt_str = prompt_str[1:-1].strip()

    skills_path = Path(args.skills).resolve()
    if args.instructions:
        instructions_path = Path(args.instructions).resolve()
    else:
        from .config import resolve_default_instructions_file
        instructions_path = resolve_default_instructions_file().resolve()

    state_dir = Path(args.state_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    registry = AgentRegistry(state_dir=state_dir)

    print("=" * 65)
    print(" [*] 3G-agent | Autonomous Antigravity Agent Orchestrator")
    print("=" * 65)

    # -------------------------------------------------------------
    # 1. INITIALIZE CLIENT (Collect API key & show successful process)
    # -------------------------------------------------------------
    is_interactive = not prompt_str and not args.stage and not args.status

    temp_config = ThreeGAgentConfig(
        agent_name="3G-agent",
        agent_id="antigravity-preview-09-2026",
        environment_type="remote",
        api_key=args.api_key,
        skills_dir=skills_path,
        instructions_file=instructions_path,
        state_dir=state_dir,
        output_dir=output_dir,
    )

    try:
        initialized_client = AgentClientInitializer.initialize(
            temp_config,
            interactive_prompt=is_interactive,
        )
        AgentClientInitializer.display_success(initialized_client)
    except Exception as init_err:
        print(f"\n[!] Client Initialization Failed: {init_err}", file=sys.stderr)
        return 1

    # Status only
    if args.status:
        agents = registry.list_agents()
        print(f"\nRegistered Agents ({len(agents)}):")
        for ag in agents:
            print(f"  - {ag.agent_id} ({len(ag.skills_names)} skills, {len(ag.conversations)} conversations)")
        return 0

    # -------------------------------------------------------------
    # 2. AGENT SELECTION: CREATE OR REUSE AGENT
    # -------------------------------------------------------------
    chosen_agent_id: Optional[str] = None

    # Check CLI argument override
    cli_specified_agent = args.agent or args.model
    if cli_specified_agent and cli_specified_agent.strip() not in ("1", "0", "true", "false"):
        try:
            chosen_agent_id = validate_agent_id(cli_specified_agent)
        except ValueError:
            chosen_agent_id = cli_specified_agent.strip()

    if not chosen_agent_id and is_interactive:
        print("\n" + "=" * 65)
        print("  Antigravity Agent Management")
        print("=" * 65)
        print("  [1] Create a new agent (pre-loads skills and instructions)")
        print("  [2] Reuse an existing agent (retains environment session)")

        while True:
            choice = input("\nSelect an option [1 or 2]: ").strip()
            if choice == "1":
                chosen_agent_id = prompt_for_agent_creation(
                    skills_path=skills_path,
                    instructions_path=instructions_path,
                    client_handle=initialized_client,
                    registry=registry,
                )
                break
            elif choice == "2":
                reused = prompt_for_agent_reuse(registry)
                if reused:
                    chosen_agent_id = reused
                    break
                else:
                    # No agents exist, fallback to creation
                    print("\nRouting to agent creation...")
                    chosen_agent_id = prompt_for_agent_creation(
                        skills_path=skills_path,
                        instructions_path=instructions_path,
                        client_handle=initialized_client,
                        registry=registry,
                    )
                    break
            else:
                print("[!] Please enter '1' to create a new agent or '2' to reuse an existing agent.")

    if not chosen_agent_id:
        chosen_agent_id = resolve_default_agent_id()

    # -------------------------------------------------------------
    # 3. ASSEMBLE 3G-AGENT
    # -------------------------------------------------------------
    try:
        agent = ThreeGAgent.create(
            skills_dir=skills_path,
            instructions_file=instructions_path,
            agent_id=chosen_agent_id,
            api_key=temp_config.api_key,
            state_dir=state_dir,
            output_dir=output_dir,
        )
        # Ensure agent is registered in local registry
        if not registry.get_agent(chosen_agent_id):
            registry.register_agent(
                agent_id=chosen_agent_id,
                description=f"Agent initialized with skills from {skills_path.name}",
                skills_names=[s.name for s in agent.skills.skills],
            )
    except Exception as e:
        print(f"\n[!] Failed to assemble agent '{chosen_agent_id}': {e}", file=sys.stderr)
        return 1

    if args.reset_env:
        agent.reset_environment()
        print(f"[+] Remote environment session for agent '{chosen_agent_id}' has been reset.")
        return 0

    # -------------------------------------------------------------
    # 4. REUSING AGENTS: CHOOSE NEW CHAT OR EXISTING CONVERSATION
    # -------------------------------------------------------------
    if is_interactive:
        handle_conversation_selection(agent)

    # -------------------------------------------------------------
    # 5. EXECUTION: SINGLE PROMPT, STAGE, OR INTERACTIVE LOOP
    # -------------------------------------------------------------
    if args.stage:
        stage_input = prompt_str or "Proceed with stage execution using provided context."
        print(f"\n[>] Executing Skill Stage: {args.skill_name} / {args.stage}...")
        try:
            response = agent.run_skill_stage(
                skill_name=args.skill_name,
                stage_identifier=args.stage,
                stage_input=stage_input,
                save_output_as=f"{args.skill_name}_{args.stage}_output.md",
            )
            print("\n--- Output ---")
            print(response.output_text)
            print(f"\nEnvironment ID: {response.environment_id}")
            if response.saved_files:
                print(f"\n[+] Created Artifact(s) Saved Locally ({len(response.saved_files)}):")
                for sf in response.saved_files:
                    print(f"  📁 {sf.file_name} ({sf.size_bytes} bytes) -> {sf.file_uri}")
            return 0
        except Exception as err:
            print(f"\n[!] Execution Failed: {err}", file=sys.stderr)
            return 1

    if prompt_str:
        print(f"\n[>] Executing Prompt for agent '{chosen_agent_id}': {prompt_str}...")
        try:
            response = agent.execute(prompt_str)
            print("\n--- Output ---")
            print(response.output_text)
            print(f"\nEnvironment ID: {response.environment_id}")
            if response.saved_files:
                print(f"\n[+] Created Artifact(s) Saved Locally ({len(response.saved_files)}):")
                for sf in response.saved_files:
                    print(f"  📁 {sf.file_name} ({sf.size_bytes} bytes) -> {sf.file_uri}")
            return 0
        except Exception as err:
            print(f"\n[!] Execution Failed: {err}", file=sys.stderr)
            return 1

    # Interactive chat loop
    active_env_id = agent.get_environment_id() or "(Container will be provisioned on first turn)"
    print("\n" + "=" * 65)
    print(f"  Session Active: Agent '{chosen_agent_id}'")
    print(f"  Session ID    : {agent.active_session_id or 'New Unsaved Session'}")
    print(f"  Environment ID: {active_env_id}")
    print(f"  Local Storage : {output_dir}")
    print("  Type 'exit' to quit, '/reset' to clear sandbox container.")
    print("  (Type your instructions directly without needing quotation marks)")
    print("=" * 65)

    while True:
        try:
            user_msg = input(f"\n{chosen_agent_id} > ").strip()
            if not user_msg:
                continue
            # Strip accidental outer double/single quotes so user can interact naturally
            if (user_msg.startswith('"') and user_msg.endswith('"')) or (user_msg.startswith("'") and user_msg.endswith("'")):
                user_msg = user_msg[1:-1].strip()

            if user_msg.lower() in ("exit", "quit", "q"):
                print("Session ended.")
                break
            if user_msg.lower() == "/reset":
                agent.reset_environment()
                print("[+] Environment reset. Next turn will spawn a fresh remote container.")
                continue

            response = agent.chat(user_msg)
            print("\n" + response.output_text)
            print(f"\n[Held Environment ID: {response.environment_id} | Session: {response.session_id}]")
            if response.saved_files:
                print(f"\n[+] Created Artifact(s) Saved Locally ({len(response.saved_files)}):")
                for f in response.saved_files:
                    print(f"  📁 {f.file_name} ({f.size_bytes} bytes) -> {f.file_uri}")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break
        except Exception as loop_err:
            print(f"\nError: {loop_err}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
