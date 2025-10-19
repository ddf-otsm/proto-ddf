"""
Integration tests for Proto-DDF workflows.

Tests cover:
- Virtual environment setup
- Configuration loading
- Port availability
- Application startup
- Generated app execution
"""

import os
import socket
import subprocess
import sys
import unittest
from pathlib import Path


class TestVirtualEnvironment(unittest.TestCase):
    """Test virtual environment setup."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.venv_path = self.project_root / "venv"

    def test_venv_exists(self):
        """Test that virtual environment exists."""
        self.assertTrue(self.venv_path.exists(), "Virtual environment not found")
        self.assertTrue(self.venv_path.is_dir(), "Virtual environment is not a directory")

    def test_venv_python(self):
        """Test that virtual environment has Python."""
        python_path = self.venv_path / "bin" / "python"
        self.assertTrue(python_path.exists(), "Python not found in virtual environment")

    def test_python_version(self):
        """Test that Python version is 3.10+."""
        python_path = self.venv_path / "bin" / "python"

        if not python_path.exists():
            self.skipTest("Python not found in virtual environment")

        result = subprocess.run([str(python_path), "--version"], capture_output=True, text=True)

        version_str = result.stdout.strip()
        # Extract version number (e.g., "Python 3.11.13" -> "3.11.13")
        version = version_str.split()[1]
        major, minor = map(int, version.split(".")[:2])

        self.assertGreaterEqual(major, 3, "Python major version should be 3 or higher")
        self.assertGreaterEqual(minor, 10, "Python minor version should be 10 or higher")

    def test_reflex_installed(self):
        """Test that Reflex is installed in virtual environment."""
        python_path = self.venv_path / "bin" / "python"

        if not python_path.exists():
            self.skipTest("Python not found in virtual environment")

        # Test that reflex can be imported (installed from submodule)
        # Need to add project root to PYTHONPATH for submodule imports
        import os

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)

        # Test that reflex imports successfully and has expected attributes
        result = subprocess.run(
            [
                str(python_path),
                "-c",
                "import reflex; import reflex.constants; print('SUCCESS')",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(
            result.returncode,
            0,
            f"Reflex not installed or import failed.\nStdout: {result.stdout}\nStderr: {result.stderr}",
        )
        self.assertIn("SUCCESS", result.stdout, "Reflex import did not complete successfully")


class TestConfigurationLoading(unittest.TestCase):
    """Test configuration loading."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(self.project_root))

    def test_import_config_module(self):
        """Test that config module can be imported."""
        try:
            import config

            self.assertTrue(hasattr(config, "FRONTEND_PORT"))
            self.assertTrue(hasattr(config, "BACKEND_PORT"))
            self.assertTrue(hasattr(config, "BACKEND_HOST"))
        except ImportError as e:
            self.fail(f"Failed to import config module: {e}")

    def test_import_constants(self):
        """Test that constants can be imported."""
        try:
            from config.constants import (
                BACKEND_PORT,
                FRONTEND_PORT,
                GENERATED_BACKEND_PORT,
                GENERATED_FRONTEND_PORT,
            )

            self.assertIsInstance(FRONTEND_PORT, int)
            self.assertIsInstance(BACKEND_PORT, int)
            self.assertIsInstance(GENERATED_FRONTEND_PORT, int)
            self.assertIsInstance(GENERATED_BACKEND_PORT, int)
        except ImportError as e:
            self.fail(f"Failed to import constants: {e}")

    def test_rxconfig_loading(self):
        """Test that rxconfig can be loaded."""
        try:
            sys.path.insert(0, str(self.project_root))
            import rxconfig

            self.assertTrue(hasattr(rxconfig, "config"))
        except ImportError as e:
            self.fail(f"Failed to import rxconfig: {e}")


class TestPortAvailability(unittest.TestCase):
    """Test port availability checks."""

    def test_check_port_method(self):
        """Test method to check if port is available."""

        def is_port_in_use(port):
            """Check if a port is in use."""
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return False
                except OSError:
                    return True

        # Test with a port that should be free
        high_port = 49999
        # We can't guarantee it's free, but we can test the function works
        result = is_port_in_use(high_port)
        self.assertIsInstance(result, bool)

    def test_configured_ports_conflict(self):
        """Test that configured ports don't conflict with each other."""
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))

        try:
            from config import (
                BACKEND_PORT,
                FRONTEND_PORT,
                GENERATED_BACKEND_PORT,
                GENERATED_FRONTEND_PORT,
            )

            ports = [
                FRONTEND_PORT,
                BACKEND_PORT,
                GENERATED_FRONTEND_PORT,
                GENERATED_BACKEND_PORT,
            ]
            unique_ports = set(ports)

            self.assertEqual(len(ports), len(unique_ports), f"Port conflict detected: {ports}")
        except ImportError as e:
            self.skipTest(f"Could not import config: {e}")


class TestRunScripts(unittest.TestCase):
    """Test run scripts."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent

    def test_workflow_run_script_exists(self):
        """Test that workflow run script exists."""
        run_script = self.project_root / "workflows" / "run.sh"
        self.assertTrue(run_script.exists(), "workflows/run.sh not found")

    def test_run_script_symlink_exists(self):
        """Test that run.sh symlink exists."""
        run_script = self.project_root / "run.sh"
        self.assertTrue(run_script.exists(), "run.sh symlink not found")

    def test_run_script_executable(self):
        """Test that run scripts are executable."""
        scripts = [
            self.project_root / "workflows" / "run.sh",
            self.project_root / "generated" / "netsuite_integration_hub" / "run.sh",
        ]

        for script in scripts:
            if script.exists():
                self.assertTrue(os.access(script, os.X_OK), f"Script not executable: {script}")

    def test_generated_app_run_script(self):
        """Test that generated app has run script."""
        generated_app = self.project_root / "generated" / "netsuite_integration_hub"

        if not generated_app.exists():
            self.skipTest("NetSuite Integration Hub not found")

        run_script = generated_app / "run.sh"
        self.assertTrue(run_script.exists(), "Generated app run.sh not found")
        self.assertTrue(os.access(run_script, os.X_OK), "Generated app run.sh not executable")


class TestApplicationStructure(unittest.TestCase):
    """Test application structure and organization."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent

    def test_project_directories(self):
        """Test that all required directories exist."""
        required_dirs = [
            "proto_ddf_app",
            "config",
            "generated",
            "workflows",
            "tests",
            "reflex",
        ]

        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Directory not found: {dir_name}")
            self.assertTrue(dir_path.is_dir(), f"Path is not a directory: {dir_name}")

    def test_generator_module(self):
        """Test that generator module exists."""
        generator_path = self.project_root / "proto_ddf_app" / "generator.py"
        self.assertTrue(generator_path.exists(), "Generator module not found")

    def test_rxconfig_exists(self):
        """Test that rxconfig exists."""
        rxconfig_path = self.project_root / "rxconfig.py"
        self.assertTrue(rxconfig_path.exists(), "rxconfig.py not found")

    def test_config_init_exists(self):
        """Test that config __init__.py exists."""
        config_init = self.project_root / "config" / "__init__.py"
        self.assertTrue(config_init.exists(), "config/__init__.py not found")


if __name__ == "__main__":
    unittest.main()
