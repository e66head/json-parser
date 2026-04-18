import time
import json
import os
import sys

# Add the project root to the path so we can import jsonparser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from jsonparser.parser import JsonParser

def generate_monster_string(depth, breadth):
    """Simple streaming generator to create the string in memory."""
    parts = []
    for i in range(depth, 1, -1):
        parts.append(f'{{"id": "level_{i}", "data": [')
    
    parts.append('{"id": "level_1", "data": [')
    parts.append(', '.join([f'"leaf_{j}"' for j in range(breadth)]))
    parts.append(']}')
    
    for i in range(2, depth + 1):
        for j in range(1, breadth):
            parts.append(f', "item_{j}"')
        parts.append(']}')
    
    return "".join(parts)

def run_benchmarks():
    depths = [10, 50, 100, 200, 300, 400, 500]
    breadths = [10, 50, 100, 200, 300, 400, 500]
    results = []

    # Ensure output directory exists
    output_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "../output"))
    os.makedirs(output_dir, exist_ok=True)

    total_runs = len(depths) * len(breadths)
    current_run = 0

    print(f"Starting benchmark of {total_runs} combinations...")

    for d in depths:
        for b in breadths:
            current_run += 1
            print(f"[{current_run}/{total_runs}] Testing depth={d}, breadth={b}...", end="\r")
            
            content = generate_monster_string(d, b)
            
            # Benchmark Custom Parser
            start = time.perf_counter()
            parser = JsonParser(content)
            parser.parse()
            custom_time = time.perf_counter() - start
            
            # Benchmark Built-in
            start = time.perf_counter()
            json.loads(content)
            builtin_time = time.perf_counter() - start
            
            results.append({
                "depth": d,
                "breadth": b,
                "custom_time": custom_time,
                "builtin_time": builtin_time,
                "size_kb": len(content) / 1024
            })

    results_path = os.path.join(output_dir, "benchmark_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nBenchmark complete. Data saved to '{results_path}'.")

if __name__ == "__main__":
    run_benchmarks()
