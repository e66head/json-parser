"""
Verification tests for JSON with comments (JSONC) support in version 0.3.0.
"""

import pytest
import os
from jsonparser.lexer import JsonDialect
from jsonparser.parser import JsonParser
from jsonparser.errors import UnexpectedCharacterError, ExtraDataError

def test_strict_mode_rejects_comments():
    """Verify that the default STRICT dialect still rejects comments."""
    json_str = '{"a": 1} // comment'
    parser = JsonParser(json_str) # Default is JSON (Strict)
    with pytest.raises(UnexpectedCharacterError):
        parser.parse()

def test_jsonc_mode_accepts_comments():
    """Verify that the JSONC dialect accepts comments."""
    json_str = '{"a": 1} // comment'
    parser = JsonParser(json_str, dialect=JsonDialect.JSONC)
    result = parser.parse()
    assert result == {"a": 1}

def test_allow_comments_convenience_flag():
    """Verify that the allow_comments flag correctly promotes the dialect."""
    json_str = '{"a": 1} // comment'
    # Test True
    parser = JsonParser(json_str, allow_comments=True)
    assert parser.parse() == {"a": 1}
    
    # Test False
    parser_strict = JsonParser(json_str, allow_comments=False)
    with pytest.raises(UnexpectedCharacterError):
        parser_strict.parse()

def test_comment_placements():
    """Test various placements of comments in JSONC."""
    json_str = """
    // Leading comment
    {
        /* Block comment
           on multiple lines */
        "key": "value", // Inline comment
        "list": [
            1, // item comment
            /* nested block */ 2,
            3
        ] /* trailing block */
    }
    // Final comment
    """
    parser = JsonParser(json_str, dialect=JsonDialect.JSONC)
    assert parser.parse() == {"key": "value", "list": [1, 2, 3]}

def test_comment_regex_edge_cases():
    """Test edge cases for comment regex matching."""
    # Empty block comment
    assert JsonParser('{"a":/**/1}', dialect=JsonDialect.JSONC).parse() == {"a": 1}
    
    # Comment at EOF without newline
    assert JsonParser('{"a":1}//', dialect=JsonDialect.JSONC).parse() == {"a": 1}
    
    # Block comment at EOF without newline
    assert JsonParser('{"a":1}/**/', dialect=JsonDialect.JSONC).parse() == {"a": 1}

    # Characters in comments that look like JSON tokens
    json_str = '{"a": 1} // { "b": 2 } /* [3, 4] */'
    assert JsonParser(json_str, dialect=JsonDialect.JSONC).parse() == {"a": 1}

def test_json_test_suite_integration():
    """Test using actual files from the JSON Parsing Test Suite that contain comments."""
    base_path = os.path.join(os.path.dirname(__file__), "json_test_suite")
    
    # These files are marked 'n_' (should fail) in standard JSON because of comments.
    # In JSONC, they should now pass.
    comment_files = [
        "n_object_trailing_comment.json",            # {"a":"b"}/**/
        "n_object_trailing_comment_slash_open.json", # {"a":"b"}//
        "n_structure_object_with_comment.json",      # {"a":/*comment*/"b"}
    ]
    
    for filename in comment_files:
        path = os.path.join(base_path, filename)
        with open(path, "r") as f:
            content = f.read()
            
        # 1. Should fail in STRICT mode
        parser_strict = JsonParser(content, dialect=JsonDialect.JSON)
        with pytest.raises(UnexpectedCharacterError):
            parser_strict.parse()
            
        # 2. Should pass in JSONC mode
        parser_jsonc = JsonParser(content, dialect=JsonDialect.JSONC)
        result = parser_jsonc.parse()
        assert result == {"a": "b"}

def test_invalid_trailing_garbage_after_comment():
    """Ensure that garbage after a valid comment is still caught."""
    # The '//' comment is valid, but the trailing '/' is garbage.
    json_str = '{"a":"b"}/**//'
    parser = JsonParser(json_str, dialect=JsonDialect.JSONC)
    with pytest.raises(UnexpectedCharacterError):
        parser.parse()

    # Hash comments are NOT supported in our JSONC implementation (keeping it strict to VS Code style).
    json_str_hash = '{"a":"b"} # comment'
    parser_hash = JsonParser(json_str_hash, dialect=JsonDialect.JSONC)
    with pytest.raises(UnexpectedCharacterError):
        parser_hash.parse()
