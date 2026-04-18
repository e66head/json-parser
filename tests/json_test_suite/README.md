# JSON Parsing Test Suite

This directory contains test cases from the [JSON Parsing Test Suite](https://github.com/nst/JSONTestSuite) project by Nicolas Seriot.

## Origin

* **Repository:** [JSON Parsing Test Suite](https://github.com/nst/JSONTestSuite)
* **Author:** Nicolas Seriot
* **License:** MIT License (See [LICENSE](LICENSE) in this directory)
* **Commit:** [1ef36fa012](https://github.com/nst/JSONTestSuite/tree/1ef36fa01286573e846ac449e8683f8833c5b26a) (Fetched: 2026-04-16)

## Test Naming Convention

The files are named according to the expected behavior of the parser when parsing its contents:

* **`y_` (Yes):** Valid JSON that a parser **must** accept.
* **`n_` (No):** Invalid JSON that a parser **must** reject.
* **`i_` (Indeterminate):** Edge cases where the JSON specification is ambiguous or parser behavior may vary (e.g., specific Unicode sequences or large numbers). Parsers may either accept or reject these.

These files are used by `tests/test_suite_runner.py` to ensure the compliance of this JSON parser with the standard.
