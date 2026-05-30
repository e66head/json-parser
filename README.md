# JSON Parser

A pure-Python [JSON](https://www.json.org/json-en.html) lexer and parser written from scratch for educational and practical use.

This code is in active development. See the [ROADMAP](ROADMAP.md) for planned features such as JSONC and JSON5 support.
While it is fully compliant with the JSON specification (RFC 8259), it should be considered educational in nature.

## Usage

### As an importable module

```python
from jsonparser import JsonParser

parser = JsonParser('{"foo": 123, "bar": true}')
data = parser.parse()
print(data)
```

### As a shell script

The package can be run directly as a utility:

```shell
python -m jsonparser [options] [json-file]
```

**Common Examples:**

* **Standard:** `python -m jsonparser data.json`
* **Pickle (Auto-name):** `python -m jsonparser data.json -p` (creates `data.pkl`)
* **Stealth (Logs to file):** `python -m jsonparser data.json -o result.txt --log-file debug.log -s -t`
* **Piping:** `cat data.json | python -m jsonparser -t > result.txt`

**Available Options:**

| Option       | Short | Description                                                   |
| :----------- | :---- | :------------------------------------------------------------ |
| `--help`     | `-h`  | Show the help message and exit                                |
| `--version`  | `-v`  | Show the program's version number and exit                    |
| `--output`   | `-o`  | Path to a file where the parsed Python object will be written |
| `--pickle`   | `-p`  | Output as a binary Pickle file (auto-names if -o is omitted)  |
| `--time`     | `-t`  | Time the parsing operation and report duration to stderr      |
| `--silent`   | `-s`  | Suppress data output to the console                           |
| `--log`      | `-l`  | Set log level (CRITICAL, ERROR, WARNING, INFO, DEBUG)         |
| `--log-file` |       | Path to a file where logs will be written                     |

## Unit Testing

This project uses the "test_parsing" files from the [JSON Parsing Test Suite](https://github.com/nst/JSONTestSuite) by Nicolas Seriot (licensed under the MIT License) to ensure full compliance with the JSON specification.

### Running Tests

To run all tests (Lexer, Parser, and the full Compliance Suite):

```shell
python -m pytest
```

### Specific Test Modules

If you are debugging a specific area, you can run individual test files:

| Target               | Command                              |
| :------------------- | :----------------------------------- |
| **Lexer**            | `pytest tests/test_lexer.py`         |
| **Parser**           | `pytest tests/test_parser.py`        |
| **Compliance Suite** | `pytest tests/test_suite_runner.py`  |

**Debugging:** Add `--log-cli-level=DEBUG` to any of the above commands to see detailed internal state transitions and tokenization logs during the test run.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
