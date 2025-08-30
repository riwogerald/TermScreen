#!/usr/bin/env python3
"""
Advanced showcase demos for Terminal Screen Renderer
Demonstrates sophisticated usage patterns and impressive visual effects
"""

import math
import sys
from demo import BinaryCommandBuilder


def create_animated_sine_wave() -> bytes:
    """Create an animated sine wave demo - great for portfolios!"""
    builder = BinaryCommandBuilder()
    
    # Setup large screen for better effect
    width, height = 120, 30
    builder.screen_setup(width, height, 2)  # 256 colors
    builder.clear_screen()
    
    # Title
    builder.render_text(35, 1, 14, "ANIMATED SINE WAVE VISUALIZATION")
    builder.render_text(45, 2, 8, "Mathematical Beauty in Terminal")
    
    # Draw coordinate axes
    mid_y = height // 2
    
    # X-axis
    builder.draw_line(10, mid_y, width - 10, mid_y, 7, ord('-'))
    builder.render_text(width - 8, mid_y, 7, "X")
    
    # Y-axis  
    builder.draw_line(15, 5, 15, height - 5, 7, ord('|'))
    builder.render_text(15, 4, 7, "Y")
    
    # Draw sine wave with multiple frequencies and colors
    for phase in range(0, 360, 10):  # Multiple phases for animation effect
        color = 9 + (phase // 30) % 6  # Cycle through colors
        
        for x in range(16, width - 10):
            # Calculate sine wave
            angle = (x - 16) * 0.1 + math.radians(phase)
            y_offset = int(8 * math.sin(angle))
            y_pos = mid_y + y_offset
            
            if 5 <= y_pos < height - 5:
                char = '*' if phase % 60 < 30 else 'o'  # Alternate characters
                builder.draw_character(x, y_pos, color, ord(char))
    
    # Add mathematical formula
    builder.render_text(20, height - 4, 11, "f(x) = sin(x) with multiple frequencies")
    builder.render_text(20, height - 3, 11, "Demonstrates: Math visualization, color cycling, character variation")
    
    builder.end_of_file()
    return builder.get_data()


def create_mandelbrot_set() -> bytes:
    """Create a Mandelbrot set visualization - shows algorithmic complexity"""
    builder = BinaryCommandBuilder()
    
    width, height = 80, 24
    builder.screen_setup(width, height, 2)
    builder.clear_screen()
    
    # Title
    builder.render_text(25, 1, 14, "MANDELBROT SET VISUALIZATION")
    builder.render_text(30, 2, 8, "Complex Mathematics in ASCII")
    
    # Mandelbrot parameters
    x_min, x_max = -2.5, 1.0
    y_min, y_max = -1.0, 1.0
    max_iter = 50
    
    # Character set for different iteration counts
    chars = " .:-=+*#%@"
    
    for py in range(4, height - 2):
        for px in range(5, width - 5):
            # Map pixel to complex plane
            x = x_min + (px - 5) * (x_max - x_min) / (width - 10)
            y = y_min + (py - 4) * (y_max - y_min) / (height - 6)
            
            # Mandelbrot iteration
            c = complex(x, y)
            z = 0
            iter_count = 0
            
            while abs(z) <= 2 and iter_count < max_iter:
                z = z * z + c
                iter_count += 1
            
            # Choose character and color based on iteration count
            if iter_count == max_iter:
                char = ord('#')  # Inside set
                color = 1
            else:
                char_idx = min(iter_count // 5, len(chars) - 1)
                char = ord(chars[char_idx])
                color = 8 + (iter_count % 8)  # Color gradient
            
            builder.draw_character(px, py, color, char)
    
    # Add description
    builder.render_text(5, height - 1, 11, "Mandelbrot Set: z = z² + c | Demonstrates: Complex algorithms, visual mapping")
    
    builder.end_of_file()
    return builder.get_data()


def create_game_of_life() -> bytes:
    """Conway's Game of Life - shows cellular automaton simulation"""
    builder = BinaryCommandBuilder()
    
    width, height = 60, 20
    builder.screen_setup(width, height, 2)
    builder.clear_screen()
    
    # Title
    builder.render_text(15, 1, 14, "CONWAY'S GAME OF LIFE")
    builder.render_text(20, 2, 8, "Cellular Automaton Demo")
    
    # Initialize with a glider pattern and some random cells
    grid_width, grid_height = 50, 15
    grid = [[False for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Add glider pattern
    glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
    for x, y in glider:
        if 0 <= x < grid_width and 0 <= y < grid_height:
            grid[y][x] = True
    
    # Add oscillator
    oscillator = [(10, 5), (11, 5), (12, 5)]
    for x, y in oscillator:
        if 0 <= x < grid_width and 0 <= y < grid_height:
            grid[y][x] = True
    
    # Add block (still life)
    block = [(20, 8), (21, 8), (20, 9), (21, 9)]
    for x, y in block:
        if 0 <= x < grid_width and 0 <= y < grid_height:
            grid[y][x] = True
    
    # Simulate several generations
    for generation in range(8):
        # Draw current state
        for y in range(grid_height):
            for x in range(grid_width):
                screen_x = x + 5
                screen_y = y + 4
                
                if grid[y][x]:
                    # Living cell - use different colors for age effect
                    color = 10 + (generation % 6)
                    builder.draw_character(screen_x, screen_y, color, ord('█'))
                else:
                    # Dead cell
                    builder.draw_character(screen_x, screen_y, 8, ord('·'))
        
        # Calculate next generation
        new_grid = [[False for _ in range(grid_width)] for _ in range(grid_height)]
        
        for y in range(grid_height):
            for x in range(grid_width):
                # Count live neighbors
                neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < grid_width and 0 <= ny < grid_height:
                            if grid[ny][nx]:
                                neighbors += 1
                
                # Apply Game of Life rules
                if grid[y][x]:  # Living cell
                    new_grid[y][x] = neighbors in [2, 3]
                else:  # Dead cell
                    new_grid[y][x] = neighbors == 3
        
        grid = new_grid
    
    # Add explanation
    builder.render_text(5, height - 1, 11, "Rules: Live cell survives with 2-3 neighbors, dead cell born with 3")
    
    builder.end_of_file()
    return builder.get_data()


def create_data_visualization_demo() -> bytes:
    """Create a data visualization demo with charts and graphs"""
    builder = BinaryCommandBuilder()
    
    width, height = 100, 30
    builder.screen_setup(width, height, 2)
    builder.clear_screen()
    
    # Title
    builder.render_text(35, 1, 14, "TERMINAL DATA VISUALIZATION SUITE")
    builder.render_text(40, 2, 8, "Professional Charts & Graphs")
    
    # Sample data (simulating business metrics)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    revenue = [45, 52, 48, 67, 71, 63]  # in thousands
    costs = [32, 35, 31, 41, 43, 39]
    
    # Draw bar chart
    chart_start_x, chart_start_y = 10, 6
    chart_width, chart_height = 40, 15
    
    # Chart title and axes
    builder.render_text(chart_start_x + 10, 4, 12, "REVENUE vs COSTS (Bar Chart)")
    
    # Y-axis labels
    for i in range(0, chart_height, 3):
        value = int(80 - (i * 80 / chart_height))
        builder.render_text(chart_start_x - 3, chart_start_y + i, 7, f"{value:2d}k")
    
    # Draw bars
    bar_width = 3
    for i, (month, rev, cost) in enumerate(zip(months, revenue, costs)):
        x_pos = chart_start_x + i * 6
        
        # Revenue bar (taller, blue-ish)
        rev_height = int((rev / 80.0) * chart_height)
        for h in range(rev_height):
            for w in range(bar_width):
                builder.draw_character(x_pos + w, chart_start_y + chart_height - h - 1, 12, ord('█'))
        
        # Cost bar (shorter, red-ish, offset)
        cost_height = int((cost / 80.0) * chart_height)
        for h in range(cost_height):
            for w in range(bar_width):
                builder.draw_character(x_pos + bar_width + 1 + w, chart_start_y + chart_height - h - 1, 9, ord('█'))
        
        # Month label
        builder.render_text(x_pos + 1, chart_start_y + chart_height + 1, 7, month)
    
    # Legend
    builder.render_text(chart_start_x, chart_start_y + chart_height + 3, 12, "█ Revenue")
    builder.render_text(chart_start_x + 15, chart_start_y + chart_height + 3, 9, "█ Costs")
    
    # Draw line graph on the right
    line_start_x, line_start_y = 60, 6
    line_width, line_height = 35, 15
    
    builder.render_text(line_start_x + 5, 4, 12, "PROFIT TREND (Line Chart)")
    
    # Calculate and draw profit trend
    profits = [r - c for r, c in zip(revenue, costs)]
    max_profit = max(profits)
    
    prev_x, prev_y = None, None
    for i, profit in enumerate(profits):
        x = line_start_x + int((i / len(profits)) * line_width)
        y = line_start_y + line_height - int((profit / max_profit) * line_height)
        
        # Draw point
        builder.draw_character(x, y, 14, ord('●'))
        
        # Draw line to previous point
        if prev_x is not None:
            builder.draw_line(prev_x, prev_y, x, y, 10, ord('─'))
        
        prev_x, prev_y = x, y
    
    # Add data insights
    builder.render_text(10, height - 5, 11, "Key Insights:")
    builder.render_text(10, height - 4, 7, f"• Peak revenue: ${max(revenue)}k in {months[revenue.index(max(revenue))]}")
    builder.render_text(10, height - 3, 7, f"• Highest profit: ${max(profits)}k")
    builder.render_text(10, height - 2, 7, f"• Average monthly growth: {((profits[-1] - profits[0]) / len(profits)):.1f}k")
    builder.render_text(10, height - 1, 11, "Demonstrates: Business intelligence, data visualization, trend analysis")
    
    builder.end_of_file()
    return builder.get_data()


def create_ascii_art_showcase() -> bytes:
    """Create an ASCII art showcase with various techniques"""
    builder = BinaryCommandBuilder()
    
    width, height = 90, 25
    builder.screen_setup(width, height, 2)
    builder.clear_screen()
    
    # Title
    builder.render_text(30, 1, 14, "ASCII ART SHOWCASE")
    builder.render_text(25, 2, 8, "Demonstrating Artistic Terminal Graphics")
    
    # Create a computer/terminal icon
    icon_x, icon_y = 10, 5
    
    # Monitor frame
    builder.draw_line(icon_x, icon_y, icon_x + 15, icon_y, 7, ord('─'))  # top
    builder.draw_line(icon_x, icon_y + 8, icon_x + 15, icon_y + 8, 7, ord('─'))  # bottom
    builder.draw_line(icon_x, icon_y, icon_x, icon_y + 8, 7, ord('│'))  # left
    builder.draw_line(icon_x + 15, icon_y, icon_x + 15, icon_y + 8, 7, ord('│'))  # right
    
    # Screen content (code)
    builder.render_text(icon_x + 2, icon_y + 2, 10, "def render():")
    builder.render_text(icon_x + 3, icon_y + 3, 10, "screen.draw()")
    builder.render_text(icon_x + 3, icon_y + 4, 10, "return True")
    builder.render_text(icon_x + 2, icon_y + 5, 11, "# Terminal")
    builder.render_text(icon_x + 2, icon_y + 6, 11, "# Graphics!")
    
    # Monitor stand
    builder.draw_line(icon_x + 6, icon_y + 9, icon_x + 9, icon_y + 9, 7, ord('─'))
    builder.draw_character(icon_x + 7, icon_y + 10, 7, ord('│'))
    builder.draw_line(icon_x + 5, icon_y + 11, icon_x + 10, icon_y + 11, 7, ord('─'))
    
    # Draw a geometric pattern
    pattern_x, pattern_y = 35, 6
    
    # Diamond pattern
    for i in range(7):
        for j in range(7):
            if (i + j) % 2 == 0:
                color = 12 if (i * j) % 3 == 0 else 13
                char = '◆' if i == j else '◇'
                builder.draw_character(pattern_x + j, pattern_y + i, color, ord(char))
    
    # Create a progress bar visualization
    progress_x, progress_y = 55, 8
    builder.render_text(progress_x, progress_y - 1, 11, "Progress Bars:")
    
    progress_values = [25, 67, 90, 45, 100]
    progress_labels = ["CPU", "RAM", "GPU", "SSD", "NET"]
    
    for i, (value, label) in enumerate(zip(progress_values, progress_labels)):
        y = progress_y + i
        builder.render_text(progress_x, y, 7, f"{label}:")
        
        # Progress bar background
        for x in range(8):
            builder.draw_character(progress_x + 5 + x, y, 8, ord('░'))
        
        # Progress bar fill
        filled = int((value / 100.0) * 8)
        for x in range(filled):
            color = 10 if value < 50 else 14 if value < 80 else 9
            builder.draw_character(progress_x + 5 + x, y, color, ord('█'))
        
        # Percentage
        builder.render_text(progress_x + 15, y, 7, f"{value:3d}%")
    
    # Create a network diagram
    network_x, network_y = 10, 16
    builder.render_text(network_x, network_y - 1, 11, "Network Topology:")
    
    # Central node
    builder.draw_character(network_x + 10, network_y + 2, 14, ord('●'))
    builder.render_text(network_x + 8, network_y + 3, 7, "Server")
    
    # Connected nodes
    nodes = [(5, 1), (15, 1), (5, 3), (15, 3), (10, 0)]
    for i, (nx, ny) in enumerate(nodes):
        node_x, node_y = network_x + nx, network_y + ny
        builder.draw_character(node_x, node_y, 12, ord('○'))
        builder.draw_line(network_x + 10, network_y + 2, node_x, node_y, 8, ord('·'))
        builder.render_text(node_x - 1, node_y + 1, 7, f"PC{i+1}")
    
    # Add frame around everything
    builder.draw_line(2, 4, width - 3, 4, 7, ord('═'))
    builder.draw_line(2, height - 3, width - 3, height - 3, 7, ord('═'))
    builder.draw_line(2, 4, 2, height - 3, 7, ord('║'))
    builder.draw_line(width - 3, 4, width - 3, height - 3, 7, ord('║'))
    
    # Corner decorations
    builder.draw_character(2, 4, 7, ord('╔'))
    builder.draw_character(width - 3, 4, 7, ord('╗'))
    builder.draw_character(2, height - 3, 7, ord('╚'))
    builder.draw_character(width - 3, height - 3, 7, ord('╝'))
    
    builder.render_text(10, height - 1, 11, "Showcasing: Icons, patterns, progress bars, network diagrams, and decorative frames")
    
    builder.end_of_file()
    return builder.get_data()


def main():
    """Generate showcase demos"""
    if len(sys.argv) < 2:
        print("Usage: python showcase_demos.py [sine|mandelbrot|gameoflife|dataviz|ascii]", file=sys.stderr)
        print("\nAvailable demos:")
        print("  sine       - Animated sine wave visualization")
        print("  mandelbrot - Mandelbrot set fractal")
        print("  gameoflife - Conway's Game of Life simulation")
        print("  dataviz    - Business data visualization")
        print("  ascii      - ASCII art showcase")
        sys.exit(1)
    
    demo_type = sys.argv[1].lower()
    
    if demo_type == "sine":
        data = create_animated_sine_wave()
    elif demo_type == "mandelbrot":
        data = create_mandelbrot_set()
    elif demo_type == "gameoflife":
        data = create_game_of_life()
    elif demo_type == "dataviz":
        data = create_data_visualization_demo()
    elif demo_type == "ascii":
        data = create_ascii_art_showcase()
    else:
        print(f"Unknown demo type: {demo_type}", file=sys.stderr)
        sys.exit(1)
    
    # Output binary data
    sys.stdout.buffer.write(data)


if __name__ == "__main__":
    main()
