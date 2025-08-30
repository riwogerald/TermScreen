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


class TestFullIntegration(unittest.TestCase):
    """Full integration tests combining all components"""
    
    def test_demo_to_renderer_pipeline(self):
        """Test complete pipeline from demo generation to screen rendering"""
        # Generate demo data
        demo_data = create_demo_1()
        
        # Process with renderer
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        
        # Mock the init to avoid curses dependency
        with patch.object(renderer, 'init_screen'):
            # Parse and process all commands
            i = 0
            commands_processed = []
            
            while i < len(demo_data) - 1:
                if i + 1 >= len(demo_data):
                    break
                    
                command = demo_data[i]
                length = demo_data[i + 1]
                
                if i + 2 + length > len(demo_data):
                    break
                    
                command_data = list(demo_data[i + 2:i + 2 + length])
                result = renderer.process_command(command, length, command_data)
                commands_processed.append(command)
                
                if not result:  # EOF
                    break
                    
                i += 2 + length
        
        # Verify we processed multiple commands including setup and EOF
        self.assertIn(0x1, commands_processed)  # Screen setup
        self.assertIn(0xFF, commands_processed)  # EOF
        self.assertGreater(len(commands_processed), 5)
        self.assertTrue(renderer.initialized)
    
    def test_file_io_integration(self):
        """Test file input/output integration"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # Write demo data to temporary file
            demo_data = create_demo_2()
            tmp.write(demo_data)
            tmp.flush()
            
            # Test reading from file
            with patch('renderer.process_binary_stream') as mock_process:
                with patch('sys.argv', ['renderer.py', tmp.name]):
                    main()
                
                mock_process.assert_called_once()
                # Verify the data passed matches what we wrote
                called_data = mock_process.call_args[0][0]
                self.assertEqual(called_data, demo_data)
        
        # Clean up
        os.unlink(tmp.name)
    
    def test_demo_main_function(self):
        """Test demo main function with different parameters"""
        # Test demo 1
        with patch('sys.argv', ['demo.py', '1']), \
             patch('sys.stdout') as mock_stdout:
            
            mock_buffer = Mock()
            mock_stdout.buffer = mock_buffer
            
            demo_main()
            
            # Should have written binary data
            self.assertTrue(mock_buffer.write.called)
            written_data = mock_buffer.write.call_args[0][0]
            self.assertIsInstance(written_data, bytes)
            self.assertGreater(len(written_data), 0)
        
        # Test demo 2
        with patch('sys.argv', ['demo.py', '2']), \
             patch('sys.stdout') as mock_stdout:
            
            mock_buffer = Mock()
            mock_stdout.buffer = mock_buffer
            
            demo_main()
            
            self.assertTrue(mock_buffer.write.called)


def run_integration_tests():
    """Run integration tests"""
    test_classes = [
        TestFullIntegration
    ]
    
    return run_test_suite_with_summary(test_classes, "Integration Tests")


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
