#!/usr/bin/env python3
"""
Integration tests for the terminal screen renderer
Tests the complete workflow from demo generation to rendering
"""
import unittest
import tempfile
import os
import sys
import subprocess
from unittest.mock import patch, Mock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from renderer import ScreenRenderer, process_binary_stream, main
from demo import BinaryCommandBuilder, create_demo_1, create_demo_2, main as demo_main
from utils import run_test_suite_with_summary
    return run_test_suite_with_summary(test_classes, "Integration Tests")


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)