import time
import json
import pytest
from jsonparser.parser import JsonParser

def test_monster_parse_performance(monster_file):
    """Measures the time it takes to parse the monster JSON and compares it to built-in json."""
    with open(monster_file, "r") as f:
        content = f.read()
    
    file_size_mb = len(content) / (1024 * 1024)
    print(f"\n[Performance Test] File Size: {file_size_mb:.2f} MB")

    # 1. Benchmark: Built-in json module
    json_failed = False
    try:
        start_time = time.perf_counter()
        json.loads(content)
        json_duration = time.perf_counter() - start_time
        print(f"[Performance Test] Built-in json: {json_duration:.4f} seconds")
    except RecursionError:
        print("[Performance Test] Built-in json: FAILED (RecursionError)")
        json_failed = True

    # 2. Custom Parser
    start_time = time.perf_counter()
    parser = JsonParser(content)
    result = parser.parse()
    custom_duration = time.perf_counter() - start_time
    print(f"[Performance Test] Custom Parser: {custom_duration:.4f} seconds")
    
    # 3. Final Comparison
    if json_failed:
        print("[Performance Test] Custom Parser survived where built-in json failed!")
    else:
        ratio = custom_duration / json_duration
        print(f"[Performance Test] Custom Parser is {ratio:.2f}x slower than built-in json.")

    assert result is not None
    assert isinstance(result, dict)
