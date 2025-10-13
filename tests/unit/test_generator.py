"""
Unit tests for generator interface.

Tests cover:
- Generator state management
- Template selection
- App generation logic
- Generated app tracking
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestGeneratorState(unittest.TestCase):
    """Test generator state management."""

    def setUp(self):
        """Set up test environment."""
        # Import after path is set
        from proto_ddf_app.generator import GeneratorState
        self.state_class = GeneratorState

    def test_initial_state(self):
        """Test generator initial state."""
        state = self.state_class()

        # Check initial values
        self.assertIsInstance(state.generated_apps, list)
        self.assertEqual(state.generation_status, "idle")
        self.assertEqual(state.generation_message, "")
        self.assertEqual(state.project_name, "")
        self.assertEqual(state.project_description, "")

    def test_generated_apps_list(self):
        """Test that generated apps list is properly initialized."""
        state = self.state_class()

        # Should have at least the example NetSuite Integration Hub
        self.assertGreaterEqual(len(state.generated_apps), 1)

        # Check first app structure
        if len(state.generated_apps) > 0:
            app = state.generated_apps[0]
            required_keys = ["name", "description", "path", "status", "port"]
            for key in required_keys:
                self.assertIn(key, app, f"Generated app missing key: {key}")

    def test_app_generation(self):
        """Test app generation functionality."""
        state = self.state_class()

        # Set project name and try to generate
        test_name = "TestApp"
        state.set_project_name(test_name)
        
        self.assertEqual(state.project_name, test_name)
        
        # Try generating (note: this is a generator function in Reflex)
        # We can test that it exists and is callable
        self.assertTrue(hasattr(state, 'generate_app'))
        self.assertTrue(callable(state.generate_app))

    def test_project_name_setting(self):
        """Test setting project name."""
        state = self.state_class()

        test_name = "TestApp"
        state.set_project_name(test_name)

        self.assertEqual(state.project_name, test_name)

    def test_project_description_setting(self):
        """Test setting project description."""
        state = self.state_class()

        test_description = "Test application description"
        state.set_project_description(test_description)

        self.assertEqual(state.project_description, test_description)


class TestGeneratorComponents(unittest.TestCase):
    """Test generator UI components."""

    def test_app_card_import(self):
        """Test that app card component can be imported."""
        try:
            from proto_ddf_app.generator import app_card
            self.assertTrue(callable(app_card))
        except ImportError as e:
            self.fail(f"Failed to import app_card: {e}")

    def test_index_import(self):
        """Test that index function can be imported."""
        try:
            from proto_ddf_app.generator import index
            self.assertTrue(callable(index))
        except ImportError as e:
            self.fail(f"Failed to import index: {e}")
    
    def test_generator_app_import(self):
        """Test that generator app can be imported."""
        try:
            from proto_ddf_app.generator import app
            self.assertIsNotNone(app)
        except ImportError as e:
            self.fail(f"Failed to import app: {e}")


class TestGeneratedAppStructure(unittest.TestCase):
    """Test generated application structure."""

    def setUp(self):
        """Set up test environment."""
        self.generated_dir = Path(__file__).parent.parent.parent / "generated"

    def test_generated_directory_exists(self):
        """Test that generated directory exists."""
        self.assertTrue(self.generated_dir.exists(), "Generated directory does not exist")
        self.assertTrue(self.generated_dir.is_dir(), "Generated path is not a directory")

    def test_netsuite_hub_exists(self):
        """Test that NetSuite Integration Hub example exists."""
        netsuite_hub = self.generated_dir / "netsuite_integration_hub"
        self.assertTrue(netsuite_hub.exists(), "NetSuite Integration Hub not found")

    def test_netsuite_hub_structure(self):
        """Test NetSuite Integration Hub structure."""
        netsuite_hub = self.generated_dir / "netsuite_integration_hub"

        if not netsuite_hub.exists():
            self.skipTest("NetSuite Integration Hub not found")

        # Check required files
        required_files = [
            "rxconfig.py",
            "netsuite_integration_hub.py",
            "run.sh"
        ]

        for file in required_files:
            file_path = netsuite_hub / file
            self.assertTrue(file_path.exists(), f"Missing file: {file}")

        # Check run.sh is executable
        run_sh = netsuite_hub / "run.sh"
        if run_sh.exists():
            self.assertTrue(os.access(run_sh, os.X_OK), "run.sh is not executable")


if __name__ == "__main__":
    unittest.main()

