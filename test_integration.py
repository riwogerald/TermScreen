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


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflows"""
    
    def test_demo_to_renderer_pipeline(self):
        """Test complete pipeline from demo generation to rendering"""
        # Generate demo data
        demo_data = create_demo_1()
        
        # Verify demo data structure
        self.assertGreater(len(demo_data), 50)
        self.assertEqual(demo_data[0], 0x1)  # Screen setup
        
        # Process with renderer (mocked)
        with patch('renderer.ScreenRenderer') as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer
            mock_renderer.process_command.return_value = True
            mock_renderer.screen = Mock()
            mock_renderer.height = 24
            
            with patch('signal.signal'):
                process_binary_stream(demo_data)
            
            # Verify renderer was used
            mock_renderer.init_screen.assert_called_once()
            self.assertTrue(mock_renderer.process_command.called)
    
    def test_builder_to_file_to_renderer(self):
        """Test workflow: builder -> file -> renderer"""
        # Create command sequence
        builder = BinaryCommandBuilder()
        builder.screen_setup(40, 20, 1)
        builder.clear_screen()
        builder.render_text(5, 5, 7, "Integration Test")
        builder.draw_line(0, 0, 39, 19, 3, ord('*'))
        builder.end_of_file()
        
        data = builder.get_data()
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(data)
            temp_file_path = temp_file.name
        
        try:
            # Read file and process
            with open(temp_file_path, 'rb') as f:
                file_data = f.read()
            
            self.assertEqual(data, file_data)
            
            # Process with mocked renderer
            with patch('renderer.ScreenRenderer') as mock_renderer_class:
                mock_renderer = Mock()
                mock_renderer_class.return_value = mock_renderer
                mock_renderer.screen = Mock()
                mock_renderer.height = 20
                
                with patch('signal.signal'):
                    process_binary_stream(file_data)
                
                mock_renderer.init_screen.assert_called_once()
        
        finally:
            os.unlink(temp_file_path)
    
    def test_all_commands_integration(self):
        """Test integration with all supported commands"""
        builder = BinaryCommandBuilder()
        
        # Use all commands
        builder.screen_setup(60, 15, 2)
        builder.clear_screen()
        builder.render_text(2, 2, 14, "All Commands Test")
        builder.draw_character(5, 5, 12, ord('A'))
        builder.draw_line(10, 3, 50, 3, 9, ord('-'))
        builder.cursor_movement(20, 8)
        builder.draw_at_cursor(ord('X'), 11)
        builder.render_text(2, 12, 8, "Complete!")
        builder.end_of_file()
        
        data = builder.get_data()
        
        # Parse and verify all commands are present
        commands_found = set()
        i = 0
        
        while i < len(data) - 1:
            command = data[i]
            length = data[i + 1]
            commands_found.add(command)
            i += 2 + length
            
            if command == 0xFF:
                break
        
        expected_commands = {0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0xFF}
        self.assertEqual(commands_found, expected_commands)
        
        # Process with renderer
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        
        i = 0
        while i < len(data) - 1:
            command = data[i]
            length = data[i + 1]
            command_data = list(data[i + 2:i + 2 + length])
            
            result = renderer.process_command(command, length, command_data)
            
            if not result:
                break
            
            i += 2 + length
        
        self.assertTrue(renderer.initialized)


class TestCommandLineInterface(unittest.TestCase):
    """Test command line interface functionality"""
    
    def test_demo_main_function(self):
        """Test demo main function with different arguments"""
        # Test demo 1
        with patch('sys.argv', ['demo.py', '1']), \
             patch('sys.stdout') as mock_stdout:
            
            mock_stdout.buffer = Mock()
            demo_main()
            mock_stdout.buffer.write.assert_called_once()
            
            # Verify data starts with screen setup
            written_data = mock_stdout.buffer.write.call_args[0][0]
            self.assertEqual(written_data[0], 0x1)
    
    def test_demo_main_invalid_argument(self):
        """Test demo main with invalid argument"""
        with patch('sys.argv', ['demo.py', '99']), \
             patch('sys.exit') as mock_exit, \
             patch('builtins.print'):
            
            demo_main()
            mock_exit.assert_called_once_with(1)
    
    def test_renderer_main_with_file(self):
        """Test renderer main function with file input"""
        # Create test data
        builder = BinaryCommandBuilder()
        builder.screen_setup(20, 10, 1)
        builder.render_text(0, 0, 7, "Test")
        builder.end_of_file()
        data = builder.get_data()
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(data)
            temp_file_path = temp_file.name
        
        try:
            with patch('sys.argv', ['renderer.py', temp_file_path]), \
                 patch('renderer.process_binary_stream') as mock_process:
                
                main()
                mock_process.assert_called_once_with(data)
        
        finally:
            os.unlink(temp_file_path)


class TestDataValidation(unittest.TestCase):
    """Test data validation and error recovery"""
    
    def test_command_data_validation(self):
        """Test validation of command data"""
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        
        # Test various invalid data scenarios
        test_cases = [
            # (command, length, data, should_continue)
            (0x1, 2, [80, 24], True),  # Screen setup with missing color mode
            (0x2, 3, [10, 10, 5], True),  # Draw character missing char
            (0x3, 5, [0, 0, 10, 10, 5], True),  # Draw line missing char
            (0x4, 2, [10, 10], True),  # Render text missing color and text
            (0x5, 1, [10], True),  # Cursor movement missing y
            (0x6, 1, [65], True),  # Draw at cursor missing color
        ]
        
        for command, length, data, expected_continue in test_cases:
            result = renderer.process_command(command, length, data)
            self.assertEqual(result, expected_continue)
    
    def test_bounds_checking(self):
        """Test coordinate bounds checking"""
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        renderer.initialized = True
        renderer.width = 80
        renderer.height = 24
        
        # Test out-of-bounds coordinates
        with patch.object(renderer, '_safe_addch') as mock_addch, \
             patch.object(renderer, '_safe_addstr') as mock_addstr:
            
            # These should not crash
            renderer._cmd_draw_character([100, 100, 1, ord('A')])
            renderer._cmd_render_text([90, 30, 1] + list(b"Test"))
            
            # Safe methods should be called
            mock_addch.assert_called()
            mock_addstr.assert_called()
    
    def test_color_validation(self):
        """Test color value validation"""
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        renderer.initialized = True
        renderer.color_pairs_initialized = True
        
        with patch('curses.COLOR_PAIRS', 16):
            # Test various color values
            test_colors = [0, 1, 15, 16, 255, -1]
            
            for color in test_colors:
                # Should not crash with any color value
                attr = renderer._get_color_attr(color)
                self.assertIsInstance(attr, int)


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""
    
    def test_text_editor_simulation(self):
        """Simulate a simple text editor scenario"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(80, 24, 1)
        builder.clear_screen()
        
        # Draw title bar
        builder.render_text(0, 0, 15, "Simple Text Editor" + " " * 62)
        
        # Draw content area
        lines = [
            "This is line 1 of the document",
            "Here is line 2 with some text",
            "Line 3 contains more content",
            "",
            "Line 5 after an empty line",
        ]
        
        for i, line in enumerate(lines):
            builder.render_text(0, i + 2, 7, line)
        
        # Draw cursor
        builder.draw_character(31, 2, 15, ord('_'))
        
        # Draw status bar
        builder.render_text(0, 23, 8, "Line 1, Col 32" + " " * 66)
        
        builder.end_of_file()
        data = builder.get_data()
        
        # Verify reasonable data size
        self.assertGreater(len(data), 200)
        self.assertLess(len(data), 1000)
    
    def test_simple_game_display(self):
        """Simulate a simple game display"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(40, 20, 2)
        builder.clear_screen()
        
        # Draw game border
        for x in range(40):
            builder.draw_character(x, 0, 12, ord('#'))
            builder.draw_character(x, 19, 12, ord('#'))
        
        for y in range(20):
            builder.draw_character(0, y, 12, ord('#'))
            builder.draw_character(39, y, 12, ord('#'))
        
        # Draw player
        builder.draw_character(10, 10, 10, ord('@'))
        
        # Draw enemies
        enemy_positions = [(15, 5), (25, 8), (30, 15)]
        for x, y in enemy_positions:
            builder.draw_character(x, y, 9, ord('E'))
        
        # Draw score
        builder.render_text(2, 1, 14, "Score: 1250")
        
        builder.end_of_file()
        data = builder.get_data()
        
        # Process and verify
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        
        i = 0
        commands_processed = 0
        
        while i < len(data) - 1:
            command = data[i]
            length = data[i + 1]
            command_data = list(data[i + 2:i + 2 + length])
            
            result = renderer.process_command(command, length, command_data)
            commands_processed += 1
            
            if not result:
                break
            
            i += 2 + length
        
        self.assertGreater(commands_processed, 50)  # Many draw operations
    
    def test_progress_bar_animation(self):
        """Simulate an animated progress bar"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(60, 10, 1)
        builder.clear_screen()
        
        # Draw static elements
        builder.render_text(5, 3, 7, "Processing...")
        builder.render_text(5, 5, 7, "[" + " " * 40 + "]")
        
        # Simulate progress updates
        for progress in range(0, 41, 5):
            # Clear previous progress
            builder.render_text(6, 5, 7, " " * 40)
            
            # Draw new progress
            filled = "=" * progress
            empty = " " * (40 - progress)
            builder.render_text(6, 5, 10, filled + empty)
            
            # Update percentage
            percentage = int((progress / 40) * 100)
            builder.render_text(20, 7, 12, f"{percentage}% complete")
        
        builder.end_of_file()
        data = builder.get_data()
        
        # Should contain many text rendering commands
        self.assertGreater(len(data), 500)


def run_integration_tests():
    """Run all integration tests"""
    print("Running Integration Tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEndToEndWorkflow,
        TestCommandLineInterface,
        TestDataValidation,
        TestRealWorldScenarios
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Integration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)