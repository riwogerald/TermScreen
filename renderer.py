#!/usr/bin/env python3
"""
Enhanced Terminal Screen Renderer
Processes binary command streams to render graphics in terminal
"""

import curses
import sys
import os
from typing import List, Optional, Tuple
import signal
import traceback

class ScreenRenderer:
    """Main renderer class that handles binary command processing"""
    
    def __init__(self):
        self.screen = None
        self.width = 0
        self.height = 0
        self.color_mode = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.initialized = False
        self.color_pairs_initialized = False
        
    def init_screen(self):
        """Initialize the curses screen with proper error handling"""
        try:
            self.screen = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(True)
            curses.curs_set(0)  # Hide cursor
            
            # Initialize color pairs based on terminal capabilities
            if curses.has_colors():
                self._init_color_pairs()
                
        except Exception as e:
            self.cleanup()
            raise RuntimeError(f"Failed to initialize screen: {e}")
    
    def _init_color_pairs(self):
        """Initialize color pairs based on terminal capabilities"""
        try:
            max_colors = min(curses.COLORS, 256)
            max_pairs = min(curses.COLOR_PAIRS - 1, 255)
            
            for i in range(1, min(max_colors, max_pairs + 1)):
                try:
                    curses.init_pair(i, i % max_colors, -1)
                except curses.error:
                    # Some terminals don't support all color combinations
                    pass
                    
            self.color_pairs_initialized = True
        except Exception:
            # Fallback to basic colors if advanced color initialization fails
            for i in range(1, 8):
                try:
                    curses.init_pair(i, i, -1)
                except curses.error:
                    pass
    
    def cleanup(self):
        """Clean up curses resources"""
        if self.screen:
            try:
                self.screen.keypad(False)
                curses.echo()
                curses.nocbreak()
                curses.curs_set(1)  # Show cursor
                curses.endwin()
            except:
                pass
    
    def _safe_addch(self, y: int, x: int, char: int, attr: int = 0):
        """Safely add character with bounds checking"""
        try:
            if 0 <= y < self.height and 0 <= x < self.width:
                self.screen.addch(y, x, char, attr)
        except curses.error:
            # Ignore errors from drawing at invalid positions
            pass
    
    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0):
        """Safely add string with bounds checking"""
        try:
            if 0 <= y < self.height and 0 <= x < self.width:
                # Truncate text if it would exceed screen width
                max_len = self.width - x
                if len(text) > max_len:
                    text = text[:max_len]
                self.screen.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    def _get_color_attr(self, color: int) -> int:
        """Get color attribute, with fallback for unsupported colors"""
        if not self.color_pairs_initialized or color == 0:
            return 0
        
        # Clamp color to available range
        max_color = min(curses.COLOR_PAIRS - 1, 255)
        color = max(1, min(color, max_color))
        
        try:
            return curses.color_pair(color)
        except:
            return 0
    
    def process_command(self, command: int, length: int, data: List[int]) -> bool:
        """Process a single command from the binary stream"""
        # Only allow screen setup before initialization
        if command != 0x1 and not self.initialized:
            return True
        
        try:
            if command == 0x1:  # Screen setup
                return self._cmd_screen_setup(data)
            elif command == 0x2:  # Draw character
                return self._cmd_draw_character(data)
            elif command == 0x3:  # Draw line
                return self._cmd_draw_line(data)
            elif command == 0x4:  # Render text
                return self._cmd_render_text(data)
            elif command == 0x5:  # Cursor movement
                return self._cmd_cursor_movement(data)
            elif command == 0x6:  # Draw at cursor
                return self._cmd_draw_at_cursor(data)
            elif command == 0x7:  # Clear screen
                return self._cmd_clear_screen(data)
            elif command == 0xFF:  # End of file
                return False
            else:
                # Unknown command, continue processing
                return True
                
        except Exception as e:
            # Log error but continue processing
            return True
    
    def _cmd_screen_setup(self, data: List[int]) -> bool:
        """Handle screen setup command"""
        if len(data) < 3:
            return True
            
        self.width = data[0]
        self.height = data[1]
        self.color_mode = data[2]
        
        # Validate dimensions
        if self.width <= 0 or self.height <= 0:
            return True
            
        try:
            # Resize screen if possible
            if hasattr(self.screen, 'resize'):
                self.screen.resize(self.height, self.width)
        except:
            pass
            
        self.initialized = True
        self.screen.refresh()
        return True
    
    def _cmd_draw_character(self, data: List[int]) -> bool:
        """Handle draw character command"""
        if len(data) < 4:
            return True
            
        x, y, color, char = data[:4]
        attr = self._get_color_attr(color)
        self._safe_addch(y, x, char, attr)
        self.screen.refresh()
        return True
    
    def _cmd_draw_line(self, data: List[int]) -> bool:
        """Handle draw line command"""
        if len(data) < 6:
            return True
            
        x1, y1, x2, y2, color, char = data[:6]
        attr = self._get_color_attr(color)
        self._draw_line(x1, y1, x2, y2, char, attr)
        self.screen.refresh()
        return True
    
    def _cmd_render_text(self, data: List[int]) -> bool:
        """Handle render text command"""
        if len(data) < 3:
            return True
            
        x, y, color = data[:3]
        try:
            text = bytes(data[3:]).decode('ascii', errors='replace')
            attr = self._get_color_attr(color)
            self._safe_addstr(y, x, text, attr)
            self.screen.refresh()
        except:
            pass
        return True
    
    def _cmd_cursor_movement(self, data: List[int]) -> bool:
        """Handle cursor movement command"""
        if len(data) < 2:
            return True
            
        self.cursor_x, self.cursor_y = data[:2]
        # Clamp cursor to screen bounds
        self.cursor_x = max(0, min(self.cursor_x, self.width - 1))
        self.cursor_y = max(0, min(self.cursor_y, self.height - 1))
        
        try:
            self.screen.move(self.cursor_y, self.cursor_x)
        except:
            pass
        return True
    
    def _cmd_draw_at_cursor(self, data: List[int]) -> bool:
        """Handle draw at cursor command"""
        if len(data) < 2:
            return True
            
        char, color = data[:2]
        attr = self._get_color_attr(color)
        self._safe_addch(self.cursor_y, self.cursor_x, char, attr)
        self.screen.refresh()
        return True
    
    def _cmd_clear_screen(self, data: List[int]) -> bool:
        """Handle clear screen command"""
        try:
            self.screen.clear()
            self.screen.refresh()
        except:
            pass
        return True
    
    def _draw_line(self, x1: int, y1: int, x2: int, y2: int, char: int, attr: int):
        """Draw line using Bresenham's algorithm"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx // 2
            while x != x2:
                self._safe_addch(y, x, char, attr)
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy // 2
            while y != y2:
                self._safe_addch(y, x, char, attr)
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        
        self._safe_addch(y, x, char, attr)


def process_binary_stream(data: bytes) -> None:
    """Process binary stream and render to screen"""
    renderer = ScreenRenderer()
    
    def signal_handler(signum, frame):
        renderer.cleanup()
        sys.exit(0)
    
    # Set up signal handlers for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        renderer.init_screen()
        i = 0
        
        while i < len(data):
            if i + 1 >= len(data):
                break
                
            command = data[i]
            length = data[i + 1]
            
            # Validate length to prevent buffer overflow
            if i + 2 + length > len(data):
                break
                
            command_data = list(data[i + 2:i + 2 + length])
            i += 2 + length
            
            if not renderer.process_command(command, length, command_data):
                break
        
        # Wait for user input before exiting
        renderer.screen.addstr(renderer.height - 1, 0, "Press any key to exit...")
        renderer.screen.refresh()
        renderer.screen.getch()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        renderer.cleanup()
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
    finally:
        renderer.cleanup()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Read from file
        try:
            with open(sys.argv[1], 'rb') as f:
                binary_data = f.read()
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            binary_data = sys.stdin.buffer.read()
        except KeyboardInterrupt:
            sys.exit(0)
    
    if not binary_data:
        print("No data provided", file=sys.stderr)
        sys.exit(1)
    
    process_binary_stream(binary_data)


if __name__ == "__main__":
    main()