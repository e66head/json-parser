"""
Parser module for the JSON parsing.

This module defines the JSON Parser class (JsonParser). It consumes a token stream produced by the JSON Lexer class and
converts it into Python objects.
"""

import logging

from .lexer import JsonLexer
from .errors import (
    ExtraColonError,
    ExtraCommaError,
    ExtraDataError,
    InvalidKeyError,
    LeadingCommaError,
    MissingColonError,
    MissingCommaError,
    MissingKeyError,
    MissingLeftBraceError,
    MissingLeftBracketError,
    MissingRightBraceError,
    MissingRightBracketError,
    MissingValueError,
    TrailingCommaError,
    UnexpectedColonError,
    UnexpectedTokenError,
)
from .stack import Stack
from .tokens import Token, TokenType

class JsonParser():
    """A simple JSON parser that uses the JSON lexer to parse JSON strings."""

    def __init__(self, json_str):
        self._lexer = JsonLexer(json_str)

        # The main stack holds tokens shifted in from the lexer and aggregated values reduced from objects and arrays.
        self._main_stack = Stack()

        # The open_stack stores the absolute index of the opening container token (that is, '{' or '[') currently on
        # the main_stack. This allows O(1) lookups of matching containers and O(1) calculation of how many tokens to
        # pop during a reduction, bypassing the need for a linear scan-back through the main stack to find the opening
        # container token.
        self._open_stack = Stack()

        self._logger = logging.getLogger(__name__)

    def _handle_object_reduction(self):
        """Handles the construction of the dictionary from the JSON object when a right brace token is encountered."""

        # Get the the most recent opening token from the open stack. This should be the left brace corresponding to the
        # right brace that triggered this reduce operation.
        try:
            index, token = self._open_stack.pop()
        except IndexError as exc:
            raise MissingLeftBraceError("Unexpected right brace without matching left brace.") from exc

        if token.type != TokenType.LBRACE:
            raise MissingLeftBraceError(f"Unexpected token {token} when expecting a left brace.")

        # Pop everything off the main stack in FIFO order from the first left brace to the top of the stack.
        token_array = self._main_stack.pop_from_index(index)

        # The 'expected' variable drives the validation logic while iterating through the tokens of a JSON object. The
        # initial state for a JSON object is to expect an opening left brace.
        expected = TokenType.LBRACE
        dictionary = {}
        for token in token_array:

            # Conditions are ordered to favor performance (most common first).

            # EXPECTED CONDITIONS.

            if TokenType.STRING is expected and token.type is TokenType.STRING:
                key = token.value
                expected = TokenType.COLON

            elif TokenType.COLON is expected and token.type is TokenType.COLON:
                expected = TokenType.VALUE

            elif TokenType.VALUE is expected and token.is_value():
                dictionary[key] = token.value
                expected = TokenType.COMMA

            elif TokenType.COMMA is expected and token.type is TokenType.COMMA:
                expected = TokenType.STRING

            # STARTING CONDITIONS.

            elif TokenType.LBRACE is expected and token.type is TokenType.LBRACE:
                expected = TokenType.STRING

            # TERMINAL CONDITIONS.

            elif TokenType.COMMA is expected and token.type is TokenType.RBRACE:
                break # End of object.

            elif TokenType.STRING is expected and token.type is TokenType.RBRACE and not dictionary:
                break # End of empty object.

            # ERROR CONDITIONS.

            # {<string> <value>}
            elif TokenType.COLON is expected and token.is_value():
                raise MissingColonError("Missing colon between key and value.")

            # {<string>: ,}
            elif TokenType.VALUE is expected and token.type is TokenType.COMMA:
                raise MissingValueError("Unexpected comma when expecting a value.")

            # {<string>:: <value>}
            elif TokenType.VALUE is expected and token.type is TokenType.COLON:
                raise ExtraColonError("Unexpected double colon")

            # {: <value>}
            elif TokenType.STRING is expected and token.type is TokenType.COLON:
                raise MissingKeyError("Unexpected colon when expecting a string key.")

            # {<string>: <value>,,<string>: <value>}
            elif TokenType.STRING is expected and token.type is TokenType.COMMA and dictionary:
                raise ExtraCommaError("Unexpected extra comma in object.")

            # {, <string>: <value>}
            elif TokenType.STRING is expected and token.type is TokenType.COMMA and not dictionary:
                raise LeadingCommaError("Unexpected leading comma in object.")

            # {<value>: <value>}
            elif TokenType.STRING is expected and token.type is not TokenType.STRING:
                raise InvalidKeyError(f"Invalid key type {token.type.name}. Keys must be strings.")

            # {<string>: <value> <string>: <value>}
            elif TokenType.COMMA is expected and token.is_value():
                raise MissingCommaError("Missing comma between object members.")

            else:
                raise UnexpectedTokenError(f"Unexpected token {token} in object. Expected {expected.name}.")

        # Replace the entire array sequence on the main stack with a list represented as a single VALUE token.
        self._main_stack.push(Token(TokenType.VALUE, dictionary, token_array[0].line))

    def _handle_array_reduction(self):
        """Handles the construction of the list from the JSON array when a right bracket token is encountered."""

        # Get the the most recent opening token from the open stack. This should be the left bracket corresponding to
        # the right bracket that triggered this reduce operation.
        try:
            index, token = self._open_stack.pop()
        except IndexError as exc:
            raise MissingLeftBracketError("Unexpected right bracket without matching left bracket.") from exc

        if token.type != TokenType.LBRACKET:
            raise MissingLeftBracketError(f"Unexpected token {token} when expecting a left bracket.")

        # Pop everything off the main stack in FIFO order from the first left bracket to the top of the stack.
        token_array = self._main_stack.pop_from_index(index)

        # The 'expected' variable drives the validation logic while iterating through the tokens of a JSON array. The
        # starting condition for a JSON array is to expect an opening left bracket.
        expected = TokenType.LBRACKET
        array = []
        for token in token_array:

            # The following conditions are ordered to favor performance.

            # EXPECTED CONDITIONS.
            if TokenType.VALUE is expected and token.is_value():
                array.append(token.value)
                expected = TokenType.COMMA

            elif TokenType.COMMA is expected and token.type is TokenType.COMMA:
                expected = TokenType.VALUE

            # STARTING CONDITIONS.
            elif TokenType.LBRACKET is expected and token.type is TokenType.LBRACKET:
                expected = TokenType.VALUE

            # TERMINAL CONDITIONS.
            elif TokenType.COMMA is expected and token.type is TokenType.RBRACKET:
                break # End of array.

            elif TokenType.VALUE is expected and token.type is TokenType.RBRACKET and not array:
                break # End of empty array.

            # ERROR CONDITIONS.

            # [<value> <value>]
            elif TokenType.COMMA is expected and token.is_value():
                raise MissingCommaError("Unexpected value when expecting a comma")

            # [<value>,]
            elif TokenType.VALUE is expected and token.type is TokenType.RBRACKET and array:
                raise TrailingCommaError("Unexpected trailing comma")

            # [<value>,,<value>]
            elif TokenType.VALUE is expected and token.type is TokenType.COMMA and array:
                raise ExtraCommaError("Unexpected comma when expecting a value")

            # [,<value>]
            elif TokenType.VALUE is expected and token.type is TokenType.COMMA and not array:
                raise LeadingCommaError("Unexpected leading comma")

            # [<string>: <value>]
            elif token.type is TokenType.COLON:
                raise UnexpectedColonError("Unexpected colon in array.")

            else:
                raise UnexpectedTokenError(f"Unexpected token {token} in array. Expected {expected.name}.")

        # Replace the entire sequence on the main stack with the single reduced VALUE token.
        self._main_stack.push(Token(TokenType.VALUE, array, token_array[0].line))

    def _handle_opening_token(self):
        """Handles a token representing the opening brace or bracket of an object or array."""
        # Record the position of the opening token so it doesn't require scanning back to find it during reduction.
        index = self._main_stack.size() - 1
        token = self._main_stack.peek()
        self._open_stack.push((index, token))

    def _handle_eof(self):
        """Handles cleaning up the stack when an end-of-file token is encountered."""

        self._main_stack.pop() # Pop the EOF token.

        # After popping the EOF token, there should be one item remaining on the stack representing valid JSON.
        if self._main_stack.size() == 1 and self._main_stack.peek().is_value():
            return

        if self._main_stack.is_empty():
            raise ExtraDataError("Unexpected end of JSON input. No data found.")

        # Check for unclosed containers.
        if self._main_stack[0].type == TokenType.LBRACE:
            raise MissingRightBraceError("Unexpected end of object. Missing right brace.")

        if self._main_stack[0].type == TokenType.LBRACKET:
            raise MissingRightBracketError("Unexpected end of array. Missing right bracket.")

        raise ExtraDataError("Unexpected end of JSON input. Extra data found.")

    def parse(self):
        """Parses the JSON string and returns the corresponding Python object.

        This is a shift-reduce parser that uses a stack to hold tokens. It unconditionally shifts tokens from the lexer
        onto the stack until a reduce operation is triggered by encountering a terminal token ( } , ] , or EOF).
        """

        for token in self._lexer.tokenize():
            self._logger.debug("Received token: %s", token)

            self._main_stack.push(token)

            match token.type:

                case TokenType.RBRACE:
                    self._handle_object_reduction()

                case TokenType.RBRACKET:
                    self._handle_array_reduction()

                case TokenType.LBRACE | TokenType.LBRACKET:
                    self._handle_opening_token()

                case TokenType.EOF:
                    self._handle_eof()

        # The final pop yields the root Python object.
        token = self._main_stack.pop()

        return token.value
