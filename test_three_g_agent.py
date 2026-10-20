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


if __name__ == "__main__":
    unittest.main()
