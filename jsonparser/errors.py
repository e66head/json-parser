"""
Custom exception classes for handling errors in a JSON lexer and parser.

This module defines a hierarchy of exception classes for reporting specific errors encountered during the lexical analysis and parsing of JSON data. It
includes base exception classes for both the lexer and parser, as well as specialized exceptions for various error conditions such as unexpected tokens,
invalid characters, malformed numbers, and structural issues in JSON objects and arrays.

Classes:
    JsonLexerError: Base exception for lexer-related errors.
    JsonParserError: Base exception for parser-related errors.
"""

###JDG TODO: Fix these pylint errors.
# pylint: disable=missing-class-docstring

class JsonLexerError(Exception):
    """Base exception for JsonLexer errors."""

class EndOfJsonError(JsonLexerError):
    pass

class ObjectStartError(JsonLexerError):
    pass

class ObjectMembersError(JsonLexerError):
    pass

class ObjectEndError(JsonLexerError):
    pass

class JsonKeyError(JsonLexerError):
    pass

class ColonError(JsonLexerError):
    pass

class ArrayStartError(JsonLexerError):
    pass

class ArrayElementsError(JsonLexerError):
    pass

class ArrayEndError(JsonLexerError):
    pass

class StringStartError(JsonLexerError):
    pass

class StringCharactersError(JsonLexerError):
    pass

class StringEndError(JsonLexerError):
    pass

class CharacterError(JsonLexerError):
    pass

class LiteralError(JsonLexerError):
    pass

class NumberError(JsonLexerError):
    pass

class TrueError(JsonLexerError):
    pass

class FalseError(JsonLexerError):
    pass

class NullError(JsonLexerError):
    pass

class EscapeError(JsonLexerError):
    pass

class OneNineError(JsonLexerError):
    pass

class OneNineIndexError(JsonLexerError):
    pass

class DigitError(JsonLexerError):
    pass

class DigitsError(JsonLexerError):
    pass

class IntegerError(JsonLexerError):
    pass

class FractionError(JsonLexerError):
    pass

class ExponentError(JsonLexerError):
    pass

class JsonParserError(Exception):
    """Base exception for JsonParser errors."""

class UnknownEventError(JsonParserError):
    pass

class InvalidStateError(JsonParserError):
    pass
