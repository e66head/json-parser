# JSON Parser

A pure-Python JSON lexer and parser written from scratch for educational and practical use.

This code should not be considered ready for any production use! It's licensed to allow free use for any purpose. But buyer beware. This code is being used to
better learn Python and explore its features. As a result, it will undergo big changes over time.

## Usage

```python
from jsonparser import JsonParser

parser = JsonParser('{"foo": 123, "bar": true}')
data = parser.parse()
print(data)
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
