#!/usr/bin/env python3
"""
Utility functions and classes to reduce code redundancy across the project
"""

import sys
import time
import unittest
from typing import List, Callable, Any
from contextlib import contextmanager


class MockCursesBase:
    """Base mock curses implementation with common functionality"""
    
    COLOR_PAIRS = 256
    COLORS = 256
    
    class error(Exception):
        pass
    
    @staticmethod
    def _noop(*args, **kwargs):
        """No-operation method for methods that don't need implementation"""
        pass
    
    @staticmethod
    def _return_true(*args, **kwargs):
        return True
    
    @staticmethod
    def _return_zero(*args, **kwargs):
        return 0


def create_mock_curses():
    """Factory function to create a mock curses module"""
    
    class MockCurses(MockCursesBase):
        initscr = lambda: MockScreen()
        start_color = MockCursesBase._noop
        use_default_colors = MockCursesBase._noop
        noecho = MockCursesBase._noop
        cbreak = MockCursesBase._noop
        curs_set = MockCursesBase._noop
        has_colors = MockCursesBase._return_true
        init_pair = MockCursesBase._noop
        color_pair = MockCursesBase._return_zero
        echo = MockCursesBase._noop
        nocbreak = MockCursesBase._noop
        endwin = MockCursesBase._noop
    
    return MockCurses()


class MockScreen:
    """Mock screen implementation"""
    
    def __init__(self):
        self.width = 80
        self.height = 24
    
    def keypad(self, enable):
        pass
    
    def addch(self, y, x, char, attr=0):
        pass
    
    def addstr(self, y, x, text, attr=0):
        pass
    
    def clear(self):
        pass
    
    def refresh(self):
        pass
    
    def move(self, y, x):
        pass
    
    def getch(self):
        return ord('q')  # Simulate quit key
    
    def resize(self, height, width):
        self.height = height
        self.width = width


@contextmanager
def preserve_sys_state():
    """Context manager to preserve and restore sys.path and sys.argv"""
    original_path = sys.path[:]
    original_argv = sys.argv[:]
    
    try:
        yield
    finally:
        sys.path[:] = original_path
        sys.argv[:] = original_argv


def safe_curses_operation(operation: Callable, *args, **kwargs) -> Any:
    """Safely execute a curses operation, catching and ignoring curses errors"""
    try:
        return operation(*args, **kwargs)
    except Exception:
        # Ignore all curses-related errors
        return None


def validate_command_data(data: List[int], min_length: int) -> bool:
    """Validate command data has minimum required length"""
    return len(data) >= min_length


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp a value between min and max bounds"""
    return max(min_val, min(value, max_val))


def run_test_suite_with_summary(test_classes: List[type], suite_name: str) -> bool:
    """Run a test suite and print summary"""
    print(f"Running {suite_name}...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"{suite_name} Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_count = result.testsRun - len(result.failures) - len(result.errors)
        success_rate = (success_count / result.testsRun) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    print(f"{'='*60}")
    
    return result.wasSuccessful()


class BatchRenderer:
    """Helper class to batch screen refresh operations"""
    
    def __init__(self, screen):
        self.screen = screen
        self.needs_refresh = False
    
    def mark_dirty(self):
        """Mark that screen needs refresh"""
        self.needs_refresh = True
    
    def flush(self):
        """Refresh screen if needed"""
        if self.needs_refresh and self.screen:
            safe_curses_operation(self.screen.refresh)
            self.needs_refresh = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
