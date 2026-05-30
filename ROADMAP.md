# Project Roadmap

This document covers where this JSON parser is headed next. The goal is to move from a "standard" parser to one that can
handle very large files efficiently and support more flexible formats like JSONC and JSON5.

## Phase 1: Supporting Other JSONs

- [ ] **JSONC**: Extend the Lexer to support and ignore both single-line (`//`) and multi-line (`/* */`) comments.
- [ ] **JSON5**:
  - [ ] **Strings**: Support single-quoted (') strings.
  - [ ] **Objects**: Support unquoted and reserved-word keys; allow trailing commas.
  - [ ] **Arrays**: Allow trailing commas.
  - [ ] **Numbers**: Support hex numbers (like 0x123), plus signs, positive/negative Infinity, and NaN.

## Phase 2: Memory & Speed (The "40MB+ Overhaul")

- [ ] **Object Overhead**: Optimize the `Token` class (use `__slots__` to reduce its memory footprint).
- [ ] **True Streaming Mode**:
  - [ ] **Byte-Stream Lexing**: Transition `JsonLexer` to consume `BinaryIO` (raw bytes) in small chunks rather than a single `str`. This eliminates the "Double Memory" penalty where the entire file must be loaded into RAM before parsing begins.
  - [ ] **Incremental Parser Yielding**: Update `JsonParser` to `yield` fully-reduced objects or array elements as soon as they are completed. This allows users to process massive top-level arrays (e.g., log files) item-by-item without ever buffering the entire JSON structure.
- [ ] **Faster Reductions**: Clean up the "Reduction" steps to build dictionaries and lists directly from the main stack
- [ ] **Type Hinting**: Finish adding Python type hints to make the code easier to read and debug in VS Code.

## Phase 3: Better Errors & Testing

- [ ] **Better Errors**: Use the line and column logic for better diagnostic error messages.
- [ ] **Performance Benchmarking**: Add additional perfomance testing to compare with other JSON parsers.
- [ ] **Validity Benchmarking**: Consider adding this project to other validity testing (like [JSON Parsing Test Suite](https://github.com/nst/JSONTestSuite))

## A.I. Review (consider adding to roadmap)

### Critical/Correctness Issues

- [x] **Strict String Decoding**: Replace unicode_escape with a manual escape sequence handler. unicode_escape handles Python-specific escapes (like \xHH or \v) that are forbidden in the JSON spec (RFC 8259).
- [ ] **Duplicate Key Detection**: The current object reduction (dictionary[key] = token.value) silently overwrites duplicate keys. Standard JSON suggests (and some parsers require) flagging or specific handling for duplicate keys.
- [ ] **Maximum Depth Protection**: Although shift-reduce is better than recursion, a maliciously nested JSON (e.g., 10,000 [[[[...]]]]) could still lead to massive memory spikes or stack issues. A configurable depth limit is recommended.

### Architecture & Refinement

- [ ] **Zero-Slice Unescaping**: Optimize `_json_unescape` to avoid string slicing (like `esc[1:]`) by including backslashes directly in the `UNESCAPE_MAP` or using regex groups. This reduces garbage collection pressure on large files.
- [ ] **Lexer `__slots__`**: The roadmap mentions `__slots__` for the Token class, but the JsonLexer itself (which stores the entire _json_str) could also benefit from slotting if many lexers are instantiated.
- [ ] **Integer Overflow Strategy**: Python handles arbitrarily large integers, but for compatibility with other languages (like C++ or Java), you might want to add an option to flag integers that exceed 64-bit precision.
- [ ] **Error Context (Snippets)**: While the roadmap mentions "line and column logic," it doesn't specify showing a code snippet (e.g., ^ pointing to the error) in the console output, which significantly improves developer experience.
