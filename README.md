# 3G-agent: Custom Reusable Antigravity Agent

`3G-agent` is an autonomous, reusable AI agent built using the **Antigravity Python SDK** and **Google GenAI Interactions API**. It is designed specifically to operate inside managed remote sandbox environments, dynamically ingest modular skills (such as `pedagogy-engineering`), securely persist environment state across turns, and ensure immediate local file accessibility for all generated outputs.

---

## Key Architectural Principles

`3G-agent` strictly complies with all system requirements:

1. **Modular Skill Ingestion from Folder**:
   - Accepts a single skill folder or a directory containing a group of skills.
   - Automatically parses `SKILL.md` YAML frontmatter, loads progressive disclosure stages (e.g., all 22 stages of `pedagogy-engineering`), and mounts them as inline sources inside the remote sandbox container.
2. **Remote Sandbox Environment (`environment="remote"`)**:
   - Provisions an isolated, cloud-hosted Linux execution sandbox container.
3. **Secure Environment ID Persistence**:
   - The returned `environment_id` is automatically captured and securely stored in `.3g_agent/environment_state.json`.
   - On subsequent execution turns, `3G-agent` automatically reuses the existing container ID, preserving installed dependencies, working directories, and files across multi-turn sessions.
   - Supports explicit session resets via `.reset_environment()`.
4. **Strict Separation of Concerns**:
   - **Parameter Collection & Validation** (`three_g_agent/config.py`): Pure parameter parsing, validation, and defaults.
   - **Model & Client Initialization** (`three_g_agent/initializer.py`): Pure client instantiation and authentication without executing prompts or operations.
   - **Skill Discovery & Packaging** (`three_g_agent/skills.py`): Skill folder parsing and payload formatting.
   - **Environment Management** (`three_g_agent/environment.py`): Sandbox ID persistence and state lifecycle.
   - **Local File Accessibility** (`three_g_agent/storage.py`): Local disk persistence and file manifest index.
   - **Operational Engine** (`three_g_agent/agent.py`): Only runtime execution and multi-turn orchestration.
5. **Guaranteed Local File Accessibility**:
   - All deliverables, reports, code files, and artifacts produced by the agent are downloaded and stored locally under `./outputs/3g_agent/`.
   - Maintained with a local index manifest (`manifest.json`) and clickable `file://` URIs.

---

## Multi-Agent Architecture (Orchestrator / Designer / Builder)

`3G-agent` implements a decoupled multi-agent architecture with strict responsibilities:

1. **Parent Orchestrator Agent**:
   - **Brain (`agent_config.model`)**: `3.1 flash lite` (`gemini-3.1-flash-lite`).
   - **Lifecycle**: Created with the current process.
   - **Interface**: Sole user-facing facade; subagents remain internal.
   - **System Prompt**: Loaded from common directory (`instructions/orch_instruction.md`) using ANIR and affirmative action language.
   - **Role**: Ingests user requests, classifies intent, delegates tasks to subagents on demand, and validates outputs before presenting deliverables to user.

2. **Designer Subagent**:
   - **Brain (`agent_config.model`)**: `3.5 flash lite` (`gemini-3.5-flash-lite`).
   - **Lifecycle**: Spun up on-demand only when educational / pedagogical design is requested.
   - **Skills**: Preloaded with skills from `./skills` directory (`pedagogy-engineering`). Only the designer agent needs these custom skills.
   - **System Prompt**: Preloaded with `instructions/desi_instructions.md` (renamed from `instructions.md`) in ANIR with affirmative action language.
   - **Tool Constraints**: Confined strictly to file access tools (create, read, write, list); coding execution tools are disabled.
   - **Target Output Directory**: Deliverables saved strictly to `./outputs/design/`.

3. **Builder Subagent**:
   - **Brain (`agent_config.model`)**: `3.8 flash` (`gemini-3.8-flash`).
   - **Lifecycle**: Spun up on-demand only when it is time to build / implement.
   - **Skills**: None (custom skills unnecessary).
   - **System Prompt**: None (no specific system instruction).
   - **Tool Constraints**: Full coding and execution tools enabled.
   - **Target Output Directory**: Deliverables saved strictly to `./outputs/build/`.

4. **Shared Environment**:
   - All 3 agents share the exact same remote sandbox execution container (`environment_id`), maintaining context, files, and state across turns and across agent delegations.

5. **Affirmative Action Language & ANIR**:
   - System prompts strictly avoid negative phrasing (zero "DO NOT" / "DON'T" / "NEVER" commands) and employ affirmative action language (avoid, prevent, decline, confine, defer).
   - Prompts use Agent-Native Intermediate Representation (ANIR) with structured declarative blocks to prevent instruction bloating.

6. **Declarative Subagent YAML Definitions**:
   - Subagent specifications are placed in the `subagents/` directory (`designer.yaml`, `builder.yaml`, `orchestrator.yaml`).

---

## Architecture Diagram

```
                        +---------------------------+
                        |        USER REQUEST       |
                        +-------------+-------------+
                                      |
                                      v
                        +---------------------------+
                        |    Parent Orchestrator    |
                        |   (Brain: 3.1 flash lite) |
                        | [orch_instruction in ANIR]|
                        +------+-------------+------+
                               |             |
                 +-------------+             +-------------+
                 | (on demand)                             | (on demand)
                 v                                         v
   +---------------------------+             +---------------------------+
   |     Designer Subagent     |             |      Builder Subagent     |
   |   (Brain: 3.5 flash lite) |             |    (Brain: 3.8 flash)     |
   | - Skills: ./skills        |             | - Skills: None            |
   | - Prompt: desi_instruct.. |             | - Prompt: None            |
   | - Tools: File access only |             | - Tools: Full coding tools|
   +-------------+-------------+             +-------------+-------------+
                 |                                         |
                 v                                         v
   +---------------------------+             +---------------------------+
   |   /outputs/design/        |             |   /outputs/build/         |
   | (Pedagogical specs/plans) |             | (Executable code/scripts) |
   +-------------+-------------+             +-------------+-------------+
                 \                                         /
                  +-------------------+-------------------+
                                      | (Shared environment_id)
                                      v
                        +---------------------------+
                        |   Shared Remote Sandbox   |
                        |  (Cloud Container State)  |
                        +---------------------------+
```

---

## Directory Structure

```text
├── instructions/
│   ├── orch_instruction.md   # Orchestrator system prompt (ANIR, affirmative action)
│   └── desi_instructions.md   # Designer system prompt (ANIR, affirmative action)
├── subagents/
│   ├── designer.yaml         # Designer subagent YAML definition
│   ├── builder.yaml          # Builder subagent YAML definition
│   └── orchestrator.yaml     # Orchestrator YAML definition
├── outputs/
│   ├── design/               # Designer agent deliverables (.md curricula, rubrics)
│   └── build/                # Builder agent deliverables (.py scripts, code)
├── skills/
│   └── pedagogy-engineering/ # Custom pedagogy engineering skills
├── three_g_agent/
│   ├── orchestrator.py       # Parent Orchestrator agent & validation engine
│   ├── subagents.py          # Designer & Builder subagents and YAML loader
│   ├── config.py             # Configuration schema, model mappings & parameters
│   ├── agent.py              # Antigravity agent execution core
│   ├── environment.py        # Secure remote Environment ID store & lifecycle
│   ├── skills.py             # Skill discovery, YAML parsing, and remote mounting
│   ├── storage.py            # Local file accessibility & manifest manager
│   ├── initializer.py        # Strict model/client initialization factory
│   └── cli.py                # Command-line interface
├── run_3g_agent.py           # Demonstration script
├── test_three_g_agent.py     # Comprehensive automated test suite
├── requirements.txt          # Python package dependencies
└── README.md                 # Project documentation
```


---

## Installation

```bash
pip install -r requirements.txt
```

Set your Gemini API key (or authenticate via Google Cloud ADC):
```bash
# Windows PowerShell:
$env:GEMINI_API_KEY="your-api-key-here"

# Linux / macOS:
export GEMINI_API_KEY="your-api-key-here"
```

---

## Python Usage Example

```python
from pathlib import Path
from three_g_agent import ThreeGAgent

# 1. Instantiate 3G-agent with skills folder
agent = ThreeGAgent.create(
    skills_dir="./skills/pedagogy-engineering",
    model_name="antigravity-preview-09-2026",
    output_dir="./outputs/3g_agent",
    state_dir="./.3g_agent",
)

# 2. Execute an initial prompt (spawns remote sandbox and captures Environment ID)
response = agent.execute(
    "Perform Stage 0 intake for an industrial milling operator training programme."
)

print(response.output_text)
print(f"Persisted Environment ID: {response.environment_id}")

# 3. Access files stored locally
for saved_file in response.saved_files:
    print(f"Deliverable saved locally: {saved_file.file_name}")
    print(f"File URI: {saved_file.file_uri}")

# 4. Multi-turn continuation (automatically reuses the persistent remote container)
response_turn2 = agent.chat("Proceed to Stage 1 problem diagnosis.")
```

---

## CLI Usage

### Check Active Environment and Skills
```bash
python -m three_g_agent.cli --status
```

### Run a Specific Skill Stage (e.g. Stage 0)
```bash
python -m three_g_agent.cli --skill-name pedagogy-engineering --stage 0 --prompt "Target Audience: Chemical Engineering Apprentices"
```

### Start an Interactive Session
```bash
python -m three_g_agent.cli
```

### Reset Environment ID
```bash
python -m three_g_agent.cli --reset-env
```

---

## Running the Automated Test Suite

```bash
python -m unittest test_three_g_agent.py -v
```
All unit tests validate:
- Strictly separated parameter collection and model initialization.
- Ingestion of single and multi-file skills (including progressive stage files).
- Secure persistence and reuse of `environment_id`.
- Local file extraction, indexing, and accessibility.
