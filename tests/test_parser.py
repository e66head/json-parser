import pytest
from jsonparser.parser import JsonParser
from jsonparser.errors import (
    ExtraColonError,
    ExtraCommaError,
    ExtraDataError,
    InvalidKeyError,
    LeadingCommaError,
    MissingColonError,
    MissingCommaError,
    MissingKeyError,
    MissingLeftBraceError,
    MissingLeftBracketError,
    MissingRightBraceError,
    MissingRightBracketError,
    MissingValueError,
    TrailingCommaError,
    UnexpectedTokenError
)

def test_parser_basic_object():
    json_str = '{"key": "value"}'
    parser = JsonParser(json_str)
    result = parser.parse()
    assert result == {"key": "value"}

def test_parser_empty_object():
    json_str = '{}'
    parser = JsonParser(json_str)
    result = parser.parse()
    assert result == {}

def test_parser_basic_array():
    json_str = '[1, 2, 3]'
    parser = JsonParser(json_str)
    result = parser.parse()
    assert result == [1, 2, 3]

def test_parser_empty_array():
    json_str = '[]'
    parser = JsonParser(json_str)
    result = parser.parse()
    assert result == []

def test_parser_complex_object():
    json_str = """
    {
        "string": "value",
        "number": 123,
        "bool_true": true,
        "bool_false": false,
        "null_val": null,
        "list": [1, 2, {"nested": "obj"}],
        "nested_obj": {
            "a": 1,
            "b": [true, false]
        }
    }
    """
    parser = JsonParser(json_str)
    result = parser.parse()
    assert result["string"] == "value"
    assert result["number"] == 123
    assert result["list"][2]["nested"] == "obj"
    assert result["nested_obj"]["b"] == [True, False]

@pytest.mark.parametrize("invalid_json, expected_error, expected_match", [
    # Object Errors
    ('{ "key" "value" }',       MissingColonError, "Missing colon between key and value"),
    ('{ : "value" }',           MissingKeyError,   "Unexpected colon when expecting a string key"),
    ('{ 123: "value" }',        InvalidKeyError,   "Invalid key type NUMBER"),
    ('{ "key": , }',            MissingValueError, "Unexpected comma when expecting a value"),
    ('{ "key": "v", , }',       ExtraCommaError,   "Unexpected extra comma in object"),
    ('{ "key": "v" "key2": 1}', MissingCommaError, "Missing comma between object members"),
    ('{ , "key": "v" }',        LeadingCommaError, "Unexpected leading comma in object"),
    ('{ "key":: "value" }',     ExtraColonError,   "Unexpected double colon"),

    # Structural Object Errors
    ('}',                     MissingLeftBraceError, "Unexpected right brace without matching left brace"),
    ('{',                     MissingRightBraceError, "Unexpected end of object. Missing right brace"),
])
def test_parser_object_errors(invalid_json, expected_error, expected_match):
    parser = JsonParser(invalid_json)
    with pytest.raises(expected_error, match=expected_match):
        parser.parse()

@pytest.mark.parametrize("invalid_json, expected_error, expected_match", [
    # Array Errors
    ("[, 1, 2]",              LeadingCommaError,    "Unexpected leading comma"),
    ("[1, , 2]",              ExtraCommaError,      "Unexpected comma when expecting a value"),
    ("[1, 2,]",               TrailingCommaError,   "Unexpected trailing comma"),
    ("[1 2]",                 MissingCommaError,    "Unexpected value when expecting a comma"),

    # Structural Array Errors
    ("]",                     MissingLeftBracketError, "Unexpected right bracket without matching left bracket"),
    ("[",                     MissingRightBracketError, "Unexpected end of array. Missing right bracket"),
])
def test_parser_array_errors(invalid_json, expected_error, expected_match):
    parser = JsonParser(invalid_json)
    with pytest.raises(expected_error, match=expected_match):
        parser.parse()

def test_parser_extra_data():
    json_str = '{"a": 1} "extra"'
    parser = JsonParser(json_str)
    with pytest.raises(ExtraDataError, match="Unexpected end of JSON input. Extra data found."):
        parser.parse()

def test_parser_no_data():
    json_str = ''
    parser = JsonParser(json_str)
    # The lexer will yield EOF immediately, parser will raise ExtraDataError
    with pytest.raises(ExtraDataError, match="Unexpected end of JSON input. No data found."):
        parser.parse()
