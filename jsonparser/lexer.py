"""
Lexer module for JSON parsing.

This module defines the JSON Lexer class (JsonLexer), which is responsible for converting a JSON string into a stream
of tokens that can be consumed by the JSON Parser (JsonParser).
"""

import logging

from collections.abc import Generator

from .tokens import Token, TokenType
from .errors import (
    LiteralError,
    StringEndError,
    CharacterError,
    NumberError,
    UnexpectedCharacterError
)

class JsonLexer:
    """A lexer for JSON that converts a JSON string into a stream of tokens."""

    ###JDG TODO: Consider making these instance variables so this lexer can be extended to support other lexers (like JSON5 in particular).
    JSON_MAX_CODEPOINT = 0x10FFFF
    JSON_MIN_CODEPOINT = 0x000020
    JSON_FORBIDDEN = {'"', '\\'}
    JSON_ESCAPES = {'"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}
    JSON_DECIMAL_DIGIT = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    JSON_ONENINE_DIGIT = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
    JSON_HEXIDECIMAL_DIGIT = {
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'a', 'b', 'c', 'd', 'e', 'f',
        'A', 'B', 'C', 'D', 'E', 'F'
    }
    JSON_WHITESPACE = {' ', '\t', '\n', '\r'}

    @staticmethod
    def is_forbidden(char) -> bool:
        """Determines if a character is forbidden in JSON strings."""
        forbidden = False
        if char in JsonLexer.JSON_FORBIDDEN:
            forbidden = True
        elif ord(char) < JsonLexer.JSON_MIN_CODEPOINT:
            forbidden = True
        elif ord(char) > JsonLexer.JSON_MAX_CODEPOINT:
            forbidden = True
        return forbidden

    @staticmethod
    def is_decimal(char) -> bool:
        """Determines if a character is a decimal digit."""
        return char in JsonLexer.JSON_DECIMAL_DIGIT

    @staticmethod
    def is_onenine(char) -> bool:
        """Determines if a character is a one-nine digit."""
        return char in JsonLexer.JSON_ONENINE_DIGIT

    @staticmethod
    def is_hex(char) -> bool:
        """Determines if a character is a hexadecimal digit."""
        return char in JsonLexer.JSON_HEXIDECIMAL_DIGIT

    @staticmethod
    def is_escapable(char) -> bool:
        """Determines if a character is escapable in JSON strings."""
        return char in JsonLexer.JSON_ESCAPES

    @staticmethod
    def is_whitespace(char) -> bool:
        """Determines if a character is whitespace in JSON."""
        return char in JsonLexer.JSON_WHITESPACE

    def __init__(self, json_str):

        self._json_str = json_str
        self._index = 0
        self._line_number = 1
        self._logger = logging.getLogger(__name__)

    def tokenize(self) -> Generator[Token, None, None]:
        """Yields tokens from the JSON string until EOF."""
        self._logger.info("Starting tokenization.")
        while True:
            self._consume_whitespace()

            if not self._peek():
                break

            token = self._get_next_token()
            self._logger.debug("Scanned token: %s", token)
            yield token

        eof_token = Token(TokenType.EOF, None, self._line_number)
        self._logger.info("Tokenization complete. Generated EOF token.")
        yield eof_token

    def _peek(self) -> str | None:
        if self._index >= len(self._json_str):
            return None
        return self._json_str[self._index]

    def _consume(self) -> str | None:
        char = self._peek()
        if char:
            if char == '\n':
                self._line_number += 1
            self._index += 1 # Advancing the index "consumes" the character.
        return char

    def _expect_sequence(self, expected: str):
        """Consumes the expected string from the input or raises an error."""
        for char in expected:
            actual = self._consume()
            if actual != char:
                raise LiteralError(f"Expected '{expected}' but found '{actual}' on line {self._line_number}")

    def _scan_true(self) -> Token:
        self._expect_sequence("true")
        return Token(TokenType.TRUE, True, self._line_number)

    def _scan_false(self) -> Token:
        self._expect_sequence("false")
        return Token(TokenType.FALSE, False, self._line_number)

    def _scan_null(self) -> Token:
        self._expect_sequence("null")
        return Token(TokenType.NULL, None, self._line_number)

    def _consume_whitespace(self):
        while (JsonLexer.is_whitespace(self._peek())):
            self._consume()

    def _scan_string(self) -> Token:
        """Scans a JSON string and returns the associated token."""

        self._consume()  # Consume the opening double quote (")

        chars = []
        while True:

            char = self._peek()
            match char:

                case None:
                    raise StringEndError(f"Unexpected end of input inside string on line {self._line_number}")

                case '"':
                    self._consume()  # Consume the closing double quote (")
                    break

                case '\\':
                    self._consume()  # Consume the escape (\)

                    # [Lookahead: Escape Sequences]
                    # Encountering a backslash triggers a lookahead to determine if the sequence is a single-character
                    # escape (like \n) or a fixed-width unicode sequence (like \uXXXX).
                    if self.is_escapable(escaped_char := self._consume()):
                        chars.append(JsonLexer.JSON_ESCAPES[escaped_char])

                    elif escaped_char == 'u':
                        # Handle \uXXXX hex escapes
                        hex_digits = "".join([self._consume() or "" for _ in range(4)])
                        if len(hex_digits) < 4:
                            raise CharacterError(f"Invalid unicode escape sequence on line {self._line_number}")
                        try:
                            chars.append(chr(int(hex_digits, 16)))
                        except ValueError as e:
                            raise CharacterError( f"Invalid hex in unicode escape on line {self._line_number}") from e

                    else:
                        raise CharacterError(f"Invalid escape sequence '\\{escaped_char}' on line {self._line_number}")

                case _ if self.is_forbidden(char):
                    raise CharacterError(f"Invalid character '{char}' in string on line {self._line_number}")

                case _:
                    chars.append(self._consume())

        return Token(TokenType.STRING, "".join(chars), self._line_number)

    def _scan_number(self) -> Token:
        """Scans a JSON number and returns its value as an int or float."""

        start_index = self._index

        # 1. Optional minus sign
        if self._peek() == '-':
            self._consume()

        # 2. Integer part
        char = self._peek()
        if char == '0':
            self._consume()
        elif self.is_onenine(char):
            self._consume()
            while (c := self._peek()) and self.is_decimal(c):
                self._consume()
        else:
            raise NumberError(f"Expected a digit at line {self._line_number}")

        # 3. Optional fractional part
        is_float = False
        if self._peek() == '.':
            is_float = True
            self._consume()
            if not (c := self._peek()) or not self.is_decimal(c):
                raise NumberError(f"Expected a digit after '.' at line {self._line_number}")
            while (c := self._peek()) and self.is_decimal(c):
                self._consume()

        # 4. Optional exponent part
        if (char := self._peek()) and char in "eE":
            is_float = True
            self._consume()
            if (c := self._peek()) and c in "+-":
                self._consume()
            if not (c := self._peek()) or not self.is_decimal(c):
                raise NumberError(f"Expected a digit in exponent at line {self._line_number}")
            while (c := self._peek()) and self.is_decimal(c):
                self._consume()

        # 5. Conversion
        num_str = self._json_str[start_index:self._index]
        try:
            val = float(num_str) if is_float else int(num_str)
            return Token(TokenType.NUMBER, val, self._line_number)
        except ValueError as e:
            raise NumberError(f"Invalid number format '{num_str}' at line {self._line_number}") from e

    def _scan_lbrace(self) -> Token:
        self._consume()
        return Token(TokenType.LBRACE, "{", self._line_number)

    def _scan_rbrace(self) -> Token:
        self._consume()
        return Token(TokenType.RBRACE, "}", self._line_number)

    def _scan_lbracket(self) -> Token:
        self._consume()
        return Token(TokenType.LBRACKET, "[", self._line_number)

    def _scan_rbracket(self) -> Token:
        self._consume()
        return Token(TokenType.RBRACKET, "]", self._line_number)

    def _scan_comma(self) -> Token:
        self._consume()
        return Token(TokenType.COMMA, ",", self._line_number)

    def _scan_colon(self) -> Token:
        self._consume()
        return Token(TokenType.COLON, ":", self._line_number)

    def _get_next_token(self) -> Token:
        """Identifies and returns the next token from the character stream."""

        char = self._peek()
        match char:

            case '{':
                token = self._scan_lbrace()

            case '}':
                token = self._scan_rbrace()

            case '[':
                token = self._scan_lbracket()

            case ']':
                token = self._scan_rbracket()

            case ',':
                token = self._scan_comma()

            case ':':
                token = self._scan_colon()

            case '"':
                token = self._scan_string()

            case 't':
                token = self._scan_true()

            case 'f':
                token = self._scan_false()

            case 'n':
                token = self._scan_null()

            case '-' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9':
                token = self._scan_number()

            case _:
                raise UnexpectedCharacterError(f"Unexpected character '{char}' at line {self._line_number}")

        return token
