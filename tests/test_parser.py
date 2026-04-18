"""
Unit tests for the JSON Parser.
"""

import pytest

from jsonparser.parser import * # pylint: disable=wildcard-import,unused-wildcard-import
from jsonparser.errors import * # pylint: disable=wildcard-import,unused-wildcard-import

#
# Ensure that valid arrays are parsed correctly.
#
@pytest.mark.parametrize("valid_json, expected_result", [
    ("[]",        []),
    ("[1]",       [1]),
    ("[1, 2, 3]", [1, 2, 3]),
])
def test_parser_valid_array(valid_json, expected_result):
    """Tests that valid arrays are parsed correctly."""
    parser = JsonParser(valid_json)
    assert parser.parse() == expected_result

#
# Ensure malformed arrays raise specific errors with helpful messages.
#
@pytest.mark.parametrize("invalid_json, expected_error, expected_match", [
    ("[, 1, 2]", LeadingCommaError,        "Unexpected leading comma"),
    ("[1, , 2]", ExtraCommaError,          "Unexpected comma when expecting a value"),
    ("[1, 2,]",  TrailingCommaError,       "Unexpected trailing comma"),
    ("[1 2]",    MissingCommaError,        "Unexpected value when expecting a comma"),
    ("]",        MissingLeftBracketError,  "Unexpected end of array"),
    ("[",        MissingRightBracketError, "Unexpected end of array"),
    ("1, 2]",    MissingLeftBracketError,  "Unexpected end of array"),
])
def test_parser_array_errors(invalid_json, expected_error, expected_match):
    """Ensures that various malformed arrays raise specific errors with helpful messages."""
    parser = JsonParser(invalid_json)
    with pytest.raises(expected_error, match=expected_match):
        parser.parse()

#@pytest.mark.parametrize("malformed_json", [
#    ("[1, 2"),      # Unclosed array
#    ("1, 2"),       # Multiple values/trailing comma at root
#    ("[1] true"),   # Trailing data after valid JSON
#    ('{"a": 1'),    # Unclosed object
#])
#def test_parser_structural_errors(malformed_json):
#    """Ensures that malformed JSON structures that leave junk on the stack raise an error."""
#    parser = JsonParser(malformed_json)
#    with pytest.raises(JsonParserError):
#        parser.parse()
#def test_parser_basic_object():
#    """Ensures that the parser can handle a simple object."""
#    parser = JsonParser('{"foo": 1}')
#    result = parser.parse()
#    assert result is not None

JSON_DATA =r"""
{
  "project": "JSON Parser",
  "version": 0.1,
  "beta": true,
  "released": null,
  "features": [
    "arrays",
    "objects",
    "numbers (123, -4.5, 6.7e+8)",
    "strings with escapes: \" \/ \b \f \n \r \t",
    "unicode: \u2728"
  ],
  "metadata": {
    "author": "Frankie",
    "tags": ["python", "lexer", "parser"],
    "stats": {
      "lines_of_code": 1024,
      "test_coverage": 0.98,
      "is_functional": true
    },
    "empty_stuff": {
      "empty_array": [],
      "empty_object": {}
    }
  },
  "deeply_nested": [[[[{"key": "value"}]]]]
}
"""



def test_parser_complex_object():
    """Ensures that the parser can handle a complex object."""
    parser = JsonParser(JSON_DATA)
    result = parser.parse()

    print(result)
