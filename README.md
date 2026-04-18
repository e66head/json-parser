# JSON Parser

A pure-Python JSON lexer and parser written from scratch for educational and practical use.

This code should not be considered ready for any production use! However, it's MIT-licensed to allow liberal use for
most any purpose. But buyer beware. This code is being used to better learn Python and explore its features. As a
result, it will undergo changes. There are no plans to productize this code. There is no definite roadmap.

## Usage

```python
from jsonparser import JsonParser

parser = JsonParser('{"foo": 123, "bar": true}')
data = parser.parse()
print(data)
```

## Unit Testing

This project uses the "test_parsing" files from the [JSON Parsing Test Suite](https://github.com/nst/JSONTestSuite) by
Nicolas Seriot (licensed under the MIT License) to ensure full compliance with the JSON specification.

### Test the Lexer

```shell
python -m pytest [--log-cli-level=[INFO|DEBUG]] tests/test_lexer.py
python -m pytest [--log-cli-level=[INFO|DEBUG]] tests/test_parser.py
python -m pytest [--log-cli-level=[INFO|DEBUG]] tests/test_suite_runner.py
```

### Run All Tests

```shell
python -m pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
