"""
Lexer module for JSON parsing.

This module defines the JSON Lexer class (JsonLexer), which is responsible for converting a JSON string into a stream
of tokens that can be consumed by the JSON Parser (JsonParser).
"""

import logging
import re

from collections.abc import Generator

from .tokens import Token, TokenType
from .errors import UnexpectedCharacterError

class JsonLexer:
    """A lexer for JSON that converts a JSON string into a stream of tokens."""

    # JSON string regex helper components.
    JSON_VALID_ESCAPES  = r'\\["\\/bfnrt]'
    JSON_UNICODE_ESCAPE = r'\\u[0-9a-fA-F]{4}'
    JSON_VALID_LITERALS = r'[^"\\\0-\x1F]'

    # JSON number regex helper components.
    JSON_ONENINE_DIGITS = r'[1-9]\d*'
    JSON_EXPONENT       = r'[eE][+-]?\d+'

    # JSON string unescaping components.
    JSON_ESCAPE_RE = re.compile(fr'{JSON_VALID_ESCAPES}|{JSON_UNICODE_ESCAPE}')
    JSON_UNESCAPE_MAP = {
        '"':  '"',
        '\\': '\\',
        '/':  '/',
        'b':  '\b',
        'f':  '\f',
        'n':  '\n',
        'r':  '\r',
        't':  '\t'
    }

    @staticmethod
    def _json_unescape(match: re.Match) -> str:
        """Unescape a JSON string escape sequence that was matched by JSON_ESCAPE_RE."""
        esc = match.group(0) # match.group(0) must be an escape sequence matched by JSON_ESCAPE_RE.
        if esc.startswith(r'\u'): # Handle unicode escapes (that is, \uXXXX)
            return chr(int(esc[2:], 16))
        return JsonLexer.JSON_UNESCAPE_MAP[esc[1:]]

    TOKENS = {
        'LBRACE': {
            'regex':   r'\{',
            'handler': lambda s: s
        },

        'RBRACE': {
            'regex':   r'\}',
            'handler': lambda s: s
        },

        'LBRACKET': {
            'regex':   r'\[',
            'handler': lambda s: s
        },

        'RBRACKET': {
            'regex':   r'\]',
            'handler': lambda s: s
        },

        'COMMA': {
            'regex':   r',',
            'handler': lambda s: s
        },

        'COLON': {
            'regex':   r':',
            'handler': lambda s: s
        },

        'STRING': {
            'regex':   fr'''
                "                         # Opening double quote
                (?:                       # Group for content
                    {JSON_VALID_ESCAPES}  # 1. Escaped characters
                    |                     # OR
                    {JSON_UNICODE_ESCAPE} # 2. Unicode escape
                    |                     # OR
                    {JSON_VALID_LITERALS} # 3. Any other valid literal
                )*                        # GREEDY: consume as much as possible
                "                         # Closing double quote
            ''',
            'handler': lambda s: JsonLexer.JSON_ESCAPE_RE.sub(JsonLexer._json_unescape, s[1:-1])
        },

        'FLOAT': {
            'regex':   fr'''
                -?                              # Optional leading minus sign
                (?: 0 | {JSON_ONENINE_DIGITS} ) # Integer part: either a single 0 or 1-9 followed by digits
                (?:                             # Mandatory Fractional OR Exponent part:
                    \.\d+                       # . followed by one or more digits
                    (?: {JSON_EXPONENT} )?      # followed by an optional exponent
                    |                           # OR
                    {JSON_EXPONENT}             # a mandatory exponent (e.g., 1e10)
                )
            ''',
            'handler': float
        },

        'INTEGER': {
            'regex':   fr'''
                -?                        # Optional leading minus sign
                (?:                       # Integer part:
                    0                     #   Either a literal zero
                    |                     #   OR
                    {JSON_ONENINE_DIGITS} #   A non-zero digit followed by any number of digits
                )
            ''',
            'handler': int
        },

        'TRUE': {
            'regex':   r'true',
            'handler': lambda _: True
        },

        'FALSE': {
            'regex':   r'false',
            'handler': lambda _: False
        },

        'NULL': {
            'regex':   r'null',
            'handler': lambda _: None
        },

        'WHITESPACE': {
            'regex':   r'[\x20\t\r\n]+',
            'handler': lambda s: s
        },
    }

    # Create one regex from the individual token patterns so one match() call can match any token.
    TOKENS_RE = re.compile('|'.join(f'(?P<{key}>{value['regex']})' for key, value in TOKENS.items()), re.VERBOSE)

    def __init__(self, json_str):
        """Initialize the lexer with the given JSON string."""
        self._json_str = json_str
        self._index = 0
        self._logger = logging.getLogger(__name__)

    def _compute_line_column(self):
        """Compute the current line and column given the current index.
        
        Note! This is expensive! So, it should be called only when handling fatal exceptions."""
        line = self._json_str[:self._index].count('\n') + 1
        column = self._index - self._json_str[:self._index].rfind('\n') - 1
        return line, column

    def tokenize(self) -> Generator[Token, None, None]:
        """Yields tokens from the JSON string until EOF."""
        self._logger.info("Starting tokenization.")

        json_str_len = len(self._json_str)
        while self._index < json_str_len:

            match = self.TOKENS_RE.match(self._json_str, self._index)
            if not match:
                char = self._json_str[self._index]
                line, column = self._compute_line_column()
                raise UnexpectedCharacterError(f"Unexpected character '{char}' at {line}:{column}")

            # There was a match, so latch the type and value directly from the match object.
            raw_type = match.lastgroup
            raw_value = match.group(raw_type)

            # Save the start index before advancing the index past the matching token.
            start_index = self._index
            self._index = match.end()

            # Don't produce the whitespace token.
            if raw_type == 'WHITESPACE':
                continue

            # Resolve the token value and type and create the token itself.
            handler = self.TOKENS[raw_type]['handler']
            token_value = handler(raw_value)
            token_type = TokenType.NUMBER if raw_type in ('FLOAT', 'INTEGER') else TokenType[raw_type]
            token = Token(token_type, token_value, start_index)

            self._logger.debug("Scanned token: %s", token)
            yield token

        yield Token(TokenType.EOF, None, self._index)
