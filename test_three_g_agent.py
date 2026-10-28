"""Comprehensive Test Suite for 3G-agent.

Validates:
1. Parameter Collection & Validation (Separation of Concerns)
2. Model/Client Initialization (Strictly Separated from Execution)
3. Skill Loading & Packaging (Testing skills/pedagogy-engineering and auxiliary stages)
4. Remote Environment ID Persistence & Security (Testing EnvironmentStore)
5. Local File Accessibility & Artifact Management (Testing FileStorageManager)
6. ThreeGAgent Full Workflow Orchestration
"""

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from three_g_agent import (
    ThreeGAgent,
    ThreeGAgentConfig,
    ThreeGAgentResponse,
    ClientParameterCollector,
    AgentClientInitializer,
    ModelInitializer,
    EnvironmentStore,
    SkillLoader,
    FileStorageManager,
    SavedFile,
    AgentRegistry,

    AgentDeletionManager,
    AgentCreationSpec,
    AgentCreator,
    TurnStatusReporter,
    validate_agent_id,
    extract_interaction_text,
    ThreeGOrchestrator,
    DesignerSubagent,
    BuilderSubagent,
    SubagentConfig,
    SubagentYamlLoader,
    ValidationResult,
    MODEL_ORCHESTRATOR,
    MODEL_DESIGNER,
    MODEL_BUILDER,
    canonicalize_model_name,
)




class TestThreeGAgent(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_3g_agent_"))
        self.state_dir = self.temp_dir / ".3g_agent"
        self.output_dir = self.temp_dir / "outputs"

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parameter_collection_and_validation(self):
        """Test parameter collection and ensure environment_type must be remote."""
        config = ThreeGAgentConfig(
            skills_dir=Path("./skills"),
            environment_type="remote",
        )
        errors = ClientParameterCollector.validate(config)
        self.assertEqual(len(errors), 0)
        self.assertEqual(config.environment_type, "remote")
        self.assertEqual(config.agent_name, "3G-agent")

    def test_agent_id_resolution(self):
        """Test that agent_id defaults to Antigravity coding agent and rejects boolean flags."""
        from three_g_agent.config import resolve_default_agent_id

        # Default resolution
        self.assertEqual(resolve_default_agent_id(), "antigravity-preview-09-2026")

        # Config properly sets agent_id
        config = ThreeGAgentConfig(skills_dir=Path("./skills"))
        self.assertEqual(config.agent_id, "antigravity-preview-09-2026")
        self.assertEqual(config.model_name, "antigravity-preview-09-2026")

        # Rejection of boolean flag '1' when passed as model_name or agent_id
        config_with_flag = ThreeGAgentConfig(skills_dir=Path("./skills"), model_name="1")
        self.assertEqual(config_with_flag.agent_id, "antigravity-preview-09-2026")

        # Acceptance of explicit custom agent ID
        custom_config = ThreeGAgentConfig(skills_dir=Path("./skills"), agent_id="custom-coding-agent")
        self.assertEqual(custom_config.agent_id, "custom-coding-agent")

        # Test failure if environment is not remote
        invalid_config = ThreeGAgentConfig(
            skills_dir=Path("./skills"),
            environment_type="local",
        )
        with self.assertRaises(ValueError) as ctx:
            ClientParameterCollector.validate(invalid_config)
        self.assertIn("environment_type must be 'remote'", str(ctx.exception))

    def test_instructions_file_loading(self):
        """Test that instructions.md is loaded appropriately when present or empty."""
        test_instr_file = self.temp_dir / "instructions.md"
        
        # Scenario 1: Empty instructions file returns None
        test_instr_file.write_text("", encoding="utf-8")
        config_empty = ThreeGAgentConfig(
            skills_dir=Path("./skills"),
            instructions_file=test_instr_file,
        )
        self.assertIsNone(config_empty.load_instructions())

        # Scenario 2: Populated instructions file returns system prompt
        sample_prompt = "You are 3G-agent, an elite autonomous pedagogy engineering agent."
        test_instr_file.write_text(sample_prompt, encoding="utf-8")
        config_populated = ThreeGAgentConfig(
            skills_dir=Path("./skills"),
            instructions_file=test_instr_file,
        )
        self.assertEqual(config_populated.load_instructions(), sample_prompt)

    def test_model_initializer_separation(self):
        """Test that ModelInitializer creates an InitializedClient handle without executing code."""
        config = ThreeGAgentConfig(
            skills_dir=Path("./skills"),
            environment_type="remote",
            api_key="test_key_abc_123",
        )
        client_handle = ModelInitializer.initialize(config)
        self.assertIsNotNone(client_handle)
        self.assertIsNotNone(client_handle.client)
        self.assertEqual(client_handle.config.agent_name, "3G-agent")

    def test_skill_loader_with_pedagogy_engineering(self):
        """Test scanning and parsing the workspace skills (including pedagogy-engineering)."""
        skills_path = Path("./skills/pedagogy-engineering")
        if not skills_path.exists():
            skills_path = Path("./skills")

        loader = SkillLoader(skills_path)
        self.assertGreater(len(loader.skills), 0)

        # Check first skill
        skill = loader.skills[0]
        self.assertTrue(len(skill.name) > 0)
        self.assertTrue(len(skill.description) > 0)
        self.assertTrue(len(skill.auxiliary_files) >= 1)

        # Test generating remote inline sources
        sources = loader.build_remote_sources()
        self.assertGreater(len(sources), 0)
        self.assertEqual(sources[0]["type"], "inline")
        self.assertTrue(sources[0]["target"].startswith(".agents/skills/"))

    def test_environment_store_secure_persistence(self):
        """Test saving, retrieving, updating turn count, and resetting environment IDs."""
        store = EnvironmentStore(state_dir=self.state_dir, agent_name="3G-agent")

        # Initially no active environment
        self.assertIsNone(store.get_environment_id())

        # Save an environment ID
        test_env_id = "env_remote_sandbox_xyz_999"
        store.save_environment_id(test_env_id, metadata={"test": True})

        # Verify it can be retrieved
        retrieved_id = store.get_environment_id()
        self.assertEqual(retrieved_id, test_env_id)

        # Verify turn count increments on subsequent save
        updated_state = store.save_environment_id(test_env_id)
        self.assertEqual(updated_state.turn_count, 2)

        # Verify build_environment_payload reuses active ID
        payload = store.build_environment_payload(sources=[])
        self.assertEqual(payload, test_env_id)

        # Verify reset marks environment as inactive
        store.reset_environment()
        self.assertIsNone(store.get_environment_id())

        # Verify fresh environment is now requested
        fresh_payload = store.build_environment_payload(sources=[{"type": "inline", "target": "a", "content": "b"}])
        self.assertIsInstance(fresh_payload, dict)
        self.assertEqual(fresh_payload["type"], "remote")
        self.assertEqual(len(fresh_payload["sources"]), 1)

    def test_local_file_storage_and_accessibility(self):
        """Test that files created by agent are saved locally and indexed in manifest."""
        storage = FileStorageManager(output_dir=self.output_dir)

        # Direct file save
        test_content = "# Sample Deliverable\nPedagogical spec created by 3G-agent."
        saved_file = storage.save_file("deliverable.md", test_content)

        self.assertEqual(saved_file.file_name, "deliverable.md")
        self.assertTrue(saved_file.local_path.exists())
        self.assertEqual(saved_file.local_path.read_text(encoding="utf-8"), test_content)
        self.assertTrue(saved_file.file_uri.startswith("file:///"))
        self.assertGreater(saved_file.size_bytes, 0)

        # Extract file from model output text
        model_output_with_blocks = """
Here is the specification you requested:

```markdown:stage_0_spec.md
# Stage 0 Intake Document
Target Audience: Mill Operators
Domain: Industrial Automation
```

End of document.
"""
        extracted_files = storage.extract_and_save_deliverables(model_output_with_blocks)
        self.assertEqual(len(extracted_files), 1)
        self.assertEqual(extracted_files[0].file_name, "stage_0_spec.md")
        self.assertTrue(extracted_files[0].local_path.exists())

        # Check manifest
        all_files = storage.list_saved_files()
        self.assertEqual(len(all_files), 2)

    def test_three_g_agent_orchestration_mock(self):
        """Test full 3G-agent creation and execution lifecycle using a mock interaction."""
        config = ThreeGAgentConfig(
            agent_name="3G-agent",
            model_name="antigravity-preview-09-2026",
            environment_type="remote",
            skills_dir=Path("./skills"),
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )

        class MockInteraction:
            def __init__(self, prompt, environment):
                self.id = "int_12345"
                self.environment_id = (
                    environment if isinstance(environment, str) else "env_mock_sandbox_777"
                )
                self.output_text = (
                    "Completed analysis.\n\n"
                    "```pedagogy_plan.md\n# 3G-agent Pedagogy Plan\nObjectives formulated.\n```"
                )

        class MockInteractionsClient:
            def create(self, **kwargs):
                return MockInteraction(kwargs.get("input"), kwargs.get("environment"))

        class MockGenAIClient:
            def __init__(self):
                self.interactions = MockInteractionsClient()

        initialized_client = ModelInitializer._create_fallback_client(config)
        # Inject mock client for execution test
        initialized_client.client = MockGenAIClient()

        env_store = EnvironmentStore(state_dir=self.state_dir, agent_name="3G-agent")
        skill_loader = SkillLoader(config.skills_dir)
        storage_mgr = FileStorageManager(output_dir=self.output_dir)

        agent = ThreeGAgent(
            config=config,
            initialized_client=initialized_client,
            skill_loader=skill_loader,
            environment_store=env_store,
            storage_manager=storage_mgr,
        )

        # Execute turn 1
        response1 = agent.execute("Diagnose learning problem for engineering course.")
        self.assertIn("Completed analysis", response1.output_text)
        self.assertEqual(response1.environment_id, "env_mock_sandbox_777")
        self.assertEqual(agent.get_environment_id(), "env_mock_sandbox_777")
        self.assertGreater(len(response1.saved_files), 0)
        self.assertEqual(response1.saved_files[0].file_name, "pedagogy_plan.md")
        self.assertTrue(response1.saved_files[0].local_path.exists())

        # Execute turn 2 (verifying environment ID is reused)
        response2 = agent.chat("Proceed to Stage 1.")
        self.assertEqual(response2.environment_id, "env_mock_sandbox_777")

    def test_custom_agent_environment_payload_and_persistence(self):
        """Verify that when interacting with a custom created agent, 'environment' is ALWAYS
        passed (preventing 'Missing required field environment' 400 errors) and persists."""
        from three_g_agent.environment import EnvironmentStore

        env_store = EnvironmentStore(state_dir=self.state_dir, agent_name="custom-agent")

        # 1. Test build_environment_payload directly for custom agent inheriting base env
        payload = env_store.build_environment_payload(sources=[], force_fresh=False, inherit_agent_environment=True)
        self.assertIsNotNone(payload)
        self.assertEqual(payload, {"type": "remote"})

        # 2. Test execution flow with a custom agent ID
        config = ThreeGAgentConfig(
            agent_name="3G-agent",
            agent_id="coder-55555",
            skills_dir=None,
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )

        captured_calls = []

        class MockCaptureInteraction:
            def __init__(self, output_text, env_val):
                self.output_text = output_text
                self.environment_id = env_val if isinstance(env_val, str) else "env_sandbox_custom_999"
                self.id = "inter_custom_001"

        class MockCaptureInteractionsClient:
            def create(self, **kwargs):
                captured_calls.append(kwargs)
                return MockCaptureInteraction("Hello from custom agent", kwargs.get("environment"))

        class MockCaptureGenAIClient:
            def __init__(self):
                self.interactions = MockCaptureInteractionsClient()

        init_client = ModelInitializer._create_fallback_client(config)
        init_client.client = MockCaptureGenAIClient()

        agent = ThreeGAgent(
            config=config,
            initialized_client=init_client,
            skill_loader=SkillLoader.empty(),
            environment_store=env_store,
            storage_manager=FileStorageManager(output_dir=self.output_dir),
            load_local_context=False,
        )

        # Turn 1: Fresh environment must be passed as {"type": "remote"}
        resp1 = agent.execute("First message to created orchestrator agent")
        self.assertEqual(len(captured_calls), 1)
        self.assertIn("environment", captured_calls[0])
        self.assertEqual(captured_calls[0]["environment"], {"type": "remote"})
        self.assertEqual(resp1.environment_id, "env_sandbox_custom_999")
        self.assertEqual(agent.get_environment_id(), "env_sandbox_custom_999")

        # Turn 2: Held environment ID must be passed directly as string
        resp2 = agent.execute("Second message to created orchestrator agent")
        self.assertEqual(len(captured_calls), 2)
        self.assertIn("environment", captured_calls[1])
        self.assertEqual(captured_calls[1]["environment"], "env_sandbox_custom_999")
        self.assertEqual(captured_calls[1].get("previous_interaction_id"), "inter_custom_001")

        # Verify held environment ID across sessions
        sessions = agent.list_conversations()
        self.assertGreaterEqual(len(sessions), 1)
        self.assertEqual(sessions[0].environment_id, "env_sandbox_custom_999")

    def test_validate_agent_id_format(self):
        """Test agent_id format validation for [name-id_num] e.g. [coder-12345]."""
        from three_g_agent.registry import validate_agent_id

        # Valid formats
        self.assertEqual(validate_agent_id("coder-12345"), "coder-12345")
        self.assertEqual(validate_agent_id("[coder-12345]"), "coder-12345")
        self.assertEqual(validate_agent_id("pedagogy-001"), "pedagogy-001")
        self.assertEqual(validate_agent_id("3g_agent-99"), "3g_agent-99")

        # Invalid formats
        invalid_ids = ["coder", "12345", "", "   ", "coder_12345", "coder/12345", "-12345"]
        for bad_id in invalid_ids:
            with self.assertRaises(ValueError, msg=f"Should reject '{bad_id}'"):
                validate_agent_id(bad_id)

    def test_standalone_agent_creator(self):
        """Test standalone AgentCreator module with skill and instructions pre-loading directly to SDK API."""
        from three_g_agent.creator import AgentCreationSpec, AgentCreator
        from three_g_agent.initializer import AgentClientInitializer
        from three_g_agent.config import ThreeGAgentConfig

        test_instr = self.temp_dir / "instructions.md"
        test_instr.write_text("Elite script creation agent prompt.", encoding="utf-8")

        config = ThreeGAgentConfig(
            skills_dir=Path("./skills"),
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )
        client_handle = AgentClientInitializer.initialize(config, interactive_prompt=False)

        spec = AgentCreationSpec(
            agent_id="coder-99999",
            skills_dir=Path("./skills"),
            instructions_file=test_instr,
            description="Testing standalone creator",
        )
        result = AgentCreator.create_agent(spec=spec, client_handle=client_handle)

        self.assertEqual(result.agent_id, "coder-99999")
        self.assertGreater(result.skills_count, 0)
        self.assertTrue(result.has_instructions)
        self.assertGreater(result.instructions_length, 0)
        self.assertIsNotNone(result.remote_agent)

        # Verify it was created directly on the SDK API (client.agents.get / client.agents.list)
        remote_agent = AgentCreator.get_agent("coder-99999", client_handle=client_handle)
        self.assertIsNotNone(remote_agent)
        self.assertEqual(getattr(remote_agent, "id", None), "coder-99999")

        # Verify listing agents from SDK API includes the new agent
        all_remote_agents = AgentCreator.list_agents(client_handle=client_handle)
        agent_ids = [getattr(a, "id", str(a)) for a in all_remote_agents]
        self.assertIn("coder-99999", agent_ids)

        # Verify zero local storage: no local agent registry file exists
        local_agent_file = self.state_dir / "agents_registry.json"
        self.assertFalse(local_agent_file.exists())

    def test_initial_orchestrator_creation_without_skills(self):
        """When an agent is initially created by user, it is the orchestrator agent that is created.
        The orchestrator doesn't need any special skills, so no skills are loaded at creation."""
        from three_g_agent.creator import AgentCreationSpec, AgentCreator
        from three_g_agent.initializer import AgentClientInitializer
        from three_g_agent.config import ThreeGAgentConfig

        config = ThreeGAgentConfig(
            skills_dir=None,
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )
        client_handle = AgentClientInitializer.initialize(config, interactive_prompt=False)

        # Default AgentCreationSpec represents the initial orchestrator agent creation:
        # skills_dir is None (no special skills), instructions_file defaults to orch_instruction.md
        spec = AgentCreationSpec(agent_id="orch-00001")
        self.assertIsNone(spec.skills_dir)
        self.assertEqual(Path(spec.instructions_file), Path("./instructions/orch_instruction.md"))

        result = AgentCreator.create_agent(spec=spec, client_handle=client_handle)
        self.assertEqual(result.agent_id, "orch-00001")
        self.assertEqual(result.skills_count, 0)
        self.assertEqual(result.stages_count, 0)
        self.assertTrue(result.has_instructions)
        self.assertGreater(result.instructions_length, 0)
        self.assertEqual(result.model, "gemini-3.1-flash-lite")
        self.assertEqual(result.agent_config, {"model": "gemini-3.1-flash-lite"})
        self.assertEqual(result.remote_agent.agent_config, {"model": "gemini-3.1-flash-lite"})


    def test_agent_registry_and_conversation_persistence(self):
        """Test reusing existing agent and holding environment_id across conversations."""
        from three_g_agent.registry import AgentRegistry

        registry = AgentRegistry(state_dir=self.state_dir)
        registry.register_agent("coder-11111", description="Persistent conversation test agent")

        # 1. Create a conversation session with environment ID
        session = registry.create_conversation_session(
            agent_id="coder-11111",
            environment_id="env_remote_sandbox_turn1",
            title="Script Automation Chat",
        )
        self.assertEqual(session.agent_id, "coder-11111")
        self.assertEqual(session.environment_id, "env_remote_sandbox_turn1")
        self.assertEqual(session.turn_count, 0)

        # 2. Update conversation session (turn 2)
        updated = registry.update_conversation_session(
            agent_id="coder-11111",
            session_id=session.session_id,
            environment_id="env_remote_sandbox_turn1",
            last_interaction_id="int_turn2_abc",
            increment_turn=True,
        )
        self.assertEqual(updated.turn_count, 1)
        self.assertEqual(updated.last_interaction_id, "int_turn2_abc")

        # 3. List conversations for agent
        conv_list = registry.list_conversations("coder-11111")
        self.assertEqual(len(conv_list), 1)
        self.assertEqual(conv_list[0].environment_id, "env_remote_sandbox_turn1")

        # 4. Verify ThreeGAgent resume_conversation holds this environment_id
        config = ThreeGAgentConfig(
            agent_name="3G-agent",
            agent_id="coder-11111",
            skills_dir=Path("./skills"),
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )
        agent = ThreeGAgent.create(
            skills_dir=Path("./skills"),
            agent_id="coder-11111",
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )
        resumed = agent.resume_conversation(session.session_id)
        self.assertTrue(resumed)
        self.assertEqual(agent.get_environment_id(), "env_remote_sandbox_turn1")

        # 5. Verify starting a new chat resets the active session
        agent.start_new_chat()
        self.assertIsNone(agent.active_session_id)
        self.assertIsNone(agent.get_environment_id())

    def test_turn_status_reporter(self):
        """Test real-time turn status reporting across all phases."""
        recorded_events = []

        def callback(phase, detail):
            recorded_events.append((phase, detail))

        reporter = TurnStatusReporter(enabled=True, callback=callback)
        with reporter:
            reporter.thinking("Analyzing user instructions...")
            reporter.skill_use("pedagogy-engineering", stage="stage_0")
            reporter.tool_call("code_execution", args_summary="script.py")
            reporter.tool_result("code_execution", result_summary="Success")
            reporter.environment("Holding container env_test_123")
            reporter.responding("Streaming final output...")

        phases = [p for p, _ in recorded_events]
        self.assertIn("Thinking", phases)
        self.assertIn("Skill Use", phases)
        self.assertIn("Tool Call", phases)
        self.assertIn("Tool Result", phases)
        self.assertIn("Environment", phases)
        self.assertIn("Responding", phases)

    def test_agent_deletion_manager_and_sdk_procedure(self):
        """Test Antigravity SDK procedure for deleting interactions and agents."""
        registry = AgentRegistry(state_dir=self.state_dir)
        test_agent_id = "coder-99999"

        # Initialize mock client
        config = ThreeGAgentConfig(
            skills_dir=Path("./skills"),
            agent_id=test_agent_id,
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )
        client_handle = AgentClientInitializer.initialize(config, interactive_prompt=False)

        # Create agent directly on SDK API (client.agents.create)
        spec = AgentCreationSpec(agent_id=test_agent_id)
        AgentCreator.create_agent(spec=spec, client_handle=client_handle)

        # Create session in local session registry
        session = registry.create_conversation_session(
            agent_id=test_agent_id,
            environment_id="env_remote_delete_test",
            title="Session for Deletion",
        )
        registry.update_conversation_session(
            agent_id=test_agent_id,
            session_id=session.session_id,
            last_interaction_id="inter_del_abc123",
        )

        # 1. Delete conversation session & held interaction via Antigravity SDK procedure
        session_del_result = AgentDeletionManager.delete_conversation_session(
            agent_id=test_agent_id,
            session_id=session.session_id,
            client=client_handle.client,
            registry=registry,
            state_dir=self.state_dir,
        )
        self.assertTrue(session_del_result.success)
        self.assertTrue(session_del_result.local_deleted)
        # Verify session is gone from registry
        self.assertIsNone(registry.get_conversation_session(test_agent_id, session.session_id))

        # 2. Delete agent via Antigravity SDK procedure (client.agents.delete)
        agent_del_result = AgentDeletionManager.delete_agent(
            agent_id=test_agent_id,
            client=client_handle.client,
            registry=registry,
            state_dir=self.state_dir,
        )
        self.assertTrue(agent_del_result.success)
        self.assertTrue(agent_del_result.remote_deleted)
        # Verify agent is gone from SDK API
        self.assertIsNone(AgentCreator.get_agent(test_agent_id, client_handle=client_handle))

    def test_agent_deletion_convenience_methods(self):
        """Test delete_conversation_session and delete_agent methods on ThreeGAgent."""
        agent_id = "pedagogy-88888"
        agent = ThreeGAgent.create(
            skills_dir=Path("./skills"),
            agent_id=agent_id,
            state_dir=self.state_dir,
            output_dir=self.output_dir,
        )

        # Create agent on SDK API so it exists remotely
        spec = AgentCreationSpec(agent_id=agent_id)
        AgentCreator.create_agent(spec=spec, client_handle=agent.client)

        session = agent.registry.create_conversation_session(
            agent_id=agent_id,
            environment_id="env_convenience_test",
            title="Active Session",
        )
        agent.resume_conversation(session.session_id)
        self.assertEqual(agent.active_session_id, session.session_id)

        # Delete active session via agent method
        del_sess_res = agent.delete_conversation_session()
        self.assertTrue(del_sess_res.success)
        self.assertIsNone(agent.active_session_id)

        # Delete agent via agent method (client.agents.delete)
        del_agent_res = agent.delete_agent()
        self.assertTrue(del_agent_res.success)
        self.assertTrue(del_agent_res.remote_deleted)
        self.assertIsNone(AgentCreator.get_agent(agent_id, client_handle=agent.client))

    def test_extract_interaction_text_only_clean_response(self):
        """Test that extract_interaction_text extracts only the clean text and never dumps raw API objects."""
        # 1. Official Google GenAI ModelOutputStep inside InteractionSseEventInteraction
        try:
            from google.genai._gaos.types.interactions.modeloutputstep import ModelOutputStep
            from google.genai._gaos.types.interactions.textcontent import TextContent
            from google.genai._gaos.types.interactions.interactionsseeventinteraction import InteractionSseEventInteraction

            step = ModelOutputStep(
                type="model_output",
                content=[TextContent(type="text", text="Clean pedagogical automation logic response.")],
            )
            inter = InteractionSseEventInteraction(
                id="int_live_001",
                status="completed",
                agent="coder-12345",
                steps=[step],
            )
            extracted = extract_interaction_text(inter)
            self.assertEqual(extracted, "Clean pedagogical automation logic response.")
            # Ensure no raw repr / API schema leaked
            self.assertNotIn("InteractionSseEventInteraction", extracted)
            self.assertNotIn("int_live_001", extracted)
        except ImportError:
            pass

        # 2. Dictionary with steps
        dict_inter = {
            "id": "int_dict_002",
            "steps": [
                {"type": "thought", "thought": "Internal reasoning hidden from user"},
                {"type": "model_output", "content": [{"type": "text", "text": "Direct dictionary text."}]},
            ],
        }
        extracted_dict = extract_interaction_text(dict_inter)
        self.assertEqual(extracted_dict, "Direct dictionary text.")
        self.assertNotIn("Internal reasoning", extracted_dict)

        # 3. Direct output_text object
        class MockOutputTextObj:
            output_text = "Plain text answer"
        self.assertEqual(extract_interaction_text(MockOutputTextObj()), "Plain text answer")

        # 4. Fallback streamed chunks
        self.assertEqual(
            extract_interaction_text(None, fallback_streamed="Streamed response chunk"),
            "Streamed response chunk",
        )

        # 5. Empty or unknown object must NOT dump str(obj)
        class UnknownEmptyAPIObject:
            def __str__(self):
                return "UnknownEmptyAPIObject(raw_api_dump=True, debug='leaked')"

        extracted_empty = extract_interaction_text(UnknownEmptyAPIObject())
        self.assertEqual(extracted_empty, "")
        self.assertNotIn("raw_api_dump", extracted_empty)


class DeliverableExtractorTests(unittest.TestCase):
    """Verifies that FileStorageManager extracts deliverables without premature truncation on nested blocks."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_storage_")
        self.storage = FileStorageManager(output_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_nested_code_blocks_in_markdown_do_not_truncate(self):
        output = (
            "Here is the complete plan:\n\n"
            "````markdown:complete_plan.md\n"
            "# Section 1: Intro\n"
            "Text before diagram\n"
            "```mermaid\n"
            "graph TD\n"
            "A --> B\n"
            "```\n"
            "## Section 2: Details\n"
            "```python\n"
            "x = 42\n"
            "```\n"
            "## Section 3: Summary\n"
            "Final conclusion text.\n"
            "````\n"
        )
        saved = self.storage.extract_and_save_deliverables(output)
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].file_name, "complete_plan.md")
        content = Path(saved[0].local_path).read_text(encoding="utf-8")
        self.assertIn("Section 1: Intro", content)
        self.assertIn("graph TD", content)
        self.assertIn("Section 2: Details", content)
        self.assertIn("x = 42", content)
        self.assertIn("Final conclusion text.", content)

    def test_three_backtick_nested_markdown_extraction(self):
        output = (
            "```markdown:three_tick_plan.md\n"
            "# Plan Start\n"
            "```mermaid\n"
            "graph LR\n"
            "Start --> End\n"
            "```\n"
            "# Plan End\n"
            "```\n"
        )
        saved = self.storage.extract_and_save_deliverables(output)
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].file_name, "three_tick_plan.md")
        content = Path(saved[0].local_path).read_text(encoding="utf-8")
        self.assertIn("# Plan Start", content)
        self.assertIn("graph LR", content)
        self.assertIn("# Plan End", content)


class TestThreeAgentArchitecture(unittest.TestCase):
    """Test suite validating the 3-agent architecture:
    1. Brains (3.1 flash lite, 3.5 flash lite, 3.8 flash).
    2. Affirmative action language & ANIR in system instructions (no 'DO NOT').
    3. Designer subagent with skills and file access only.
    4. Builder subagent with no system instruction and coding tools enabled.
    5. Shared environment persistence across all 3 agents.
    6. Lazy on-demand spinup by parent Orchestrator.
    7. Restructured outputs into /design and /build.
    8. Subagent YAML definitions.
    9. Orchestrator output validation against user requests.
    """

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_arch_"))
        self.state_dir = self.temp_dir / ".3g_agent"
        self.output_dir = self.temp_dir / "outputs"

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_brains_and_model_properties(self):
        """Validates model assignments: 3.1 flash lite, 3.5 flash lite, 3.8 flash."""
        self.assertEqual(MODEL_ORCHESTRATOR, "3.1 flash lite")
        self.assertEqual(MODEL_DESIGNER, "3.5 flash lite")
        self.assertEqual(MODEL_BUILDER, "3.8 flash")

        self.assertEqual(canonicalize_model_name("3.1 flash lite"), "gemini-3.1-flash-lite")
        self.assertEqual(canonicalize_model_name("3.5 flash lite"), "gemini-3.5-flash-lite")
        self.assertEqual(canonicalize_model_name("3.8 flash"), "gemini-3.8-flash")

        # Config model property reading and setting
        cfg = ThreeGAgentConfig(model="3.1 flash lite")
        self.assertEqual(cfg.model, "3.1 flash lite")
        self.assertEqual(cfg.agent_id, "3.1 flash lite")

        cfg.model = "3.5 flash lite"
        self.assertEqual(cfg.model, "3.5 flash lite")
        self.assertEqual(cfg.agent_id, "3.5 flash lite")

    def test_affirmative_action_language_and_anir(self):
        """Validates that system prompts strictly avoid negative language (DO NOT) and use ANIR."""
        forbidden_regex = re.compile(r"\b(do\s+not|don't|never|cannot|must\s+not|shall\s+not)\b", re.IGNORECASE)

        # Root instructions must be deleted
        self.assertFalse(Path("./desi_instructions.md").exists(), "desi_instructions.md must not exist in workspace root")
        self.assertFalse(Path("./orch_instruction.md").exists(), "orch_instruction.md must not exist in workspace root")

        instruction_files = [
            Path("./instructions/orch_instruction.md"),
            Path("./instructions/desi_instructions.md"),
        ]

        for p in instruction_files:
            self.assertTrue(p.exists(), f"Instruction file {p} must exist within /instructions directory")
            text = p.read_text(encoding="utf-8")


            # 1. Assert zero occurrences of forbidden negative tokens
            matches = forbidden_regex.findall(text)
            self.assertEqual(
                len(matches),
                0,
                f"File {p} contains forbidden negative language: {matches}",
            )

            # 2. Assert presence of affirmative action language
            has_affirmative = any(
                term in text.lower()
                for term in ("avoid", "prevent", "decline", "confine", "differ", "needless")
            )
            self.assertTrue(has_affirmative, f"File {p} must use affirmative action vocabulary")

            # 3. Assert ANIR structural declarative syntax
            self.assertIn("[SYSTEM_DECLARATION]", text, f"File {p} must use ANIR blocks")

    def test_subagent_yaml_definitions(self):
        """Validates that YAML specs in subagents/ directory are well-structured and load cleanly."""
        yaml_loader = SubagentYamlLoader()
        specs = yaml_loader.load_all("./subagents")

        self.assertIn("designer", specs)
        self.assertIn("builder", specs)
        self.assertIn("orchestrator", specs)

        designer_spec = specs["designer"]
        self.assertEqual(designer_spec.brain, "3.5 flash lite")
        self.assertIn("pedagogy-engineering", designer_spec.skills)
        self.assertIn("file_read", designer_spec.tools_allowed)
        self.assertIn("code_execution", designer_spec.tools_disabled)
        self.assertEqual(str(designer_spec.output_dir).replace("\\", "/"), "outputs/design")

        builder_spec = specs["builder"]
        self.assertEqual(builder_spec.brain, "3.8 flash")
        self.assertIsNone(builder_spec.system_instruction_file)
        self.assertEqual(len(builder_spec.skills), 0)
        self.assertIn("code_execution", builder_spec.tools_allowed)
        self.assertEqual(str(builder_spec.output_dir).replace("\\", "/"), "outputs/build")

    def test_outputs_directory_separation(self):
        """Validates that design outputs land in outputs/design and build outputs land in outputs/build."""
        design_mgr = FileStorageManager.for_design(self.output_dir)
        build_mgr = FileStorageManager.for_build(self.output_dir)

        design_file = design_mgr.save_file("curriculum_spec.md", "# Pedagogical Plan")
        build_file = build_mgr.save_file("simulator.py", "print('Running simulation')")

        self.assertIn("design", str(design_file.local_path).replace("\\", "/"))
        self.assertIn("build", str(build_file.local_path).replace("\\", "/"))
        self.assertTrue(design_file.local_path.exists())
        self.assertTrue(build_file.local_path.exists())

    def test_designer_subagent_skills_and_tool_restrictions(self):
        """Validates that only Designer agent gets custom skills and coding tools are disabled."""
        store = EnvironmentStore(state_dir=self.state_dir)
        designer = DesignerSubagent(
            environment_store=store,
            skills_dir="./skills",
            instructions_file="./instructions/desi_instructions.md",
            output_dir=self.output_dir / "design",
            state_dir=self.state_dir,
            brain=MODEL_DESIGNER,
        )

        self.assertEqual(designer.brain, "3.5 flash lite")
        self.assertGreater(len(designer.skill_loader.skills), 0)
        self.assertTrue(designer.is_tool_allowed("file_read"))
        self.assertTrue(designer.is_tool_allowed("file_write"))
        self.assertFalse(designer.is_tool_allowed("code_execution"))
        self.assertFalse(designer.is_tool_allowed("terminal"))
        self.assertFalse(designer.is_tool_allowed("run_command"))

    def test_builder_subagent_has_no_instructions_and_full_tools(self):
        """Validates that Builder subagent has no system instruction and has full coding tools."""
        store = EnvironmentStore(state_dir=self.state_dir)
        builder = BuilderSubagent(
            environment_store=store,
            output_dir=self.output_dir / "build",
            state_dir=self.state_dir,
            brain=MODEL_BUILDER,
        )

        self.assertEqual(builder.brain, "3.8 flash")
        self.assertIsNone(builder.config.instructions_file)
        self.assertIsNone(builder.config.load_instructions())
        self.assertEqual(len(builder.skill_loader.skills), 0)
        self.assertTrue(builder.is_tool_allowed("code_execution"))
        self.assertTrue(builder.is_tool_allowed("run_command"))
        self.assertTrue(builder.is_tool_allowed("file_write"))

    def test_shared_environment_across_all_agents(self):
        """Validates that all 3 agents share the exact same EnvironmentStore & environment_id."""
        orchestrator = ThreeGOrchestrator(
            state_dir=self.state_dir,
            output_dir=self.output_dir,
            brain=MODEL_ORCHESTRATOR,
        )

        designer = orchestrator.get_designer_subagent()
        builder = orchestrator.get_builder_subagent()

        # Both subagents share the orchestrator's environment store
        self.assertIs(orchestrator.environment, designer.environment)
        self.assertIs(orchestrator.environment, builder.environment)

        # Set environment ID on orchestrator
        test_shared_id = "env_remote_sandbox_all_3_agents_999"
        orchestrator.environment.save_environment_id(test_shared_id)

        # Designer and Builder immediately see the shared environment ID
        self.assertEqual(designer.environment.get_environment_id(), test_shared_id)
        self.assertEqual(builder.environment.get_environment_id(), test_shared_id)

    def test_lazy_subagent_spinup(self):
        """Validates that subagents are NOT spun up initially; only on demand."""
        orchestrator = ThreeGOrchestrator(
            state_dir=self.state_dir,
            output_dir=self.output_dir,
            brain=MODEL_ORCHESTRATOR,
        )

        # Initially, neither subagent is spun up
        self.assertFalse(orchestrator.is_designer_spun_up)
        self.assertFalse(orchestrator.is_builder_spun_up)

        # When design is requested, only designer is spun up
        orchestrator.get_designer_subagent()
        self.assertTrue(orchestrator.is_designer_spun_up)
        self.assertFalse(orchestrator.is_builder_spun_up)

        # When build is requested, builder is spun up
        orchestrator.get_builder_subagent()
        self.assertTrue(orchestrator.is_builder_spun_up)

    def test_orchestrator_output_validation(self):
        """Validates that the orchestrator validates subagent outputs against user requests."""
        orchestrator = ThreeGOrchestrator(
            state_dir=self.state_dir,
            output_dir=self.output_dir,
            brain=MODEL_ORCHESTRATOR,
        )

        # Case 1: Valid designer response
        valid_desi_resp = ThreeGAgentResponse(
            output_text="Pedagogical design with Bloom's taxonomy objectives.",
            environment_id="env_test",
            saved_files=[
                SavedFile(
                    file_name="plan.md",
                    local_path=self.output_dir / "design" / "plan.md",
                    file_uri="file:///outputs/design/plan.md",
                    size_bytes=100,
                    sha256="abc",
                    created_at="now",
                    source_type="direct",
                )
            ],
        )
        val_result = orchestrator.validate_output(
            "Design a curriculum plan for milling operators",
            valid_desi_resp,
            "designer",
        )
        self.assertTrue(val_result.is_valid)

        # Case 2: Designer violates policy by producing forbidden game code
        bad_desi_resp = ThreeGAgentResponse(
            output_text="Here is your game: import pygame; pygame.init(); def run_game(): pass",
            environment_id="env_test",
        )
        val_bad = orchestrator.validate_output(
            "Design an instructional plan",
            bad_desi_resp,
            "designer",
        )
        self.assertFalse(val_bad.is_valid)
        self.assertIn("game simulation", " ".join(val_bad.reasons))


if __name__ == "__main__":
    unittest.main()



