"""Command-Line Interface (CLI) for 3G-agent.

Allows running 3G-agent interactively or running single-shot tasks with custom skills folders.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .agent import ThreeGAgent
from .config import ClientParameterCollector, ThreeGAgentConfig


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
        "--model",
        "-m",
        type=str,
        default="antigravity-preview-09-2026",
        help="Model or agent identifier (default: antigravity-preview-09-2026)",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Single prompt to execute. If omitted, starts an interactive chat loop.",
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
        default="./instructions.md",
        help="Path to instructions.md holding system prompt (default: ./instructions.md)",
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


def main() -> int:
    """Main CLI execution routine."""
    parser = build_parser()
    args = parser.parse_args()

    skills_path = Path(args.skills).resolve()
    instructions_path = Path(args.instructions).resolve() if args.instructions else None

    print("=" * 65)
    print(" [*] 3G-agent | Custom Antigravity Agent")
    print("=" * 65)
    print(f"Skills Folder  : {skills_path}")
    print(f"Instructions   : {instructions_path} ({'exists' if instructions_path and instructions_path.is_file() else 'not found'})")
    print(f"Output Storage : {Path(args.output_dir).resolve()}")
    print(f"State Storage  : {Path(args.state_dir).resolve()}")
    print(f"Target Model   : {args.model}")
    print(f"Environment    : remote (managed isolated sandbox)")

    try:
        agent = ThreeGAgent.create(
            skills_dir=skills_path,
            instructions_file=instructions_path,
            model_name=args.model,
            state_dir=args.state_dir,
            output_dir=args.output_dir,
        )
    except Exception as e:
        print(f"\n[!] Initialization Error: {e}", file=sys.stderr)
        return 1

    # Check instructions loaded
    loaded_instructions = agent.config.load_instructions()
    if loaded_instructions:
        print(f"\n[+] System Prompt Loaded from {agent.config.instructions_file.name} ({len(loaded_instructions)} chars)")
    else:
        print(f"\n[-] Instructions File ({agent.config.instructions_file.name if agent.config.instructions_file else 'none'}): empty or not provided (no system prompt override)")

    # Print skills discovered
    print(f"\nDiscovered Skills ({len(agent.skills.skills)}):")
    for s in agent.skills.skills:
        print(f"  - {s.name}: {s.description[:80]}...")
        if s.auxiliary_files:
            print(f"    |-- {len(s.auxiliary_files)} stages/resources found.")

    # Show active environment
    active_env = agent.get_environment_id()
    if active_env:
        print(f"\nActive Remote Environment ID: {active_env}")
    else:
        print(f"\nNo active environment saved yet. (A new remote sandbox will be provisioned on execution)")

    if args.reset_env:
        agent.reset_environment()
        print("[+] Remote environment ID has been reset. A fresh container will be requested.")
        return 0

    if args.status:
        # Just printing status
        local_files = agent.list_local_files()
        print(f"\nLocally Stored Files ({len(local_files)}):")
        for f in local_files:
            print(f"  - {f['file_name']} ({f['size_bytes']} bytes) -> {f['file_uri']}")
        return 0

    # Specific stage execution
    if args.stage:
        stage_input = args.prompt or "Proceed with stage execution using provided context."
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
            print(f"\nEnvironment ID used: {response.environment_id}")
            if response.saved_files:
                print(f"\nFiles Stored Locally ({len(response.saved_files)}):")
                for sf in response.saved_files:
                    print(f"  - {sf.file_name} -> {sf.file_uri}")
            return 0
        except Exception as err:
            print(f"\n[!] Execution Failed: {err}", file=sys.stderr)
            return 1

    # Single-shot execution
    if args.prompt:
        print(f"\n[>] Executing Prompt: {args.prompt}...")
        try:
            response = agent.execute(args.prompt)
            print("\n--- Output ---")
            print(response.output_text)
            print(f"\nEnvironment ID: {response.environment_id}")
            if response.saved_files:
                print(f"\nFiles Stored Locally ({len(response.saved_files)}):")
                for sf in response.saved_files:
                    print(f"  - {sf.file_name} -> {sf.file_uri}")
            return 0
        except Exception as err:
            print(f"\n[!] Execution Failed: {err}", file=sys.stderr)
            return 1

    # Interactive Loop
    print("\nStarting Interactive Session with 3G-agent. Type 'exit' or 'quit' to end.\n" + "-" * 65)
    while True:
        try:
            user_msg = input("\n3G-agent > ").strip()
            if not user_msg:
                continue
            if user_msg.lower() in ("exit", "quit", "q"):
                print("Session ended.")
                break
            if user_msg.lower() == "/reset":
                agent.reset_environment()
                print("Environment reset.")
                continue

            response = agent.chat(user_msg)
            print("\n" + response.output_text)
            if response.saved_files:
                print("\n[Files saved locally:]")
                for f in response.saved_files:
                    print(f"  📁 {f.file_name} -> {f.local_path}")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break
        except Exception as loop_err:
            print(f"\nError: {loop_err}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
