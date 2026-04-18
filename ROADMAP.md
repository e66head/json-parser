# Project Roadmap

This document outlines the planned future directions for the JSON Parser project.

## Phase 1: Architectural Refinement
- [ ] **Configurable Lexer**: Transition class-level constants and static methods in `JsonLexer` to instance-level properties. This will allow the lexer to be easily extended or configured for different dialects.
- [ ] **Dependency Injection**: Implement a `JsonDialect` configuration object that can be passed through the Lexer and Parser.

## Phase 2: Dialect Support
- [ ] **JSONC (JSON with Comments)**: Extend the Lexer to support and ignore both single-line (`//`) and multi-line (`/* */`) comments.
- [ ] **JSON5 Support**:
    - [ ] **Strings**: Support single-quoted strings.
    - [ ] **Objects**: Support unquoted and reserved-word keys; allow trailing commas.
    - [ ] **Arrays**: Allow trailing commas.
    - [ ] **Numbers**: Support Hexadecimal, positive/negative Infinity, and NaN.

## Phase 3: Performance & Diagnostics
- [ ] **Object Overhead Reduction**: Optimize the `Token` object usage to reduce memory allocation during large parses.
- [ ] **Advanced Diagnostics**: Implement the "Diagnostic" error functions to provide even more granular context about structural failures.
- [ ] **Type Hinting**: Complete the transition to full type safety across the codebase.

## Phase 4: Ecosystem Integration
- [ ] **Performance Benchmarking Suite**: Create a dedicated suite to track performance regressions compared to Python's built-in `json` module.
