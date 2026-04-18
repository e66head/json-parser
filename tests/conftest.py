import os
import pytest

def pytest_addoption(parser):
    """Register custom CLI flags for the monster generator."""
    parser.addoption("--depth", action="store", default=100, type=int, help="Nesting depth of the monster JSON")
    parser.addoption("--breadth", action="store", default=100, type=int, help="Number of items per level")

@pytest.fixture(scope="session")
def monster_file(request):
    """Fixture that generates a monster JSON by hand-writing strings to a file."""
    depth = request.config.getoption("--depth")
    breadth = request.config.getoption("--breadth")
    
    # Ensure the output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    file_name = os.path.join(output_dir, f"monster_d{depth}_b{breadth}.json")
    
    if os.path.exists(file_name):
        return file_name

    print(f"\n[Generator] Writing {file_name} (depth={depth}, breadth={breadth})...")
    
    with open(file_name, "w") as f:
        # Phase 1: Open the nested structure (Downwards).
        for i in range(depth, 1, -1):
            f.write(f'{{"id": "level_{i}", "data": [')

        # Phase 2: Write the deepest level (The "Core").
        f.write('{"id": "level_1", "data": [')
        f.write(', '.join([f'"leaf_{j}"' for j in range(breadth)]))
        f.write(']}') # Close Level 1's "data" array and object.

        # Phase 3: Close the parents and append their sibling data (Upwards).
        for i in range(2, depth + 1):
            for j in range(1, breadth):
                f.write(f', "item_{j}"')
            f.write(']}') # Close the current level's "data" array and object.

    size_mb = os.path.getsize(file_name) / (1024 * 1024)
    print(f"[Generator] Done: {size_mb:.2f} MB")
    
    return file_name
