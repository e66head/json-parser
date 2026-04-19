"""
Custom exception classes for handling errors in a JSON lexer and parser.

This module defines a hierarchy of exception classes for reporting specific errors encountered during the lexical
analysis and parsing of JSON data. It includes base exception classes for both the lexer and parser, as well as
specialized exceptions for various error conditions such as unexpected tokens, invalid characters, malformed numbers,
and structural issues in JSON objects and arrays.

Classes:
    JsonLexerError: Base exception for lexer-related errors.
    JsonParserError: Base exception for parser-related errors.
"""

# pylint: disable=missing-class-docstring
# pylint: disable=multiple-statements

class JsonLexerError(Exception):
    """Base exception for JsonLexer errors."""

class CharacterError(JsonLexerError): pass
class LiteralError(JsonLexerError): pass
class NumberError(JsonLexerError): pass
class StringEndError(JsonLexerError): pass
class UnexpectedCharacterError(JsonLexerError): pass

class JsonParserError(Exception):
    """Base exception for JsonParser errors."""

class ExtraColonError(JsonParserError): pass
class ExtraCommaError(JsonParserError): pass
class ExtraDataError(JsonParserError): pass
class InvalidKeyError(JsonParserError): pass
class LeadingCommaError(JsonParserError): pass
class MissingColonError(JsonParserError): pass
class MissingCommaError(JsonParserError): pass
class MissingKeyError(JsonParserError): pass
class MissingLeftBraceError(JsonParserError): pass
class MissingLeftBracketError(JsonParserError): pass
class MissingRightBraceError(JsonParserError): pass
class MissingRightBracketError(JsonParserError): pass
class MissingValueError(JsonParserError): pass
class TrailingCommaError(JsonParserError): pass
class UnexpectedColonError(JsonParserError): pass
class UnexpectedTokenError(JsonParserError): pass
