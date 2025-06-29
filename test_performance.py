#!/usr/bin/env python3
"""
Performance and stress tests for the terminal screen renderer
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from renderer import ScreenRenderer, process_binary_stream
from demo import BinaryCommandBuilder


class TestPerformance(unittest.TestCase):
    """Performance tests for the renderer"""
    
    def setUp(self):
        self.renderer = ScreenRenderer()
        self.renderer.screen = Mock()
        self.renderer.initialized = True
        self.renderer.width = 80
        self.renderer.height = 24
    
    def test_large_text_rendering_performance(self):
        """Test performance with large text rendering"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(80, 24, 2)
        
        # Generate large amount of text
        start_time = time.time()
        for y in range(24):
            text = f"Line {y:2d}: " + "A" * 70
            builder.render_text(0, y, y % 16, text)
        
        builder.end_of_file()
        data = builder.get_data()
        build_time = time.time() - start_time
        
        # Should build quickly
        self.assertLess(build_time, 1.0, "Building large text should be fast")
        
        # Verify data size is reasonable
        self.assertGreater(len(data), 1000)
        self.assertLess(len(data), 10000)
    
    def test_many_character_draws_performance(self):
        """Test performance with many individual character draws"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(80, 24, 2)
        
        start_time = time.time()
        
        # Draw 1000 individual characters
        for i in range(1000):
            x = i % 80
            y = (i // 80) % 24
            color = i % 16
            char = ord('A') + (i % 26)
            builder.draw_character(x, y, color, char)
        
        builder.end_of_file()
        data = builder.get_data()
        build_time = time.time() - start_time
        
        # Should build reasonably quickly
        self.assertLess(build_time, 2.0, "Building many characters should be reasonably fast")
        
        # Verify correct number of commands
        # Each character = 6 bytes (command + length + 4 data)
        # Plus screen setup (5 bytes) and EOF (2 bytes)
        expected_size = 1000 * 6 + 5 + 2
        self.assertEqual(len(data), expected_size)
    
    def test_line_drawing_performance(self):
        """Test performance with complex line drawing"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(80, 24, 2)
        
        start_time = time.time()
        
        # Draw many lines
        for i in range(100):
            x1, y1 = i % 80, i % 24
            x2, y2 = (i + 20) % 80, (i + 10) % 24
            builder.draw_line(x1, y1, x2, y2, i % 16, ord('*'))
        
        builder.end_of_file()
        data = builder.get_data()
        build_time = time.time() - start_time
        
        self.assertLess(build_time, 1.0, "Line drawing should be fast")
    
    def test_command_processing_performance(self):
        """Test performance of command processing"""
        # Create test data
        builder = BinaryCommandBuilder()
        builder.screen_setup(80, 24, 2)
        
        for i in range(500):
            builder.draw_character(i % 80, (i // 80) % 24, i % 16, ord('A') + (i % 26))
        
        builder.end_of_file()
        data = builder.get_data()
        
        # Process commands and measure time
        start_time = time.time()
        
        i = 0
        commands_processed = 0
        
        while i < len(data) - 1:
            command = data[i]
            length = data[i + 1]
            command_data = list(data[i + 2:i + 2 + length])
            
            result = self.renderer.process_command(command, length, command_data)
            commands_processed += 1
            
            if not result:
                break
            
            i += 2 + length
        
        process_time = time.time() - start_time
        
        # Should process quickly
        self.assertLess(process_time, 1.0, "Command processing should be fast")
        self.assertGreater(commands_processed, 500)


class TestStress(unittest.TestCase):
    """Stress tests for edge cases and limits"""
    
    def setUp(self):
        self.renderer = ScreenRenderer()
        self.renderer.screen = Mock()
    
    def test_maximum_screen_size(self):
        """Test with maximum screen dimensions"""
        result = self.renderer._cmd_screen_setup([255, 255, 2])
        
        self.assertTrue(result)
        self.assertTrue(self.renderer.initialized)
        self.assertEqual(self.renderer.width, 255)
        self.assertEqual(self.renderer.height, 255)
    
    def test_minimum_screen_size(self):
        """Test with minimum screen dimensions"""
        result = self.renderer._cmd_screen_setup([1, 1, 0])
        
        self.assertTrue(result)
        self.assertTrue(self.renderer.initialized)
        self.assertEqual(self.renderer.width, 1)
        self.assertEqual(self.renderer.height, 1)
    
    def test_extreme_coordinates(self):
        """Test with extreme coordinate values"""
        self.renderer.initialized = True
        self.renderer.width = 80
        self.renderer.height = 24
        
        # Test with very large coordinates
        with patch.object(self.renderer, '_safe_addch') as mock_addch:
            self.renderer._cmd_draw_character([1000, 1000, 1, ord('A')])
            # Should not crash, safe_addch should handle bounds
            mock_addch.assert_called_once()
    
    def test_very_long_text(self):
        """Test with very long text strings"""
        self.renderer.initialized = True
        self.renderer.width = 80
        self.renderer.height = 24
        
        # Create very long text
        long_text = "A" * 1000
        text_bytes = long_text.encode('ascii')
        data = [10, 10, 7] + list(text_bytes)
        
        with patch.object(self.renderer, '_safe_addstr') as mock_addstr:
            result = self.renderer._cmd_render_text(data)
            self.assertTrue(result)
            mock_addstr.assert_called_once()
    
    def test_many_color_changes(self):
        """Test with many different colors"""
        self.renderer.initialized = True
        self.renderer.color_pairs_initialized = True
        
        with patch('curses.COLOR_PAIRS', 256), \
             patch('curses.color_pair', return_value=42):
            
            # Test all possible color values
            for color in range(256):
                attr = self.renderer._get_color_attr(color)
                self.assertIsInstance(attr, int)
    
    def test_malformed_command_stream(self):
        """Test with various malformed command streams"""
        test_cases = [
            b'',  # Empty stream
            b'\x01',  # Command without length
            b'\x01\x05\x50',  # Incomplete data
            b'\x99\x02\x01\x02',  # Unknown command
            b'\x01\x03\x50\x18\x01\x02\xFF',  # Invalid command in middle
        ]
        
        for test_data in test_cases:
            renderer = ScreenRenderer()
            renderer.screen = Mock()
            
            # Should not crash with malformed data
            i = 0
            while i < len(test_data) - 1:
                if i + 1 >= len(test_data):
                    break
                
                command = test_data[i]
                length = test_data[i + 1]
                
                if i + 2 + length > len(test_data):
                    break
                
                command_data = list(test_data[i + 2:i + 2 + length])
                renderer.process_command(command, length, command_data)
                
                i += 2 + length
    
    def test_rapid_cursor_movement(self):
        """Test rapid cursor movements"""
        self.renderer.initialized = True
        self.renderer.width = 80
        self.renderer.height = 24
        
        # Rapid cursor movements
        for i in range(1000):
            x = i % 80
            y = (i // 80) % 24
            result = self.renderer._cmd_cursor_movement([x, y])
            self.assertTrue(result)
            self.assertEqual(self.renderer.cursor_x, x)
            self.assertEqual(self.renderer.cursor_y, y)
    
    def test_memory_usage_large_builder(self):
        """Test memory usage with large command builder"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(80, 24, 2)
        
        # Add many commands
        for i in range(10000):
            if i % 4 == 0:
                builder.draw_character(i % 80, (i // 80) % 24, i % 16, ord('A'))
            elif i % 4 == 1:
                builder.render_text(i % 80, (i // 80) % 24, i % 16, f"Text{i}")
            elif i % 4 == 2:
                builder.cursor_movement(i % 80, (i // 80) % 24)
            else:
                builder.draw_at_cursor(ord('B'), i % 16)
        
        builder.end_of_file()
        data = builder.get_data()
        
        # Should create substantial data but not excessive
        self.assertGreater(len(data), 50000)
        self.assertLess(len(data), 500000)  # Should be reasonable size


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery"""
    
    def setUp(self):
        self.renderer = ScreenRenderer()
        self.renderer.screen = Mock()
        self.renderer.initialized = True
    
    def test_curses_error_handling(self):
        """Test handling of curses errors"""
        import curses
        
        # Mock curses errors
        self.renderer.screen.addch.side_effect = curses.error("Mock error")
        self.renderer.screen.addstr.side_effect = curses.error("Mock error")
        self.renderer.screen.clear.side_effect = curses.error("Mock error")
        
        # Should not raise exceptions
        self.renderer._safe_addch(10, 10, ord('A'), 0)
        self.renderer._safe_addstr(10, 10, "Test", 0)
        self.renderer._cmd_clear_screen([])
    
    def test_unicode_handling(self):
        """Test handling of non-ASCII characters"""
        self.renderer.initialized = True
        
        # Test with unicode text that should be replaced
        unicode_text = "Hello 世界 🌍"
        text_bytes = unicode_text.encode('ascii', errors='replace')
        data = [10, 10, 7] + list(text_bytes)
        
        with patch.object(self.renderer, '_safe_addstr') as mock_addstr:
            result = self.renderer._cmd_render_text(data)
            self.assertTrue(result)
            mock_addstr.assert_called_once()
    
    def test_exception_in_command_processing(self):
        """Test exception handling in command processing"""
        with patch.object(self.renderer, '_cmd_draw_character', side_effect=Exception("Test error")):
            # Should continue processing despite exception
            result = self.renderer.process_command(0x2, 4, [10, 10, 1, ord('A')])
            self.assertTrue(result)
    
    def test_invalid_color_handling(self):
        """Test handling of invalid color values"""
        self.renderer.color_pairs_initialized = True
        
        with patch('curses.COLOR_PAIRS', 16), \
             patch('curses.color_pair', side_effect=Exception("Invalid color")):
            
            # Should fallback gracefully
            attr = self.renderer._get_color_attr(999)
            self.assertEqual(attr, 0)


def run_performance_tests():
    """Run performance and stress tests"""
    print("Running Performance and Stress Tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPerformance,
        TestStress,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Performance Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)