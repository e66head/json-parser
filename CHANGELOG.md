# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-05-31

### Added

- **JSONC Support**: Added support for single-line (`//`) and multi-line (`/* */`) comments.
- **Dialect System**: Introduced `JsonDialect` enum to manage different JSON flavors (STRICT, JSONC).
- **Opt-in Comments**: Added `dialect` and `allow_comments` parameters to `JsonParser` and `JsonLexer` to maintain RFC 8259 compliance by default.

### Changed

- Refactored `JsonLexer` to use a "Dual-Regex" pattern for better performance when comments are disabled.
- Renamed token `handler` to `tokenizer` in `JsonLexer` for better semantic clarity.
- Updated `JsonLexer` to prioritize whitespace matching at the top of the token dictionary.

## [0.2.0] - 2026-05-28

### Added

- Initial implementation of the shift-reduce parser.
- Support for standard JSON types (Strings, Numbers, Objects, Arrays, Booleans, Null).
- Manual escape sequence handling for strict RFC 8259 compliance.
