#!/usr/bin/env python3
"""
Performance benchmarking and monitoring for Terminal Screen Renderer
Professional-grade performance analysis tools
"""

import time
import sys
import os
import statistics
from typing import List, Dict, Any, Callable, Tuple
import tracemalloc
from contextlib import contextmanager
from unittest.mock import Mock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from renderer import ScreenRenderer, process_binary_stream
from demo import BinaryCommandBuilder, create_demo_1, create_demo_2
from showcase_demos import (
    create_animated_sine_wave, create_mandelbrot_set, 
    create_game_of_life, create_data_visualization_demo
)


@contextmanager
def performance_monitor():
    """Context manager for comprehensive performance monitoring"""
    tracemalloc.start()
    start_time = time.perf_counter()
    start_cpu = time.process_time()
    
    try:
        yield
    finally:
        end_time = time.perf_counter()
        end_cpu = time.process_time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Store results in a way that can be accessed
        performance_monitor.last_results = {
            'wall_time': end_time - start_time,
            'cpu_time': end_cpu - start_cpu,
            'memory_current': current,
            'memory_peak': peak
        }


class PerformanceBenchmark:
    """Professional performance benchmarking suite"""
    
    def __init__(self):
        self.results = {}
        self.renderer = None
        
    def setup_renderer(self):
        """Setup renderer with mocked screen for testing"""
        self.renderer = ScreenRenderer()
        self.renderer.screen = Mock()
        
    def benchmark_demo_generation(self, demo_func: Callable, name: str, runs: int = 10) -> Dict[str, Any]:
        """Benchmark demo generation performance"""
        times = []
        memory_usage = []
        data_sizes = []
        
        for _ in range(runs):
            with performance_monitor():
                data = demo_func()
            
            times.append(performance_monitor.last_results['wall_time'])
            memory_usage.append(performance_monitor.last_results['memory_peak'])
            data_sizes.append(len(data))
        
        return {
            'name': name,
            'runs': runs,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_time': statistics.stdev(times) if len(times) > 1 else 0,
            'avg_memory': statistics.mean(memory_usage),
            'avg_data_size': statistics.mean(data_sizes),
            'throughput': statistics.mean(data_sizes) / statistics.mean(times)  # bytes per second
        }
    
    def benchmark_command_processing(self, data: bytes, name: str, runs: int = 10) -> Dict[str, Any]:
        """Benchmark command processing performance"""
        if not self.renderer:
            self.setup_renderer()
            
        times = []
        commands_processed = []
        
        for _ in range(runs):
            self.renderer = ScreenRenderer()
            self.renderer.screen = Mock()
            
            with performance_monitor():
                i = 0
                command_count = 0
                
                while i < len(data) - 1:
                    if i + 1 >= len(data):
                        break
                        
                    command = data[i]
                    length = data[i + 1]
                    
                    if i + 2 + length > len(data):
                        break
                        
                    command_data = list(data[i + 2:i + 2 + length])
                    result = self.renderer.process_command(command, length, command_data)
                    command_count += 1
                    
                    if not result:
                        break
                        
                    i += 2 + length
            
            times.append(performance_monitor.last_results['wall_time'])
            commands_processed.append(command_count)
        
        return {
            'name': name,
            'runs': runs,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'avg_commands': statistics.mean(commands_processed),
            'commands_per_second': statistics.mean(commands_processed) / statistics.mean(times)
        }
    
    def benchmark_memory_efficiency(self, demo_func: Callable, name: str) -> Dict[str, Any]:
        """Detailed memory usage analysis"""
        tracemalloc.start()
        
        # Initial memory snapshot
        initial_snapshot = tracemalloc.take_snapshot()
        
        # Generate demo data
        data = demo_func()
        
        # Memory after generation
        generation_snapshot = tracemalloc.take_snapshot()
        
        # Process the data
        if not self.renderer:
            self.setup_renderer()
        
        i = 0
        while i < len(data) - 1:
            if i + 1 >= len(data):
                break
                
            command = data[i]
            length = data[i + 1]
            
            if i + 2 + length > len(data):
                break
                
            command_data = list(data[i + 2:i + 2 + length])
            self.renderer.process_command(command, length, command_data)
            
            i += 2 + length
        
        # Final memory snapshot
        final_snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        # Calculate memory differences
        gen_stats = generation_snapshot.compare_to(initial_snapshot, 'lineno')
        proc_stats = final_snapshot.compare_to(generation_snapshot, 'lineno')
        
        return {
            'name': name,
            'data_size': len(data),
            'generation_memory': sum(stat.size_diff for stat in gen_stats if stat.size_diff > 0),
            'processing_memory': sum(stat.size_diff for stat in proc_stats if stat.size_diff > 0),
            'memory_efficiency': len(data) / max(sum(stat.size_diff for stat in gen_stats if stat.size_diff > 0), 1)
        }
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        print("🚀 Starting Comprehensive Performance Benchmark")
        print("=" * 60)
        
        # Demo generation benchmarks
        demos = [
            (create_demo_1, "Basic Demo"),
            (create_demo_2, "Pattern Demo"),
            (create_animated_sine_wave, "Sine Wave"),
            (create_mandelbrot_set, "Mandelbrot Set"),
            (create_game_of_life, "Game of Life"),
            (create_data_visualization_demo, "Data Visualization")
        ]
        
        generation_results = []
        processing_results = []
        memory_results = []
        
        for demo_func, name in demos:
            print(f"\n📊 Benchmarking: {name}")
            
            # Generation benchmark
            gen_result = self.benchmark_demo_generation(demo_func, name, runs=5)
            generation_results.append(gen_result)
            
            # Get demo data for processing benchmark
            demo_data = demo_func()
            
            # Processing benchmark
            proc_result = self.benchmark_command_processing(demo_data, name, runs=5)
            processing_results.append(proc_result)
            
            # Memory efficiency
            mem_result = self.benchmark_memory_efficiency(demo_func, name)
            memory_results.append(mem_result)
            
            print(f"  ✓ Generation: {gen_result['avg_time']*1000:.2f}ms avg")
            print(f"  ✓ Processing: {proc_result['avg_time']*1000:.2f}ms avg")
            print(f"  ✓ Throughput: {proc_result['commands_per_second']:.0f} commands/sec")
        
        return {
            'generation': generation_results,
            'processing': processing_results,
            'memory': memory_results,
            'summary': self._generate_summary(generation_results, processing_results, memory_results)
        }
    
    def _generate_summary(self, gen_results: List[Dict], proc_results: List[Dict], mem_results: List[Dict]) -> Dict[str, Any]:
        """Generate performance summary"""
        return {
            'fastest_generation': min(gen_results, key=lambda x: x['avg_time'])['name'],
            'fastest_processing': max(proc_results, key=lambda x: x['commands_per_second'])['name'],
            'most_memory_efficient': max(mem_results, key=lambda x: x['memory_efficiency'])['name'],
            'avg_generation_time': statistics.mean([r['avg_time'] for r in gen_results]),
            'avg_processing_speed': statistics.mean([r['commands_per_second'] for r in proc_results]),
            'total_demos_tested': len(gen_results)
        }


class PerformanceProfiler:
    """Real-time performance profiling for development"""
    
    @staticmethod
    def profile_binary_stream_processing(data: bytes, detailed: bool = False):
        """Profile binary stream processing with detailed breakdown"""
        renderer = ScreenRenderer()
        renderer.screen = Mock()
        
        command_times = {}
        total_commands = 0
        
        start_time = time.perf_counter()
        i = 0
        
        while i < len(data) - 1:
            if i + 1 >= len(data):
                break
                
            command = data[i]
            length = data[i + 1]
            
            if i + 2 + length > len(data):
                break
                
            command_data = list(data[i + 2:i + 2 + length])
            
            # Time individual command
            cmd_start = time.perf_counter()
            result = renderer.process_command(command, length, command_data)
            cmd_end = time.perf_counter()
            
            # Track command performance
            cmd_name = {
                0x1: 'screen_setup',
                0x2: 'draw_character',
                0x3: 'draw_line', 
                0x4: 'render_text',
                0x5: 'cursor_movement',
                0x6: 'draw_at_cursor',
                0x7: 'clear_screen',
                0xFF: 'end_of_file'
            }.get(command, f'unknown_0x{command:02x}')
            
            if cmd_name not in command_times:
                command_times[cmd_name] = []
            command_times[cmd_name].append(cmd_end - cmd_start)
            
            total_commands += 1
            
            if not result:
                break
                
            i += 2 + length
        
        total_time = time.perf_counter() - start_time
        
        # Generate profile report
        report = {
            'total_time': total_time,
            'total_commands': total_commands,
            'commands_per_second': total_commands / total_time if total_time > 0 else 0,
            'data_size': len(data),
            'bytes_per_second': len(data) / total_time if total_time > 0 else 0
        }
        
        if detailed:
            report['command_breakdown'] = {}
            for cmd, times in command_times.items():
                report['command_breakdown'][cmd] = {
                    'count': len(times),
                    'total_time': sum(times),
                    'avg_time': statistics.mean(times),
                    'percentage': (sum(times) / total_time) * 100
                }
        
        return report


def print_benchmark_results(results: Dict[str, Any]):
    """Pretty print benchmark results"""
    print("\n" + "=" * 80)
    print("🏆 PERFORMANCE BENCHMARK RESULTS")
    print("=" * 80)
    
    # Summary
    summary = results['summary']
    print(f"\n📈 PERFORMANCE SUMMARY:")
    print(f"  • Fastest Generation: {summary['fastest_generation']}")
    print(f"  • Fastest Processing: {summary['fastest_processing']}")
    print(f"  • Most Memory Efficient: {summary['most_memory_efficient']}")
    print(f"  • Average Generation Time: {summary['avg_generation_time']*1000:.2f}ms")
    print(f"  • Average Processing Speed: {summary['avg_processing_speed']:.0f} commands/sec")
    print(f"  • Total Demos Tested: {summary['total_demos_tested']}")
    
    # Detailed generation results
    print(f"\n🛠️  DEMO GENERATION PERFORMANCE:")
    print(f"{'Demo':<20} {'Avg Time':<12} {'Throughput':<15} {'Data Size':<12} {'Memory':<10}")
    print("-" * 80)
    
    for result in results['generation']:
        print(f"{result['name']:<20} "
              f"{result['avg_time']*1000:>8.2f}ms   "
              f"{result['throughput']/1024:>8.1f} KB/s   "
              f"{result['avg_data_size']:>8.0f}B   "
              f"{result['avg_memory']/1024:>6.1f}KB")
    
    # Processing performance
    print(f"\n⚡ COMMAND PROCESSING PERFORMANCE:")
    print(f"{'Demo':<20} {'Avg Time':<12} {'Commands/sec':<15} {'Commands':<10}")
    print("-" * 70)
    
    for result in results['processing']:
        print(f"{result['name']:<20} "
              f"{result['avg_time']*1000:>8.2f}ms   "
              f"{result['commands_per_second']:>10.0f}     "
              f"{result['avg_commands']:>8.0f}")
    
    # Memory efficiency
    print(f"\n💾 MEMORY EFFICIENCY:")
    print(f"{'Demo':<20} {'Data Size':<12} {'Generation':<12} {'Processing':<12} {'Efficiency':<10}")
    print("-" * 80)
    
    for result in results['memory']:
        print(f"{result['name']:<20} "
              f"{result['data_size']:>8.0f}B   "
              f"{result['generation_memory']/1024:>8.1f}KB   "
              f"{result['processing_memory']/1024:>8.1f}KB   "
              f"{result['memory_efficiency']:>8.2f}")
    
    print(f"\n{'='*80}")
    print("✨ Benchmark Complete! Use this data to optimize your renderer.")
    print("💡 Pro tip: Higher commands/sec and efficiency ratios are better!")


def main():
    """Run performance benchmarks"""
    if len(sys.argv) > 1 and sys.argv[1] == "--profile":
        # Run profiling mode
        print("🔬 Running Performance Profiler")
        profiler = PerformanceProfiler()
        
        # Profile different demos
        demos = [
            (create_demo_1, "Basic Demo"),
            (create_mandelbrot_set, "Mandelbrot Set")
        ]
        
        for demo_func, name in demos:
            data = demo_func()
            print(f"\n📊 Profiling: {name}")
            report = profiler.profile_binary_stream_processing(data, detailed=True)
            
            print(f"  Total Time: {report['total_time']*1000:.2f}ms")
            print(f"  Commands/sec: {report['commands_per_second']:.0f}")
            print(f"  Bytes/sec: {report['bytes_per_second']/1024:.1f} KB/s")
            
            if 'command_breakdown' in report:
                print("  Command Breakdown:")
                for cmd, stats in sorted(report['command_breakdown'].items(), 
                                       key=lambda x: x[1]['total_time'], reverse=True):
                    print(f"    {cmd:<15}: {stats['count']:>3} calls, "
                          f"{stats['avg_time']*1000:>6.2f}ms avg, "
                          f"{stats['percentage']:>5.1f}% of total")
    
    else:
        # Run full benchmark suite
        benchmark = PerformanceBenchmark()
        results = benchmark.run_comprehensive_benchmark()
        print_benchmark_results(results)


if __name__ == "__main__":
    main()
