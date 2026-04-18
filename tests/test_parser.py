from jsonparser.parser import JsonParser

def test_parser_runs():
    parser = JsonParser('{"foo": 1}')
    result = parser.parse()
    assert result is None
