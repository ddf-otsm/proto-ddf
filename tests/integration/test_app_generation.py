"""Integration tests for app generation functionality."""

import shutil
import subprocess
from pathlib import Path

import pytest


class TestAppGeneration:
    """Test the app generation functionality."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up test apps after each test."""
        yield
        # Cleanup after test
        test_dirs = [
            "generated/test_simple_app",
            "generated/test_duplicate_app",
            "generated/test_special_chars",
        ]
        for test_dir in test_dirs:
            dir_path = Path(test_dir)
            if dir_path.exists():
                shutil.rmtree(dir_path)

    def test_generated_app_structure(self):
        """Test that generated apps have the correct file structure."""
        app_dir = Path("generated/test_stock_market")

        # Check main files exist
        assert (app_dir / "rxconfig.py").exists(), "rxconfig.py should exist"
        assert (app_dir / "requirements.txt").exists(), "requirements.txt should exist"
        assert (app_dir / "run.sh").exists(), "run.sh should exist"
        assert (app_dir / ".gitignore").exists(), ".gitignore should exist"

        # Check app module directory
        app_module_dir = app_dir / "test_stock_market_app"
        assert app_module_dir.exists(), "App module directory should exist"
        assert (app_module_dir / "__init__.py").exists(), "__init__.py should exist"
        assert (
            app_module_dir / "test_stock_market.py"
        ).exists(), "Main app file should exist"

    def test_generated_app_rxconfig(self):
        """Test that rxconfig.py is correctly configured."""
        rxconfig_path = Path("generated/test_stock_market/rxconfig.py")
        assert rxconfig_path.exists(), "rxconfig.py should exist"

        content = rxconfig_path.read_text()

        # Check required config elements
        assert "app_name=" in content, "Should have app_name"
        assert "app_module_import=" in content, "Should have app_module_import"
        assert "backend_port=" in content, "Should have backend_port"
        assert "frontend_port=" in content, "Should have frontend_port"

        # Check correct module import
        assert (
            'app_module_import="test_stock_market_app.test_stock_market"' in content
        ), "Should have correct module import path"

    def test_generated_app_main_file(self):
        """Test that the main app file is correctly generated."""
        main_file = Path(
            "generated/test_stock_market/test_stock_market_app/test_stock_market.py"
        )
        assert main_file.exists(), "Main app file should exist"

        content = main_file.read_text()

        # Check required imports and components
        assert "import reflex as rx" in content, "Should import reflex"
        assert "class State(rx.State):" in content, "Should have State class"
        assert "def index() -> rx.Component:" in content, "Should have index function"
        assert "app = rx.App()" in content, "Should create app instance"
        assert "app.add_page(index" in content, "Should add index page"

    def test_generated_app_requirements(self):
        """Test that requirements.txt is correctly generated."""
        req_file = Path("generated/test_stock_market/requirements.txt")
        assert req_file.exists(), "requirements.txt should exist"

        content = req_file.read_text()
        assert "reflex" in content, "Should include reflex dependency"

    def test_generated_app_run_script(self):
        """Test that run.sh is correctly generated and executable."""
        run_script = Path("generated/test_stock_market/run.sh")
        assert run_script.exists(), "run.sh should exist"

        # Check if executable
        assert run_script.stat().st_mode & 0o111, "run.sh should be executable"

        content = run_script.read_text()

        # Check script content
        assert "#!/bin/bash" in content, "Should have bash shebang"
        assert "python3 -m venv venv" in content, "Should create venv"
        assert "source venv/bin/activate" in content, "Should activate venv"
        assert "reflex run" in content, "Should run reflex"

    def test_generated_app_gitignore(self):
        """Test that .gitignore is correctly generated."""
        gitignore_file = Path("generated/test_stock_market/.gitignore")
        assert gitignore_file.exists(), ".gitignore should exist"

        content = gitignore_file.read_text()

        # Check important ignore patterns
        assert "venv/" in content, "Should ignore venv"
        assert "__pycache__/" in content, "Should ignore __pycache__"
        assert "*.pyc" in content, "Should ignore .pyc files"
        assert ".web/" in content, "Should ignore .web directory"
        assert "*.log" in content, "Should ignore log files"

    def test_generated_app_compiles(self):
        """Test that the generated app compiles without errors."""
        app_dir = Path("generated/test_stock_market")

        # Try to compile the app (without running it)
        result = subprocess.run(
            [
                "python3",
                "-c",
                f"import sys; sys.path.insert(0, '{app_dir}'); "
                f"from test_stock_market_app import test_stock_market; "
                f"print('OK')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert (
            result.returncode == 0
        ), f"App should import successfully: {result.stderr}"
        assert "OK" in result.stdout, "Import should succeed"

    def test_port_assignment(self):
        """Test that ports are randomly assigned and valid."""
        rxconfig_path = Path("generated/test_stock_market/rxconfig.py")
        content = rxconfig_path.read_text()

        # Extract ports (simplified check)
        backend_port = None
        frontend_port = None

        for line in content.split("\n"):
            if "backend_port=" in line:
                backend_port = int(line.split("=")[1].strip().rstrip(","))
            if "frontend_port=" in line:
                frontend_port = int(line.split("=")[1].strip().rstrip(","))

        assert backend_port is not None, "Should have backend_port"
        assert frontend_port is not None, "Should have frontend_port"

        # Check port range
        assert 3000 <= backend_port <= 5000, "Backend port should be in range 3000-5000"
        assert (
            3000 <= frontend_port <= 5000
        ), "Frontend port should be in range 3000-5000"

        # Check ports are different
        assert (
            backend_port != frontend_port
        ), "Backend and frontend ports should be different"

        # Check frontend is backend + 1
        assert (
            frontend_port == backend_port + 1
        ), "Frontend port should be backend port + 1"


class TestAppNaming:
    """Test app naming conventions."""

    def test_app_name_normalization(self):
        """Test that app names with spaces are normalized."""
        app_dir = Path("generated/test_stock_market")

        # The project name was "Test Stock Market" but directory should be "test_stock_market"
        assert app_dir.exists(), "Directory should use underscores"
        assert not Path(
            "generated/Test Stock Market"
        ).exists(), "Should not use spaces in directory name"

    def test_module_naming_consistency(self):
        """Test that module names are consistent throughout."""
        app_dir = Path("generated/test_stock_market")

        # Check directory names match
        assert (
            app_dir / "test_stock_market_app"
        ).exists(), "App module directory should match naming"

        # Check file names match
        assert (
            app_dir / "test_stock_market_app" / "test_stock_market.py"
        ).exists(), "Main app file should match naming"

        # Check rxconfig references match
        rxconfig_content = (app_dir / "rxconfig.py").read_text()
        assert (
            'app_name="test_stock_market_app"' in rxconfig_content
        ), "rxconfig app_name should match"
        assert (
            'app_module_import="test_stock_market_app.test_stock_market"'
            in rxconfig_content
        ), "rxconfig import path should match"


class TestGeneratedAppContent:
    """Test the content of generated apps."""

    def test_app_displays_project_name(self):
        """Test that the generated app displays the correct project name."""
        main_file = Path(
            "generated/test_stock_market/test_stock_market_app/test_stock_market.py"
        )
        content = main_file.read_text()

        # Check that project name appears in the app
        assert "Test Stock Market" in content, "Should display project name"

    def test_app_displays_description(self):
        """Test that the generated app displays the project description."""
        main_file = Path(
            "generated/test_stock_market/test_stock_market_app/test_stock_market.py"
        )
        content = main_file.read_text()

        # The description should be in the file
        assert "stock market" in content.lower(), "Should display description"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
