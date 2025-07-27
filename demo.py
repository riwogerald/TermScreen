#!/usr/bin/env python3
"""
Demo script that generates sample binary data to test the renderer
"""

import struct
import sys
from typing import List

class BinaryCommandBuilder:
    """Helper class to build binary command streams"""
    
    def __init__(self):
        self.data = bytearray()
    
    def add_command(self, command: int, data: List[int]):
        """Add a command with data to the stream"""
        # Validate that all data values are valid bytes (0-255)
        for value in data:
            if not isinstance(value, int) or value < 0 or value > 255:
                raise ValueError(f"Data value {value} must be an integer between 0 and 255")
        
        self.data.append(command)
        self.data.append(len(data))
        self.data.extend(data)
    
    def screen_setup(self, width: int, height: int, color_mode: int):
        """Add screen setup command"""
        self.add_command(0x1, [width, height, color_mode])
    
    def draw_character(self, x: int, y: int, color: int, char: int):
        """Add draw character command"""
        self.add_command(0x2, [x, y, color, char])
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: int, char: int):
        """Add draw line command"""
        self.add_command(0x3, [x1, y1, x2, y2, color, char])
    
    def render_text(self, x: int, y: int, color: int, text: str):
        """Add render text command"""
        text_bytes = text.encode('ascii', errors='replace')
        data = [x, y, color] + list(text_bytes)
        self.add_command(0x4, data)
    
    def cursor_movement(self, x: int, y: int):
        """Add cursor movement command"""
        self.add_command(0x5, [x, y])
    
    def draw_at_cursor(self, char: int, color: int):
        """Add draw at cursor command"""
        self.add_command(0x6, [char, color])
    
    def clear_screen(self):
        """Add clear screen command"""
        self.add_command(0x7, [])
    
    def end_of_file(self):
        """Add end of file command"""
        self.add_command(0xFF, [])
    
    def get_data(self) -> bytes:
        """Get the complete binary data"""
        return bytes(self.data)


def create_demo_1() -> bytes:
    """Create a simple demo with text and shapes"""
    builder = BinaryCommandBuilder()
    
    # Setup screen
    builder.screen_setup(80, 24, 2)  # 80x24, 256 colors
    
    # Clear screen
    builder.clear_screen()
    
    # Draw title
    builder.render_text(25, 2, 14, "Terminal Screen Renderer Demo")
    builder.render_text(30, 3, 8, "Press any key to exit")
    
    # Draw a box
    builder.draw_line(10, 5, 70, 5, 12, ord('-'))   # Top
    builder.draw_line(10, 15, 70, 15, 12, ord('-'))  # Bottom
    builder.draw_line(10, 5, 10, 15, 12, ord('|'))   # Left
    builder.draw_line(70, 5, 70, 15, 12, ord('|'))   # Right
    
    # Draw corners
    builder.draw_character(10, 5, 12, ord('+'))
    builder.draw_character(70, 5, 12, ord('+'))
    builder.draw_character(10, 15, 12, ord('+'))
    builder.draw_character(70, 15, 12, ord('+'))
    
    # Add some content inside the box
    builder.render_text(15, 7, 10, "This is a demonstration of the binary")
    builder.render_text(15, 8, 10, "command protocol for terminal rendering.")
    builder.render_text(15, 10, 11, "Features demonstrated:")
    builder.render_text(17, 11, 7, "- Text rendering with colors")
    builder.render_text(17, 12, 7, "- Line drawing")
    builder.render_text(17, 13, 7, "- Character placement")
    
    # Draw a diagonal line
    builder.draw_line(15, 17, 65, 21, 13, ord('*'))
    
    # Add some scattered characters
    for i in range(5):
        builder.draw_character(20 + i * 8, 19, 9 + i, ord('o'))
    
    builder.end_of_file()
    return builder.get_data()


def create_demo_2() -> bytes:
    """Create a more complex demo with animations"""
    builder = BinaryCommandBuilder()
    
    # Setup screen
    builder.screen_setup(60, 20, 2)
    builder.clear_screen()
    
    # Title
    builder.render_text(20, 1, 14, "Pattern Demo")
    
    # Create a checkerboard pattern
    for y in range(5, 15):
        for x in range(10, 50):
            if (x + y) % 2 == 0:
                color = 8
                char = ord('#')
            else:
                color = 15
                char = ord('.')
            builder.draw_character(x, y, color, char)
    
    # Draw border around pattern
    builder.draw_line(9, 4, 50, 4, 12, ord('='))
    builder.draw_line(9, 15, 50, 15, 12, ord('='))
    builder.draw_line(9, 4, 9, 15, 12, ord('|'))
    builder.draw_line(50, 4, 50, 15, 12, ord('|'))
    
    # Corners
    builder.draw_character(9, 4, 12, ord('+'))
    builder.draw_character(50, 4, 12, ord('+'))
    builder.draw_character(9, 15, 12, ord('+'))
    builder.draw_character(50, 15, 12, ord('+'))
    
    # Status line
    builder.render_text(15, 17, 11, "Checkerboard pattern complete")
    
    builder.end_of_file()
    return builder.get_data()


def main():
    """Generate demo data and output to stdout or file"""
    if len(sys.argv) > 1:
        demo_type = sys.argv[1]
    else:
        demo_type = "1"
    
    if demo_type == "1":
        data = create_demo_1()
    elif demo_type == "2":
        data = create_demo_2()
    else:
        print("Usage: python demo.py [1|2]", file=sys.stderr)
        sys.exit(1)
    
    # Output binary data
    sys.stdout.buffer.write(data)


if __name__ == "__main__":
    main()