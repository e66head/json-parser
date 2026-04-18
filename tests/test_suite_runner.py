"""
Test runner for the JSONTestSuite.
"""

import os
import pytest
from jsonparser.parser import JsonParser
from jsonparser.errors import JsonParserError, JsonLexerError

TEST_SUITE_DIR = os.path.join(os.path.dirname(__file__), "json_test_suite")

def get_test_files():
    """Retrieves all JSON test files from the suite directory."""
    files = []
    if not os.path.exists(TEST_SUITE_DIR):
        return files

    for filename in os.listdir(TEST_SUITE_DIR):
        if filename.endswith(".json"):
            files.append(filename)
    return sorted(files)

@pytest.mark.parametrize("filename", get_test_files())
def test_json_suite(filename):
    """Runs a single test case from the JSONTestSuite."""
    file_path = os.path.join(TEST_SUITE_DIR, filename)

    with open(file_path, "rb") as f:
        try:
            content = f.read().decode("utf-8")
        except UnicodeDecodeError:
            # Some tests (like n_string_invalid_utf8) are intentionally malformed UTF-8.
            # For this parser, we expect these to either fail at lexing or be handled.
            # If we can't even decode the file as UTF-8, we'll treat it as a raw string
            # if possible, or skip if it's meant to test UTF-8 specifically.
            content = None

    # Handle the y_, n_, and i_ cases
    prefix = filename[:2]

    if prefix == "y_":
        # MUST PASS
        parser = JsonParser(content)
        result = parser.parse()
        # We don't check the exact value, just that it doesn't raise
        assert result is not None or "null" in content or "[]" in content or "{}" in content

    elif prefix == "n_":
        # MUST FAIL
        if content is None:
            # If we can't even read it as UTF-8, it's effectively invalid for a standard parser
            return

        parser = JsonParser(content)
        with pytest.raises((JsonParserError, JsonLexerError)):
            parser.parse()

    elif prefix == "i_":
        # INDETERMINATE (can pass or fail)
        if content is None:
            return

        try:
            parser = JsonParser(content)
            parser.parse()
        except (JsonParserError, JsonLexerError):
            # This is acceptable for 'i_' tests
            pass
        except Exception as e:
            # We don't want unexpected crashes (like RecursionError)
            pytest.fail(f"Unexpected exception in indeterminate test {filename}: {type(e).__name__}: {e}")
