from jsonparser.lexer import JsonLexer
from jsonparser.tokens import Token

def test_dummy_token():
    lexer = JsonLexer("{}")
    tokens = list(lexer.tokenize())
    assert tokens[0].type == "DUMMY"
