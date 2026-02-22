"""Shared unittest base class to avoid duplicated setup code."""

import shutil
import tempfile
import unittest
from pathlib import Path

from reservation_system.services import build_services


class BaseServiceTestCase(unittest.TestCase):
    """Base test case that provides an isolated temporary data directory."""

    def setUp(self) -> None:
        """Create an isolated directory for JSON persistence and build services."""
        self.temp_path = Path(tempfile.mkdtemp(prefix="rs_tests_"))
        self.addCleanup(self._cleanup_temp_dir)

        services = build_services(self.temp_path)
        self.hotels = services["hotels"]
        self.customers = services["customers"]
        self.reservations = services["reservations"]

    def _cleanup_temp_dir(self) -> None:
        """Remove the temporary directory and its contents."""
        shutil.rmtree(self.temp_path, ignore_errors=True)
