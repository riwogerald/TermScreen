import curses
import sys
from typing import List, Optional

class ScreenRenderer:
    def __init__(self):
        self.screen = None
        self.width = 0
        self.height = 0
        self.color_mode = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.initialized = False

    def init_screen(self):
        self.screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        # Initialize color pairs
        for i in range(1, 256):
            curses.init_pair(i, i, -1)
        self.screen.keypad(1)
        curses.noecho()
        curses.cbreak()

    def cleanup(self):
        if self.screen:
            self.screen.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def process_command(self, command: int, length: int, data: List[int]) -> bool:
        if command != 0x1 and not self.initialized:
            return True

        if command == 0x1:  # Screen setup
            self.width = data[0]
            self.height = data[1]
            self.color_mode = data[2]
            self.initialized = True
            self.screen.resize(self.height, self.width)

        elif command == 0x2:  # Draw character
            x, y, color, char = data
            self.screen.addch(y, x, char, curses.color_pair(color))

        elif command == 0x3:  # Draw line
            x1, y1, x2, y2, color, char = data
            self.draw_line(x1, y1, x2, y2, color, char)

        elif command == 0x4:  # Render text
            x, y, color = data[0:3]
            text = bytes(data[3:]).decode('ascii')
            self.screen.addstr(y, x, text, curses.color_pair(color))

        elif command == 0x5:  # Cursor movement
            self.cursor_x, self.cursor_y = data
            self.screen.move(self.cursor_y, self.cursor_x)

        elif command == 0x6:  # Draw at cursor
            char, color = data
            self.screen.addch(self.cursor_y, self.cursor_x, char, 
                            curses.color_pair(color))

        elif command == 0x7:  # Clear screen
            self.screen.clear()

        elif command == 0xFF:  # End of file
            return False

        self.screen.refresh()
        return True

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                  color: int, char: int):
        # Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        if dx > dy:
            err = dx / 2.0
            while x != x2:
                self.screen.addch(y, x, char, curses.color_pair(color))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                self.screen.addch(y, x, char, curses.color_pair(color))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        self.screen.addch(y, x, char, curses.color_pair(color))

def process_binary_stream(data: bytes) -> None:
    renderer = ScreenRenderer()
    try:
        renderer.init_screen()
        i = 0
        while i < len(data):
            command = data[i]
            length = data[i + 1]
            command_data = list(data[i + 2:i + 2 + length])
            i += 2 + length

            if not renderer.process_command(command, length, command_data):
                break

        renderer.screen.getch()  # Wait for key press
    finally:
        renderer.cleanup()

def main():
    # Read binary data from stdin
    binary_data = sys.stdin.buffer.read()
    process_binary_stream(binary_data)

if __name__ == "__main__":
    main()