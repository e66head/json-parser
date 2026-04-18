"""
Parser module for the JSON parsing.

This module defines the JSON Parser class (JsonParser). It consumes a token stream produced by the JSON Lexer class and
converts it into Python objects.
"""

import logging

from .lexer import JsonLexer
from .errors import *  # pylint: disable=wildcard-import,unused-wildcard-import
from .stack import Stack
from .tokens import Token, TokenType

class JsonParser():
    """A simple JSON parser that uses the JSON lexer to parse JSON strings."""

    def __init__(self, json_str):
        self._lexer = JsonLexer(json_str)
        self._main_stack = Stack()
        self._open_stack = Stack()
        self._logger = logging.getLogger(__name__)

    def _handle_object(self):
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
        depth = self._main_stack.size() - index
        token_array = self._main_stack.pop_from_depth(depth)

        expected = TokenType.LBRACE  # Set the expectation that the first item in the tokens array is a left brace.
        dictionary = {}
        for token in token_array:

            # The following conditions are ordered to favor performance. The expected conditions are hit most often so
            # they are checked first, then the starting condition, then the terminal conditions, and finally the error
            # conditions.

            # EXPECTED CONDITIONS.
            if TokenType.STRING is expected and token.type == TokenType.STRING:
                key = token.value
                expected = TokenType.COLON

            elif TokenType.COLON is expected and token.type == TokenType.COLON:
                expected = TokenType.VALUE

            elif TokenType.VALUE is expected and token.is_value():
                dictionary[key] = token.value
                expected = TokenType.COMMA

            elif TokenType.COMMA is expected and token.type == TokenType.COMMA:
                expected = TokenType.STRING

            # STARTING CONDITIONS.
            elif TokenType.LBRACE is expected and token.type == TokenType.LBRACE:
                expected = TokenType.STRING

            # TERMINAL CONDITIONS.
            elif TokenType.COMMA is expected and token.type == TokenType.RBRACE:
                break # End of object.

            elif TokenType.STRING is expected and token.type == TokenType.RBRACE and not dictionary:
                break # End of empty object.

            # ERROR CONDITIONS.
            ###JDG TODO: Add specific malformed object errors. Until then, fall into the generic unexpected token error.
            else:
                raise UnexpectedTokenError(f"Unexpected token {token} in object. Expected {expected.name}.")

        self._main_stack.push(Token(TokenType.VALUE, dictionary, token_array[0].line))

    def _handle_array(self):
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
        depth = self._main_stack.size() - index
        token_array = self._main_stack.pop_from_depth(depth)

        expected = TokenType.LBRACKET
        array = []
        for token in token_array:

            # The following conditions are ordered to favor performance. The expected conditions are hit most often so
            # they are checked first, then the starting condition, then the terminal conditions, and finally the error
            # conditions.

            # EXPECTED CONDITIONS.
            if TokenType.VALUE is expected and token.is_value():
                array.append(token.value)
                expected = TokenType.COMMA

            elif TokenType.COMMA is expected and token.type == TokenType.COMMA:
                expected = TokenType.VALUE

            # STARTING CONDITIONS.
            elif TokenType.LBRACKET is expected and token.type == TokenType.LBRACKET:
                expected = TokenType.VALUE

            # TERMINAL CONDITIONS.
            elif TokenType.COMMA is expected and token.type == TokenType.RBRACKET:
                break # End of array.

            elif TokenType.VALUE is expected and token.type == TokenType.RBRACKET and not array:
                break # End of empty array.

            # ERROR CONDITIONS.
            elif TokenType.COMMA is expected and token.is_value():
                raise MissingCommaError("Unexpected value when expecting a comma")

            elif TokenType.VALUE is expected and token.type == TokenType.RBRACKET and array:
                raise TrailingCommaError("Unexpected trailing comma")

            elif TokenType.VALUE is expected and token.type == TokenType.COMMA and array:
                raise ExtraCommaError("Unexpected comma when expecting a value")

            elif TokenType.VALUE is expected and token.type == TokenType.COMMA and not array:
                raise LeadingCommaError("Unexpected leading comma")

            else:
                raise UnexpectedTokenError(f"Unexpected token {token} in array. Expected {expected.name}.")

        self._main_stack.push(Token(TokenType.VALUE, array, token_array[0].line))

    def _handle_opening_token(self):
        """Handles a token representing the opening brace or bracket of an object or array."""
        index = self._main_stack.size() - 1   # The index into the main stack (from the "bottom") of the opening token.
        token = self._main_stack.peek()       # This is the opening token that was just pushed onto the main stack.
        self._open_stack.push((index, token))

    def _handle_eof(self):
        """Handles cleaning up the stack when an end-of-file token is encountered."""

        self._main_stack.pop() # Pop the EOF token and throw it away.

        if self._main_stack.size() == 1 and self._main_stack.peek().is_value():
            return # Successfully parsed JSON value.

        if self._main_stack.is_empty():
            raise ExtraDataError("Unexpected end of JSON input. No data found.")

        if self._main_stack[0].type == TokenType.LBRACE:
            raise MissingRightBraceError("Unexpected end of object. Missing right brace.")

        if self._main_stack[0].type == TokenType.LBRACKET:
            raise MissingRightBracketError("Unexpected end of array. Missing right bracket.")

        raise ExtraDataError("Unexpected end of JSON input. Extra data found.")

    def parse(self):
        """Parses the JSON string and returns the corresponding Python object.
        
        This a shift-reduce parser that uses a stack to hold tokens. It unconditionally shifts tokens from the lexer
        onto the stack until a reduce operation is triggered by encountering one of three tokens: a left brace, a left
        bracket, or an end-of-file token. An array or object is reduced to a single token of special type "VALUE" that
        holds the corresponding Python type (list of dict) as its value.
        """

        for token in self._lexer.tokenize():
            self._logger.debug("Received token: %s", token)

            self._main_stack.push(token)

            match token.type:

                case TokenType.RBRACE:
                    self._handle_object()

                case TokenType.RBRACKET:
                    self._handle_array()

                case TokenType.LBRACE | TokenType.LBRACKET:
                    self._handle_opening_token()

                case TokenType.EOF:
                    self._handle_eof()

        token = self._main_stack.pop() # This should be the final token holding the fully parsed JSON value.

        return token.value
