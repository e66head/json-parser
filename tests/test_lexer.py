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
    assert tokens[0] == Token(TokenType.LBRACE, "{", tokens[0].line)

    assert tokens[1] == Token(TokenType.STRING, "foo", tokens[1].line)
    assert tokens[2] == Token(TokenType.COLON, ":", tokens[2].line)
    assert tokens[3] == Token(TokenType.NUMBER, 1, tokens[3].line)
    assert tokens[4] == Token(TokenType.COMMA, ",", tokens[4].line)

    assert tokens[5] == Token(TokenType.STRING, "bar", tokens[5].line)
    assert tokens[6] == Token(TokenType.COLON, ":", tokens[6].line)
    assert tokens[7] == Token(TokenType.LBRACKET, "[", tokens[7].line)
    assert tokens[8] == Token(TokenType.TRUE, True, tokens[8].line)
    assert tokens[9] == Token(TokenType.COMMA, ",", tokens[9].line)
    assert tokens[10] == Token(TokenType.FALSE, False, tokens[10].line)
    assert tokens[11] == Token(TokenType.COMMA, ",", tokens[11].line)
    assert tokens[12] == Token(TokenType.NULL, None, tokens[12].line)
    assert tokens[13] == Token(TokenType.RBRACKET, "]", tokens[13].line)

    assert tokens[14] == Token(TokenType.RBRACE, "}", tokens[14].line)
    assert tokens[15] == Token(TokenType.EOF, None, tokens[15].line)
