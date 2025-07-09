# Terminal Screen Renderer

A robust terminal screen renderer that processes binary command streams to display graphics, text, and interactive content in terminal windows.

## Original Problem Statement

Imagine a stream of bytes supplied to a program to render them in a screen inside a terminal. Below is the definition of the binary format used for communication between a computer and the screen:

+--------------+-------------+-------------+-------------+--- ··· ---+----------------+
| Command Byte | Length Byte | Data Byte 0 | Data Byte 1 |    ···    |  Data Byte n-1 |
+--------------+-------------+-------------+-------------+--- ··· ---+----------------+

The data format is an array of bytes, containing sections of above form, in succession. Each section begins with a command byte, specifying the type of operation to be performed on the screen, followed by a length byte, and then a sequence of data bytes, which function as arguments to the command, as specified below:
- **0x1 - Screen setup: Defines the dimensions and colour setting of the screen. The screen must be set up before any other command is sent. Commands are ignored         if the screen hasn't been set up.
      Data format:
      Byte 0: Screen Width (in characters)
      Byte 1: Screen Height (in characters)
      Byte 2: Color Mode (0x00 for monochrome, 0x01 for 16 colors, 0x02 for 256 colors)
- **0x2 - Draw character: Places a character at a given coordinate of the screen.
      Data format:
      Byte 0: x coordinate
      Byte 1: y coordinate
      Byte 2: Color index
      Byte 3: Character to display (ASCII)
- **0x3 - Draw line: Draws a line from one coordinate of the screen to another.
      Data format:
      Byte 0: x1 (starting coordinate)
      Byte 1: y1 (starting coordinate)
      Byte 2: x2 (ending coordinate) Byte 4: y2 (ending coordinate)
      Byte 4: Color index
      Byte 5: Character to use (ASCII)
- **0x4 - Render text: Renders a string starting from a specific position.
      Data format:
      Byte 0: x coordinate
      Byte 1: y coordinate
      Byte 2: Color index
      Byte 3-n: Text data (ASCII characters)
- **0x5 - Cursor movement: Moves cursor to a specific location without drawing on the screen.
      Data format:
      Byte 0: x coordinate
      Byte 1: y coordinate
- **0x6 - Draw at cursor: Draws a character at the cursor location.
      Data format:
      Byte 0: Character to draw (ASCII)
      Byte 1: Color index
- **0x7 - Clear screen:
      Data format: No additional data.
- **0xFF - End of file: Marks the end of binary stream.
      Data format: No additional data.

The program should draw the screen from within a terminal window, but the question of whether to do so inside the terminal from which it is launched or to launch a separate terminal window is left to the implementer.

## Features

- **Binary Command Protocol**: Processes structured binary commands for screen operations
- **Full Color Support**: Supports monochrome, 16-color, and 256-color modes
- **Graphics Primitives**: Character drawing, line drawing, and text rendering
- **Cursor Management**: Precise cursor positioning and drawing
- **Error Handling**: Robust error handling and graceful degradation
- **Cross-Platform**: Works on Unix-like systems with curses support

## Binary Protocol

The renderer accepts a stream of binary commands with the following format:

```
+----------+----------+----------+----------+--- ··· ---+----------+
| Command  | Length   | Data 0   | Data 1   |    ···    | Data n-1 |
+----------+----------+----------+----------+--- ··· ---+----------+
```

### Supported Commands

| Command | Description | Data Format |
|---------|-------------|-------------|
| `0x1` | Screen Setup | `[width, height, color_mode]` |
| `0x2` | Draw Character | `[x, y, color, char]` |
| `0x3` | Draw Line | `[x1, y1, x2, y2, color, char]` |
| `0x4` | Render Text | `[x, y, color, ...text_bytes]` |
| `0x5` | Cursor Movement | `[x, y]` |
| `0x6` | Draw at Cursor | `[char, color]` |
| `0x7` | Clear Screen | `[]` |
| `0xFF` | End of File | `[]` |

### Color Modes

- `0x00`: Monochrome
- `0x01`: 16 colors
- `0x02`: 256 colors

## Usage

### Basic Usage

```bash
# Read from stdin
python renderer.py < input.bin

# Read from file
python renderer.py input.bin
```

### Running Demos

```bash
# Generate and display demo 1
python demo.py 1 | python renderer.py

# Generate and display demo 2
python demo.py 2 | python renderer.py

# Save demo to file
python demo.py 1 > demo1.bin
python renderer.py demo1.bin
```

### Running Tests

```bash
python test_renderer.py
```

## Programming Interface

### BinaryCommandBuilder

Use the `BinaryCommandBuilder` class to programmatically create binary command streams:

```python
from demo import BinaryCommandBuilder

builder = BinaryCommandBuilder()

# Setup screen
builder.screen_setup(80, 24, 2)  # 80x24, 256 colors

# Clear and draw
builder.clear_screen()
builder.render_text(10, 5, 14, "Hello, World!")
builder.draw_line(0, 0, 79, 23, 12, ord('*'))

# Get binary data
data = builder.get_data()
```

### Direct Rendering

```python
from renderer import process_binary_stream

# Process binary data directly
process_binary_stream(binary_data)
```

## Examples

### Simple Text Display

```python
builder = BinaryCommandBuilder()
builder.screen_setup(40, 10, 1)
builder.clear_screen()
builder.render_text(5, 3, 7, "Hello Terminal!")
builder.end_of_file()

data = builder.get_data()
# Process with: process_binary_stream(data)
```

### Drawing Shapes

```python
builder = BinaryCommandBuilder()
builder.screen_setup(60, 20, 2)

# Draw a box
builder.draw_line(10, 5, 50, 5, 12, ord('-'))   # Top
builder.draw_line(10, 15, 50, 15, 12, ord('-'))  # Bottom
builder.draw_line(10, 5, 10, 15, 12, ord('|'))   # Left
builder.draw_line(50, 5, 50, 15, 12, ord('|'))   # Right

# Add corners
builder.draw_character(10, 5, 12, ord('+'))
builder.draw_character(50, 5, 12, ord('+'))
builder.draw_character(10, 15, 12, ord('+'))
builder.draw_character(50, 15, 12, ord('+'))

builder.end_of_file()
```

## Requirements

- Python 3.6+
- Unix-like system with curses support
- Terminal with color support (recommended)

## Error Handling

The renderer includes comprehensive error handling:

- **Bounds Checking**: All drawing operations are bounds-checked
- **Color Fallback**: Graceful degradation for unsupported colors
- **Signal Handling**: Clean exit on Ctrl+C
- **Malformed Data**: Continues processing despite invalid commands

## Performance

- **Efficient Rendering**: Optimized curses usage with minimal screen updates
- **Memory Safe**: Bounds checking prevents buffer overflows
- **Responsive**: Immediate visual feedback for all operations

## Limitations

- Requires terminal with curses support
- Color support depends on terminal capabilities
- Screen size limited by terminal dimensions
- ASCII text only (can be extended for Unicode)

## Contributing

1. Run tests: `python test_renderer.py`
2. Test with demos: `python demo.py 1 | python renderer.py`
3. Ensure cross-platform compatibility
4. Add tests for new features

## License

MIT License - see LICENSE file for details.
