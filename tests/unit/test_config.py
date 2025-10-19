"""
Unit tests for configuration management.

Tests cover:
- Port assignment and validation
- Port persistence
- Configuration constants
- Port conflict resolution
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path


class TestPortConfiguration(unittest.TestCase):
    """Test port configuration and assignment."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test config
        self.test_dir = tempfile.mkdtemp()
        self.port_config_file = os.path.join(self.test_dir, ".port_config.json")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_port_range_validation(self):
        """Test that ports are within valid range (3000-5000)."""
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from config import (
            BACKEND_PORT,
            FRONTEND_PORT,
            GENERATED_BACKEND_PORT,
            GENERATED_FRONTEND_PORT,
        )

        # Check all ports are in range
        self.assertGreaterEqual(FRONTEND_PORT, 3000, "Frontend port below minimum")
        self.assertLessEqual(FRONTEND_PORT, 5000, "Frontend port above maximum")

        self.assertGreaterEqual(BACKEND_PORT, 3000, "Backend port below minimum")
        self.assertLessEqual(BACKEND_PORT, 5000, "Backend port above maximum")

        self.assertGreaterEqual(
            GENERATED_FRONTEND_PORT, 3000, "Generated frontend port below minimum"
        )
        self.assertLessEqual(GENERATED_FRONTEND_PORT, 5000, "Generated frontend port above maximum")

        self.assertGreaterEqual(
            GENERATED_BACKEND_PORT, 3000, "Generated backend port below minimum"
        )
        self.assertLessEqual(GENERATED_BACKEND_PORT, 5000, "Generated backend port above maximum")

    def test_port_uniqueness(self):
        """Test that all assigned ports are unique."""
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
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

    def test_port_persistence(self):
        """Test that ports are persisted to JSON file."""
        config_file = Path(__file__).parent.parent.parent / "config" / ".port_config.json"

        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)

            # Check all expected keys exist
            expected_keys = [
                "backend",
                "frontend",
                "generated_backend",
                "generated_frontend",
            ]
            for key in expected_keys:
                self.assertIn(key, config, f"Missing key in config: {key}")

            # Check all values are integers
            for key, value in config.items():
                self.assertIsInstance(value, int, f"Port {key} is not an integer")

    def test_backend_host_configuration(self):
        """Test that backend host is configured correctly."""
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from config import BACKEND_HOST

        self.assertEqual(
            BACKEND_HOST, "0.0.0.0", "Backend host should be 0.0.0.0 for network access"
        )


class TestApplicationConfiguration(unittest.TestCase):
    """Test application configuration constants."""

    def setUp(self):
        """Set up test environment."""
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    def test_app_name(self):
        """Test application name is set correctly."""
        from config.constants import APP_NAME

        self.assertEqual(APP_NAME, "proto_ddf_app")

    def test_supported_sources(self):
        """Test that all expected data sources are configured."""
        from config.constants import SUPPORTED_SOURCES

        expected_sources = [
            "CSV File",
            "JSON API",
            "Database",
            "REST API",
            "Salesforce",
            "Webhook",
        ]

        self.assertEqual(len(SUPPORTED_SOURCES), 6, "Expected 6 data sources")
        for source in expected_sources:
            self.assertIn(source, SUPPORTED_SOURCES, f"Missing data source: {source}")

    def test_netsuite_fields(self):
        """Test NetSuite field mapping configuration."""
        from config.constants import NETSUITE_FIELDS

        expected_fields = ["Customer Name", "Email", "Phone", "Address", "Account ID"]

        self.assertEqual(len(NETSUITE_FIELDS), 5, "Expected 5 NetSuite fields")
        for field in expected_fields:
            self.assertIn(field, NETSUITE_FIELDS, f"Missing NetSuite field: {field}")

    def test_field_mapping_patterns(self):
        """Test field mapping pattern configuration."""
        from config.constants import FIELD_MAPPING_PATTERNS

        required_patterns = ["name", "email", "phone", "address", "id"]

        for pattern in required_patterns:
            self.assertIn(pattern, FIELD_MAPPING_PATTERNS, f"Missing field pattern: {pattern}")
            self.assertIsInstance(
                FIELD_MAPPING_PATTERNS[pattern],
                list,
                f"Pattern {pattern} should be a list",
            )
            self.assertGreater(
                len(FIELD_MAPPING_PATTERNS[pattern]),
                0,
                f"Pattern {pattern} should have at least one mapping",
            )

    def test_integration_settings(self):
        """Test integration settings are within valid ranges."""
        from config.constants import (
            CONNECTION_DELAY_SECONDS,
            DEFAULT_SUCCESS_RATE,
            SYNC_DELAY_SECONDS,
        )

        # Success rate should be between 0 and 1
        self.assertGreaterEqual(DEFAULT_SUCCESS_RATE, 0.0)
        self.assertLessEqual(DEFAULT_SUCCESS_RATE, 1.0)

        # Delays should be positive
        self.assertGreater(SYNC_DELAY_SECONDS, 0)
        self.assertGreater(CONNECTION_DELAY_SECONDS, 0)


if __name__ == "__main__":
    unittest.main()
