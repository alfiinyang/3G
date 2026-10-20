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
import shutil
import tempfile
import unittest
from pathlib import Path

from three_g_agent import (
    ThreeGAgent,
    ThreeGAgentConfig,
    ClientParameterCollector,
    AgentClientInitializer,
    ModelInitializer,
    EnvironmentStore,
    SkillLoader,
    FileStorageManager,
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
        """Test standalone AgentCreator module with skill and instructions pre-loading."""
        from three_g_agent.creator import AgentCreationSpec, AgentCreator
        from three_g_agent.registry import AgentRegistry

        registry = AgentRegistry(state_dir=self.state_dir)
        test_instr = self.temp_dir / "instructions.md"
        test_instr.write_text("Elite script creation agent prompt.", encoding="utf-8")

        spec = AgentCreationSpec(
            agent_id="coder-99999",
            skills_dir=Path("./skills"),
            instructions_file=test_instr,
            description="Testing standalone creator",
        )
        result = AgentCreator.create_agent(spec=spec, registry=registry)

        self.assertEqual(result.agent_id, "coder-99999")
        self.assertGreater(result.skills_count, 0)
        self.assertTrue(result.has_instructions)
        self.assertGreater(result.instructions_length, 0)

        # Verify it was persisted in the registry
        saved_record = registry.get_agent("coder-99999")
        self.assertIsNotNone(saved_record)
        self.assertEqual(saved_record.agent_id, "coder-99999")
        self.assertTrue(saved_record.has_instructions)

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


if __name__ == "__main__":
    unittest.main()

