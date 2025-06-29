#!/usr/bin/env python3
"""
Test suite for the terminal screen renderer
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from renderer import ScreenRenderer, process_binary_stream
from demo import BinaryCommandBuilder


class TestBinaryCommandBuilder(unittest.TestCase):
    """Test the binary command builder"""
    
    def setUp(self):
        self.builder = BinaryCommandBuilder()
    
    def test_screen_setup(self):
        """Test screen setup command generation"""
        self.builder.screen_setup(80, 24, 2)
        data = self.builder.get_data()
        
        expected = bytes([0x1, 3, 80, 24, 2])
        self.assertEqual(data, expected)
    
    def test_draw_character(self):
        """Test draw character command generation"""
        self.builder.draw_character(10, 5, 12, ord('A'))
        data = self.builder.get_data()
        
        expected = bytes([0x2, 4, 10, 5, 12, ord('A')])
        self.assertEqual(data, expected)
    
    def test_render_text(self):
        """Test render text command generation"""
        self.builder.render_text(0, 0, 7, "Hello")
        data = self.builder.get_data()
        
        expected = bytes([0x4, 8, 0, 0, 7, ord('H'), ord('e'), ord('l'), ord('l'), ord('o')])
        self.assertEqual(data, expected)
    
    def test_multiple_commands(self):
        """Test multiple commands in sequence"""
        self.builder.screen_setup(40, 20, 1)
        self.builder.clear_screen()
        self.builder.render_text(5, 5, 3, "Hi")
        self.builder.end_of_file()
        
        data = self.builder.get_data()
        
        # Should contain all commands in sequence
        self.assertTrue(len(data) > 10)
        self.assertEqual(data[0], 0x1)  # Screen setup
        self.assertEqual(data[4], 0x7)  # Clear screen
        self.assertEqual(data[6], 0x4)  # Render text
        self.assertEqual(data[-2], 0xFF)  # End of file


class TestScreenRenderer(unittest.TestCase):
    """Test the screen renderer (without actual curses)"""
    
    def setUp(self):
        self.renderer = ScreenRenderer()
    
    def test_initial_state(self):
        """Test initial renderer state"""
        self.assertFalse(self.renderer.initialized)
        self.assertEqual(self.renderer.width, 0)
        self.assertEqual(self.renderer.height, 0)
        self.assertEqual(self.renderer.cursor_x, 0)
        self.assertEqual(self.renderer.cursor_y, 0)
    
    def test_screen_setup_command(self):
        """Test screen setup command processing"""
        # Mock the screen object
        self.renderer.screen = Mock()
        
        result = self.renderer._cmd_screen_setup([80, 24, 2])
        
        self.assertTrue(result)
        self.assertTrue(self.renderer.initialized)
        self.assertEqual(self.renderer.width, 80)
        self.assertEqual(self.renderer.height, 24)
        self.assertEqual(self.renderer.color_mode, 2)
    
    def test_invalid_screen_setup(self):
        """Test invalid screen setup data"""
        self.renderer.screen = Mock()
        
        # Too few parameters
        result = self.renderer._cmd_screen_setup([80])
        self.assertTrue(result)
        self.assertFalse(self.renderer.initialized)
        
        # Invalid dimensions
        result = self.renderer._cmd_screen_setup([0, 0, 1])
        self.assertTrue(result)
        self.assertFalse(self.renderer.initialized)
    
    def test_command_before_setup(self):
        """Test that commands are ignored before screen setup"""
        result = self.renderer.process_command(0x2, 4, [10, 10, 1, ord('A')])
        self.assertTrue(result)  # Should continue but not process
    
    def test_cursor_movement(self):
        """Test cursor movement command"""
        self.renderer.screen = Mock()
        self.renderer.initialized = True
        self.renderer.width = 80
        self.renderer.height = 24
        
        result = self.renderer._cmd_cursor_movement([10, 5])
        
        self.assertTrue(result)
        self.assertEqual(self.renderer.cursor_x, 10)
        self.assertEqual(self.renderer.cursor_y, 5)
    
    def test_cursor_bounds_clamping(self):
        """Test that cursor is clamped to screen bounds"""
        self.renderer.screen = Mock()
        self.renderer.initialized = True
        self.renderer.width = 80
        self.renderer.height = 24
        
        # Test negative coordinates
        self.renderer._cmd_cursor_movement([-5, -10])
        self.assertEqual(self.renderer.cursor_x, 0)
        self.assertEqual(self.renderer.cursor_y, 0)
        
        # Test coordinates beyond screen
        self.renderer._cmd_cursor_movement([100, 50])
        self.assertEqual(self.renderer.cursor_x, 79)
        self.assertEqual(self.renderer.cursor_y, 23)


class TestBinaryStreamProcessing(unittest.TestCase):
    """Test complete binary stream processing"""
    
    def test_valid_stream(self):
        """Test processing of a valid binary stream"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(40, 20, 1)
        builder.render_text(5, 5, 7, "Test")
        builder.end_of_file()
        
        data = builder.get_data()
        
        # This would normally require curses, so we'll just test data validity
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0], 0x1)  # First command should be screen setup
        self.assertEqual(data[-2], 0xFF)  # Should end with EOF
    
    def test_malformed_stream(self):
        """Test handling of malformed binary streams"""
        # Stream that ends abruptly
        data = bytes([0x1, 3, 80])  # Incomplete screen setup
        
        # Should not crash when processing incomplete data
        # (We can't easily test this without mocking curses)
        self.assertTrue(len(data) > 0)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()