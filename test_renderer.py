#!/usr/bin/env python3
"""
Comprehensive test suite for the terminal screen renderer
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import io
import tempfile
import struct

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from renderer import ScreenRenderer, process_binary_stream
from demo import BinaryCommandBuilder, create_demo_1, create_demo_2


class TestBinaryCommandBuilder(unittest.TestCase):
    """Test the binary command builder"""
    
    def setUp(self):
        self.builder = BinaryCommandBuilder()
    
    def test_empty_builder(self):
        """Test empty builder returns empty data"""
        data = self.builder.get_data()
        self.assertEqual(data, b'')
    
    def test_screen_setup(self):
        """Test screen setup command generation"""
        self.builder.screen_setup(80, 24, 2)
        data = self.builder.get_data()
        
        expected = bytes([0x1, 3, 80, 24, 2])
        self.assertEqual(data, expected)
    
    def test_screen_setup_edge_cases(self):
        """Test screen setup with edge case values"""
        # Minimum values
        self.builder.screen_setup(1, 1, 0)
        data = self.builder.get_data()
        expected = bytes([0x1, 3, 1, 1, 0])
        self.assertEqual(data, expected)
        
        # Maximum byte values
        builder2 = BinaryCommandBuilder()
        builder2.screen_setup(255, 255, 2)
        data2 = builder2.get_data()
        expected2 = bytes([0x1, 3, 255, 255, 2])
        self.assertEqual(data2, expected2)
    
    def test_draw_character(self):
        """Test draw character command generation"""
        self.builder.draw_character(10, 5, 12, ord('A'))
        data = self.builder.get_data()
        
        expected = bytes([0x2, 4, 10, 5, 12, ord('A')])
        self.assertEqual(data, expected)
    
    def test_draw_character_special_chars(self):
        """Test draw character with special characters"""
        special_chars = [0, 32, 127, 255]  # null, space, DEL, extended
        for char in special_chars:
            builder = BinaryCommandBuilder()
            builder.draw_character(0, 0, 1, char)
            data = builder.get_data()
            expected = bytes([0x2, 4, 0, 0, 1, char])
            self.assertEqual(data, expected)
    
    def test_draw_line(self):
        """Test draw line command generation"""
        self.builder.draw_line(0, 0, 10, 10, 5, ord('*'))
        data = self.builder.get_data()
        
        expected = bytes([0x3, 6, 0, 0, 10, 10, 5, ord('*')])
        self.assertEqual(data, expected)
    
    def test_draw_line_same_point(self):
        """Test draw line with same start and end point"""
        self.builder.draw_line(5, 5, 5, 5, 3, ord('.'))
        data = self.builder.get_data()
        
        expected = bytes([0x3, 6, 5, 5, 5, 5, 3, ord('.')])
        self.assertEqual(data, expected)
    
    def test_render_text(self):
        """Test render text command generation"""
        self.builder.render_text(0, 0, 7, "Hello")
        data = self.builder.get_data()
        
        expected = bytes([0x4, 8, 0, 0, 7, ord('H'), ord('e'), ord('l'), ord('l'), ord('o')])
        self.assertEqual(data, expected)
    
    def test_render_text_empty(self):
        """Test render text with empty string"""
        self.builder.render_text(5, 5, 1, "")
        data = self.builder.get_data()
        
        expected = bytes([0x4, 3, 5, 5, 1])
        self.assertEqual(data, expected)
    
    def test_render_text_special_chars(self):
        """Test render text with special characters"""
        text = "Hello\nWorld\t!"
        self.builder.render_text(0, 0, 2, text)
        data = self.builder.get_data()
        
        text_bytes = text.encode('ascii', errors='replace')
        expected = bytes([0x4, 3 + len(text_bytes), 0, 0, 2]) + text_bytes
        self.assertEqual(data, expected)
    
    def test_cursor_movement(self):
        """Test cursor movement command generation"""
        self.builder.cursor_movement(15, 8)
        data = self.builder.get_data()
        
        expected = bytes([0x5, 2, 15, 8])
        self.assertEqual(data, expected)
    
    def test_draw_at_cursor(self):
        """Test draw at cursor command generation"""
        self.builder.draw_at_cursor(ord('X'), 9)
        data = self.builder.get_data()
        
        expected = bytes([0x6, 2, ord('X'), 9])
        self.assertEqual(data, expected)
    
    def test_clear_screen(self):
        """Test clear screen command generation"""
        self.builder.clear_screen()
        data = self.builder.get_data()
        
        expected = bytes([0x7, 0])
        self.assertEqual(data, expected)
    
    def test_end_of_file(self):
        """Test end of file command generation"""
        self.builder.end_of_file()
        data = self.builder.get_data()
        
        expected = bytes([0xFF, 0])
        self.assertEqual(data, expected)
    
    def test_multiple_commands(self):
        """Test multiple commands in sequence"""
        self.builder.screen_setup(40, 20, 1)
        self.builder.clear_screen()
        self.builder.render_text(5, 5, 3, "Hi")
        self.builder.cursor_movement(10, 10)
        self.builder.draw_at_cursor(ord('!'), 4)
        self.builder.end_of_file()
        
        data = self.builder.get_data()
        
        # Verify structure
        self.assertTrue(len(data) > 15)
        self.assertEqual(data[0], 0x1)   # Screen setup
        self.assertEqual(data[4], 0x7)   # Clear screen
        self.assertEqual(data[6], 0x4)   # Render text
        self.assertEqual(data[12], 0x5)  # Cursor movement
        self.assertEqual(data[15], 0x6)  # Draw at cursor
        self.assertEqual(data[-2], 0xFF) # End of file
    
    def test_add_command_directly(self):
        """Test the add_command method directly"""
        self.builder.add_command(0x99, [1, 2, 3])
        data = self.builder.get_data()
        
        expected = bytes([0x99, 3, 1, 2, 3])
        self.assertEqual(data, expected)
    
    def test_add_command_empty_data(self):
        """Test add_command with empty data"""
        self.builder.add_command(0x88, [])
        data = self.builder.get_data()
        
        expected = bytes([0x88, 0])
        self.assertEqual(data, expected)


class TestScreenRenderer(unittest.TestCase):
    """Test the screen renderer (with mocked curses)"""
    
    def setUp(self):
        self.renderer = ScreenRenderer()
        self.mock_screen = Mock()
        self.renderer.screen = self.mock_screen
    
    def test_initial_state(self):
        """Test initial renderer state"""
        renderer = ScreenRenderer()
        self.assertFalse(renderer.initialized)
        self.assertEqual(renderer.width, 0)
        self.assertEqual(renderer.height, 0)
        self.assertEqual(renderer.cursor_x, 0)
        self.assertEqual(renderer.cursor_y, 0)
        self.assertFalse(renderer.color_pairs_initialized)
    
    @patch('curses.initscr')
    @patch('curses.start_color')
    @patch('curses.use_default_colors')
    @patch('curses.noecho')
    @patch('curses.cbreak')
    @patch('curses.curs_set')
    @patch('curses.has_colors')
    def test_init_screen_success(self, mock_has_colors, mock_curs_set, 
                                mock_cbreak, mock_noecho, mock_use_default,
                                mock_start_color, mock_initscr):
        """Test successful screen initialization"""
        mock_screen = Mock()
        mock_initscr.return_value = mock_screen
        mock_has_colors.return_value = True
        
        renderer = ScreenRenderer()
        
        with patch.object(renderer, '_init_color_pairs'):
            renderer.init_screen()
        
        self.assertEqual(renderer.screen, mock_screen)
        mock_initscr.assert_called_once()
        mock_start_color.assert_called_once()
        mock_use_default.assert_called_once()
        mock_noecho.assert_called_once()
        mock_cbreak.assert_called_once()
        mock_curs_set.assert_called_once_with(0)
    
    @patch('curses.initscr')
    def test_init_screen_failure(self, mock_initscr):
        """Test screen initialization failure"""
        mock_initscr.side_effect = Exception("Curses init failed")
        
        renderer = ScreenRenderer()
        
        with self.assertRaises(RuntimeError):
            renderer.init_screen()
    
    @patch('curses.COLORS', 256)
    @patch('curses.COLOR_PAIRS', 256)
    @patch('curses.init_pair')
    def test_init_color_pairs(self, mock_init_pair):
        """Test color pairs initialization"""
        self.renderer._init_color_pairs()
        
        # Should initialize color pairs 1-255
        self.assertTrue(mock_init_pair.called)
        self.assertTrue(self.renderer.color_pairs_initialized)
    
    @patch('curses.init_pair')
    def test_init_color_pairs_with_errors(self, mock_init_pair):
        """Test color pairs initialization with curses errors"""
        import curses
        mock_init_pair.side_effect = curses.error("Color not supported")
        
        # Should not raise exception
        self.renderer._init_color_pairs()
    
    def test_cleanup(self):
        """Test cleanup method"""
        mock_screen = Mock()
        self.renderer.screen = mock_screen
        
        with patch('curses.echo'), patch('curses.nocbreak'), \
             patch('curses.curs_set'), patch('curses.endwin'):
            self.renderer.cleanup()
    
    def test_cleanup_with_none_screen(self):
        """Test cleanup with None screen"""
        self.renderer.screen = None
        # Should not raise exception
        self.renderer.cleanup()
    
    def test_safe_addch_valid(self):
        """Test safe_addch with valid coordinates"""
        self.renderer.width = 80
        self.renderer.height = 24
        
        self.renderer._safe_addch(10, 20, ord('A'), 0)
        self.mock_screen.addch.assert_called_once_with(10, 20, ord('A'), 0)
    
    def test_safe_addch_invalid_coords(self):
        """Test safe_addch with invalid coordinates"""
        self.renderer.width = 80
        self.renderer.height = 24
        
        # Out of bounds coordinates
        self.renderer._safe_addch(-1, 20, ord('A'), 0)
        self.renderer._safe_addch(10, -1, ord('A'), 0)
        self.renderer._safe_addch(25, 20, ord('A'), 0)
        self.renderer._safe_addch(10, 85, ord('A'), 0)
        
        # Should not call addch for any of these
        self.mock_screen.addch.assert_not_called()
    
    def test_safe_addch_curses_error(self):
        """Test safe_addch handling curses errors"""
        import curses
        self.renderer.width = 80
        self.renderer.height = 24
        self.mock_screen.addch.side_effect = curses.error("Cannot draw")
        
        # Should not raise exception
        self.renderer._safe_addch(10, 20, ord('A'), 0)
    
    def test_safe_addstr_valid(self):
        """Test safe_addstr with valid coordinates"""
        self.renderer.width = 80
        self.renderer.height = 24
        
        self.renderer._safe_addstr(10, 20, "Hello", 0)
        self.mock_screen.addstr.assert_called_once_with(10, 20, "Hello", 0)
    
    def test_safe_addstr_truncation(self):
        """Test safe_addstr with text truncation"""
        self.renderer.width = 30
        self.renderer.height = 24
        
        long_text = "This is a very long text that exceeds screen width"
        self.renderer._safe_addstr(10, 25, long_text, 0)
        
        # Should truncate to fit remaining width
        expected_text = long_text[:5]  # 30 - 25 = 5 characters
        self.mock_screen.addstr.assert_called_once_with(10, 25, expected_text, 0)
    
    def test_get_color_attr(self):
        """Test color attribute generation"""
        self.renderer.color_pairs_initialized = True
        
        with patch('curses.COLOR_PAIRS', 256), patch('curses.color_pair') as mock_color_pair:
            mock_color_pair.return_value = 42
            
            attr = self.renderer._get_color_attr(5)
            self.assertEqual(attr, 42)
            mock_color_pair.assert_called_once_with(5)
    
    def test_get_color_attr_fallback(self):
        """Test color attribute fallback"""
        self.renderer.color_pairs_initialized = False
        
        attr = self.renderer._get_color_attr(5)
        self.assertEqual(attr, 0)
    
    def test_screen_setup_command(self):
        """Test screen setup command processing"""
        result = self.renderer._cmd_screen_setup([80, 24, 2])
        
        self.assertTrue(result)
        self.assertTrue(self.renderer.initialized)
        self.assertEqual(self.renderer.width, 80)
        self.assertEqual(self.renderer.height, 24)
        self.assertEqual(self.renderer.color_mode, 2)
    
    def test_screen_setup_invalid_data(self):
        """Test screen setup with invalid data"""
        # Too few parameters
        result = self.renderer._cmd_screen_setup([80])
        self.assertTrue(result)
        self.assertFalse(self.renderer.initialized)
        
        # Invalid dimensions
        result = self.renderer._cmd_screen_setup([0, 0, 1])
        self.assertTrue(result)
        self.assertFalse(self.renderer.initialized)
        
        result = self.renderer._cmd_screen_setup([-10, 20, 1])
        self.assertTrue(result)
        self.assertFalse(self.renderer.initialized)
    
    def test_draw_character_command(self):
        """Test draw character command"""
        self.renderer.initialized = True
        
        with patch.object(self.renderer, '_get_color_attr', return_value=5), \
             patch.object(self.renderer, '_safe_addch') as mock_addch:
            
            result = self.renderer._cmd_draw_character([10, 5, 3, ord('A')])
            
            self.assertTrue(result)
            mock_addch.assert_called_once_with(5, 10, ord('A'), 5)
    
    def test_draw_character_invalid_data(self):
        """Test draw character with invalid data"""
        self.renderer.initialized = True
        
        result = self.renderer._cmd_draw_character([10, 5])  # Too few params
        self.assertTrue(result)  # Should continue processing
    
    def test_draw_line_command(self):
        """Test draw line command"""
        self.renderer.initialized = True
        
        with patch.object(self.renderer, '_get_color_attr', return_value=3), \
             patch.object(self.renderer, '_draw_line') as mock_draw_line:
            
            result = self.renderer._cmd_draw_line([0, 0, 10, 10, 5, ord('*')])
            
            self.assertTrue(result)
            mock_draw_line.assert_called_once_with(0, 0, 10, 10, ord('*'), 3)
    
    def test_render_text_command(self):
        """Test render text command"""
        self.renderer.initialized = True
        
        with patch.object(self.renderer, '_get_color_attr', return_value=7), \
             patch.object(self.renderer, '_safe_addstr') as mock_addstr:
            
            text_data = [5, 10, 3] + list(b"Hello")
            result = self.renderer._cmd_render_text(text_data)
            
            self.assertTrue(result)
            mock_addstr.assert_called_once_with(10, 5, "Hello", 7)
    
    def test_cursor_movement_command(self):
        """Test cursor movement command"""
        self.renderer.initialized = True
        self.renderer.width = 80
        self.renderer.height = 24
        
        result = self.renderer._cmd_cursor_movement([10, 5])
        
        self.assertTrue(result)
        self.assertEqual(self.renderer.cursor_x, 10)
        self.assertEqual(self.renderer.cursor_y, 5)
    
    def test_cursor_bounds_clamping(self):
        """Test cursor bounds clamping"""
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
    
    def test_draw_at_cursor_command(self):
        """Test draw at cursor command"""
        self.renderer.initialized = True
        self.renderer.cursor_x = 15
        self.renderer.cursor_y = 8
        
        with patch.object(self.renderer, '_get_color_attr', return_value=4), \
             patch.object(self.renderer, '_safe_addch') as mock_addch:
            
            result = self.renderer._cmd_draw_at_cursor([ord('X'), 2])
            
            self.assertTrue(result)
            mock_addch.assert_called_once_with(8, 15, ord('X'), 4)
    
    def test_clear_screen_command(self):
        """Test clear screen command"""
        self.renderer.initialized = True
        
        result = self.renderer._cmd_clear_screen([])
        
        self.assertTrue(result)
        self.mock_screen.clear.assert_called_once()
        self.mock_screen.refresh.assert_called()
    
    def test_draw_line_algorithm(self):
        """Test line drawing algorithm"""
        self.renderer.width = 80
        self.renderer.height = 24
        
        with patch.object(self.renderer, '_safe_addch') as mock_addch:
            # Test horizontal line
            self.renderer._draw_line(0, 5, 10, 5, ord('-'), 0)
            self.assertEqual(mock_addch.call_count, 11)  # 0 to 10 inclusive
            
            mock_addch.reset_mock()
            
            # Test vertical line
            self.renderer._draw_line(5, 0, 5, 10, ord('|'), 0)
            self.assertEqual(mock_addch.call_count, 11)  # 0 to 10 inclusive
            
            mock_addch.reset_mock()
            
            # Test diagonal line
            self.renderer._draw_line(0, 0, 5, 5, ord('\\'), 0)
            self.assertEqual(mock_addch.call_count, 6)  # 0 to 5 inclusive
    
    def test_process_command_before_setup(self):
        """Test that commands are ignored before screen setup"""
        result = self.renderer.process_command(0x2, 4, [10, 10, 1, ord('A')])
        self.assertTrue(result)  # Should continue but not process
        self.assertFalse(self.renderer.initialized)
    
    def test_process_command_unknown(self):
        """Test processing unknown command"""
        self.renderer.initialized = True
        
        result = self.renderer.process_command(0x99, 2, [1, 2])
        self.assertTrue(result)  # Should continue processing
    
    def test_process_command_end_of_file(self):
        """Test end of file command"""
        self.renderer.initialized = True
        
        result = self.renderer.process_command(0xFF, 0, [])
        self.assertFalse(result)  # Should stop processing
    
    def test_process_command_exception_handling(self):
        """Test command processing with exceptions"""
        self.renderer.initialized = True
        
        with patch.object(self.renderer, '_cmd_draw_character', side_effect=Exception("Test error")):
            result = self.renderer.process_command(0x2, 4, [10, 10, 1, ord('A')])
            self.assertTrue(result)  # Should continue despite error


class TestDemoGeneration(unittest.TestCase):
    """Test demo data generation"""
    
    def test_create_demo_1(self):
        """Test demo 1 generation"""
        data = create_demo_1()
        
        self.assertIsInstance(data, bytes)
        self.assertTrue(len(data) > 0)
        
        # Should start with screen setup
        self.assertEqual(data[0], 0x1)
        
        # Should end with EOF
        self.assertEqual(data[-2], 0xFF)
    
    def test_create_demo_2(self):
        """Test demo 2 generation"""
        data = create_demo_2()
        
        self.assertIsInstance(data, bytes)
        self.assertTrue(len(data) > 0)
        
        # Should start with screen setup
        self.assertEqual(data[0], 0x1)
        
        # Should end with EOF
        self.assertEqual(data[-2], 0xFF)
    
    def test_demo_data_structure(self):
        """Test that demo data has valid structure"""
        data = create_demo_1()
        
        i = 0
        commands_found = []
        
        while i < len(data) - 1:
            command = data[i]
            length = data[i + 1]
            
            commands_found.append(command)
            
            # Validate length doesn't exceed remaining data
            self.assertLessEqual(i + 2 + length, len(data))
            
            i += 2 + length
            
            if command == 0xFF:  # EOF
                break
        
        # Should contain screen setup and EOF
        self.assertIn(0x1, commands_found)
        self.assertIn(0xFF, commands_found)


class TestBinaryStreamProcessing(unittest.TestCase):
    """Test complete binary stream processing"""
    
    @patch('renderer.ScreenRenderer')
    def test_process_binary_stream_basic(self, mock_renderer_class):
        """Test basic binary stream processing"""
        mock_renderer = Mock()
        mock_renderer_class.return_value = mock_renderer
        mock_renderer.process_command.return_value = True
        mock_renderer.screen = Mock()
        mock_renderer.height = 24
        
        # Create simple test data
        builder = BinaryCommandBuilder()
        builder.screen_setup(40, 20, 1)
        builder.end_of_file()
        data = builder.get_data()
        
        with patch('signal.signal'):
            process_binary_stream(data)
        
        # Verify renderer was initialized and commands processed
        mock_renderer.init_screen.assert_called_once()
        self.assertTrue(mock_renderer.process_command.called)
    
    @patch('renderer.ScreenRenderer')
    def test_process_binary_stream_malformed(self, mock_renderer_class):
        """Test processing malformed binary stream"""
        mock_renderer = Mock()
        mock_renderer_class.return_value = mock_renderer
        mock_renderer.screen = Mock()
        mock_renderer.height = 24
        
        # Malformed data (incomplete command)
        data = bytes([0x1, 5, 80, 24])  # Length says 5 but only 2 data bytes
        
        with patch('signal.signal'):
            process_binary_stream(data)
        
        # Should handle gracefully
        mock_renderer.init_screen.assert_called_once()
        mock_renderer.cleanup.assert_called_once()
    
    @patch('renderer.ScreenRenderer')
    def test_process_binary_stream_keyboard_interrupt(self, mock_renderer_class):
        """Test handling keyboard interrupt"""
        mock_renderer = Mock()
        mock_renderer_class.return_value = mock_renderer
        mock_renderer.init_screen.side_effect = KeyboardInterrupt()
        
        data = bytes([0x1, 3, 40, 20, 1, 0xFF, 0])
        
        with patch('signal.signal'):
            process_binary_stream(data)
        
        mock_renderer.cleanup.assert_called_once()


class TestMainFunction(unittest.TestCase):
    """Test main function and command line interface"""
    
    @patch('sys.argv', ['renderer.py'])
    @patch('sys.stdin')
    @patch('renderer.process_binary_stream')
    def test_main_stdin(self, mock_process, mock_stdin):
        """Test main function reading from stdin"""
        test_data = b'\x01\x03\x50\x18\x01\xFF\x00'
        mock_stdin.buffer.read.return_value = test_data
        
        from renderer import main
        main()
        
        mock_process.assert_called_once_with(test_data)
    
    @patch('sys.argv', ['renderer.py', 'test.bin'])
    @patch('builtins.open', create=True)
    @patch('renderer.process_binary_stream')
    def test_main_file_input(self, mock_process, mock_open):
        """Test main function reading from file"""
        test_data = b'\x01\x03\x50\x18\x01\xFF\x00'
        mock_file = Mock()
        mock_file.read.return_value = test_data
        mock_open.return_value.__enter__.return_value = mock_file
        
        from renderer import main
        main()
        
        mock_open.assert_called_once_with('test.bin', 'rb')
        mock_process.assert_called_once_with(test_data)
    
    @patch('sys.argv', ['renderer.py', 'nonexistent.bin'])
    @patch('builtins.open', side_effect=IOError("File not found"))
    @patch('sys.exit')
    def test_main_file_not_found(self, mock_exit, mock_open):
        """Test main function with non-existent file"""
        from renderer import main
        
        with patch('builtins.print'):
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('sys.argv', ['renderer.py'])
    @patch('sys.stdin')
    @patch('sys.exit')
    def test_main_no_data(self, mock_exit, mock_stdin):
        """Test main function with no input data"""
        mock_stdin.buffer.read.return_value = b''
        
        from renderer import main
        
        with patch('builtins.print'):
            main()
        
        mock_exit.assert_called_once_with(1)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""
    
    def test_full_demo_pipeline(self):
        """Test complete pipeline from demo generation to processing"""
        # Generate demo data
        data = create_demo_1()
        
        # Verify data structure
        self.assertTrue(len(data) > 10)
        self.assertEqual(data[0], 0x1)  # Screen setup
        
        # Parse and verify commands
        i = 0
        command_count = 0
        
        while i < len(data) - 1:
            command = data[i]
            length = data[i + 1]
            
            # Validate command structure
            self.assertLessEqual(i + 2 + length, len(data))
            
            command_count += 1
            i += 2 + length
            
            if command == 0xFF:
                break
        
        self.assertGreater(command_count, 5)  # Should have multiple commands
    
    def test_builder_renderer_compatibility(self):
        """Test that builder output is compatible with renderer"""
        builder = BinaryCommandBuilder()
        builder.screen_setup(20, 10, 1)
        builder.clear_screen()
        builder.render_text(2, 2, 7, "Test")
        builder.draw_character(5, 5, 3, ord('*'))
        builder.draw_line(0, 0, 10, 5, 2, ord('-'))
        builder.cursor_movement(8, 8)
        builder.draw_at_cursor(ord('X'), 4)
        builder.end_of_file()
        
        data = builder.get_data()
        
        # Create renderer and process commands
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        
        i = 0
        processed_commands = 0
        
        while i < len(data) - 1:
            command = data[i]
            length = data[i + 1]
            command_data = list(data[i + 2:i + 2 + length])
            
            result = renderer.process_command(command, length, command_data)
            
            if command == 0xFF:
                self.assertFalse(result)  # Should stop at EOF
                break
            else:
                processed_commands += 1
            
            i += 2 + length
        
        self.assertGreater(processed_commands, 5)
        self.assertTrue(renderer.initialized)


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestBinaryCommandBuilder,
        TestScreenRenderer,
        TestDemoGeneration,
        TestBinaryStreamProcessing,
        TestMainFunction,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)