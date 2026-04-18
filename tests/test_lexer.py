""""
Unit tests for the JSON Lexer.
"""

from jsonparser.lexer import JsonLexer
from jsonparser.tokens import Token, TokenType

JSON_LINE_MAP = {
    1: '{',
    2: '    "foo": 1,',
    3: '    "bar": [true, false, null]',
    4: '}',
}

def test_json_lexer_complex_object():
    """Tests that the lexer correctly tokenizes a complex JSON object."""

    lexer = JsonLexer("\n".join(JSON_LINE_MAP.values()))
    tokens = list(lexer.tokenize())

    # Helper to get the line number for a specific key
    l1, l2, l3, l4 = JSON_LINE_MAP.keys()

    # Check for specific token types and values
    assert tokens[0] == Token(TokenType.LBRACE, "{", l1)

    assert tokens[1] == Token(TokenType.STRING, "foo", l2)
    assert tokens[2] == Token(TokenType.COLON, ":", l2)
    assert tokens[3] == Token(TokenType.NUMBER, 1, l2)
    assert tokens[4] == Token(TokenType.COMMA, ",", l2)

    assert tokens[5] == Token(TokenType.STRING, "bar", l3)
    assert tokens[6] == Token(TokenType.COLON, ":", l3)
    assert tokens[7] == Token(TokenType.LBRACKET, "[", l3)
    assert tokens[8] == Token(TokenType.TRUE, True, l3)
    assert tokens[9] == Token(TokenType.COMMA, ",", l3)
    assert tokens[10] == Token(TokenType.FALSE, False, l3)
    assert tokens[11] == Token(TokenType.COMMA, ",", l3)
    assert tokens[12] == Token(TokenType.NULL, None, l3)
    assert tokens[13] == Token(TokenType.RBRACKET, "]", l3)

    assert tokens[14] == Token(TokenType.RBRACE, "}", l4)
    assert tokens[15] == Token(TokenType.EOF, None, l4)
