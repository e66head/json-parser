"""
Lexer module for JSON parsing.

This module defines the JSON Lexer class (JsonLexer), which is responsible for converting a JSON string into a stream
of tokens that can be consumed by the JSON Parser (JsonParser).
"""

import logging
import re

from collections.abc import Generator
from enum import Enum, auto

from .tokens import Token, TokenType
from .errors import UnexpectedCharacterError

class JsonDialect(Enum):
    """Defines different dialects of JSON that the lexer can support."""
    JSON = auto()  # Strict JSON as defined by RFC 8259.
    JSONC = auto() # JSON with comments (JSONC).
    JSON5 = auto() # JSON5, an even more permissive and expressive JSON dialect.

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

    # JSON token definitions. Each token is defined by a regex pattern and a tokenizer function to create the token.
    WHITESPACE_TOKEN = {
        'WHITESPACE': {
            'regex':   r'[\x20\t\r\n]+', # Any sequence of spaces, tabs, carriage returns, or line feeds.
            'tokenizer': None # A token is not produced for whitespace, so the tokenizer is None.
        }
    }
    LBRACE_TOKEN = {
        'LBRACE': {
            'regex':   r'\{',
            'tokenizer': lambda s: s
        }
    }
    RBRACE_TOKEN = {
        'RBRACE': {
            'regex':   r'\}',
            'tokenizer': lambda s: s
        }
    }
    LBRACKET_TOKEN = {
        'LBRACKET': {
            'regex':   r'\[',
            'tokenizer': lambda s: s
        }
    }
    RBRACKET_TOKEN = {
        'RBRACKET': {
            'regex':   r'\]',
            'tokenizer': lambda s: s
        }
    }
    COMMA_TOKEN = {
        'COMMA': {
            'regex':   r',',
            'tokenizer': lambda s: s
        }
    }
    COLON_TOKEN = {
        'COLON': {
            'regex':   r':',
            'tokenizer': lambda s: s
        }
    }
    STRING_TOKEN = {
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
            'tokenizer': lambda s: JsonLexer.JSON_ESCAPE_RE.sub(JsonLexer._json_unescape, s[1:-1])
        }
    }
    FLOAT_TOKEN = {
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
            'tokenizer': float
        }
    }
    INTEGER_TOKEN = {
        'INTEGER': {
            'regex':   fr'''
                -?                        # Optional leading minus sign
                (?:                       # Integer part:
                    0                     #   Either a literal zero
                    |                     #   OR
                    {JSON_ONENINE_DIGITS} #   A non-zero digit followed by any number of digits
                )
            ''',
            'tokenizer': int
        }
    }
    TRUE_TOKEN = {
        'TRUE': {
            'regex':   r'true',
            'tokenizer': lambda _: True
        }
    }
    FALSE_TOKEN = {
        'FALSE': {
            'regex':   r'false',
            'tokenizer': lambda _: False
        }
    }
    NULL_TOKEN = {
        'NULL': {
            'regex':   r'null',
            'tokenizer': lambda _: None
        }
    }
    LINE_COMMENT_TOKEN = {
        'LINE_COMMENT': {
            'regex':   r'//[^\r\n]*', # A double slash followed by anything that's NOT a carriage return or line feed.
            'tokenizer': None # A token is not produced for line comments, so the tokenizer is None.
        }
    }
    BLOCK_COMMENT_TOKEN = {
        'BLOCK_COMMENT': {
            'regex':   r'/\*[\s\S]*?\*/', # A slash+splat, followed by anything, followed by a splat+slash.
            'tokenizer': None # A token is not produced for block comments, so the tokenizer is None.
        }
    }

    # Group tokens into categories for easier handling in the parser.
    WHITESPACE_TOKENS = {
        **WHITESPACE_TOKEN,
    }
    STRUCTURAL_TOKENS = {
        **LBRACE_TOKEN,
        **RBRACE_TOKEN,
        **LBRACKET_TOKEN,
        **RBRACKET_TOKEN,
        **COMMA_TOKEN,
        **COLON_TOKEN,
    }
    VALUE_TOKENS = {
        **STRING_TOKEN,
        **FLOAT_TOKEN, # Important! Define FLOAT before INTEGER so that floats don't get matched as integers.
        **INTEGER_TOKEN,
        **TRUE_TOKEN,
        **FALSE_TOKEN,
        **NULL_TOKEN,
    }
    COMMENT_TOKENS = {
        **LINE_COMMENT_TOKEN,
        **BLOCK_COMMENT_TOKEN,
    }

    # RFC 8259 standard (the JSON specification)
    TOKENS_JSON = {
        **WHITESPACE_TOKENS,
        **STRUCTURAL_TOKENS,
        **VALUE_TOKENS,
    }

    # JSON with comments (JSONC)
    TOKENS_JSONC = {
        **TOKENS_JSON,
        **COMMENT_TOKENS,
    }

    # create a static function that will generate a compiled regular expression from one of these tokens dictionaries.
    @staticmethod
    def _compile_tokens_regex(tokens_dict):
        """Compile a regular expression that can match any token defined in the given token dictionary."""
        combined_regex = '|'.join(f'(?P<{name}>{info["regex"]})' for name, info in tokens_dict.items())
        compiled_regex = re.compile(combined_regex, re.VERBOSE)
        return compiled_regex

    TOKENS_MAP_RE = {
        JsonDialect.JSON: _compile_tokens_regex(TOKENS_JSON),
        JsonDialect.JSONC: _compile_tokens_regex(TOKENS_JSONC),
        # JsonDialect.JSON5: _compile_tokens_regex(TOKENS_JSON5), # TODO: Implement JSON5 support.
    }

    TOKENS_MAP = {
        JsonDialect.JSON: TOKENS_JSON,
        JsonDialect.JSONC: TOKENS_JSONC,
        # JsonDialect.JSON5: TOKENS_JSON5, # TODO: Implement JSON5 support.
    }

    def __init__(self, json_str, dialect=JsonDialect.JSON):
        """Initialize the lexer with the given JSON string."""
        self._json_str = json_str
        self._index = 0
        self._logger = logging.getLogger(__name__)
        self.tokens_re = self.TOKENS_MAP_RE[dialect]
        self.tokens = self.TOKENS_MAP[dialect]

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

            match = self.tokens_re.match(self._json_str, self._index)
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

            # Don't produce tokens for whitespace or comments.
            if raw_type in ('WHITESPACE', 'LINE_COMMENT', 'BLOCK_COMMENT'):
                continue

            # Resolve the token value and token type and create the token itself.
            tokenizer = self.tokens[raw_type]['tokenizer']
            token_value = tokenizer(raw_value)
            token_type = TokenType.NUMBER if raw_type in ('FLOAT', 'INTEGER') else TokenType[raw_type]
            token = Token(token_type, token_value, start_index)

            self._logger.debug("Scanned token: %s", token)
            yield token

        yield Token(TokenType.EOF, None, self._index)
