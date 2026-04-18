
###JDG TODO: Fix these pylint errors.
# pylint: disable=missing-module-docstring    # This file needs a docstring.
# pylint: disable=unused-import               # This is due to the import of tokens.
# pylint: disable=missing-class-docstring     # Classes should have docstrings.
# pylint: disable=missing-function-docstring  # Functions should have docstrings.
# pylint: disable=raise-missing-from          # Exceptions are not being raised properly and should be fixed.
# pylint: disable=unused-variable             # This is due to raising exceptions as "e" but not using "e".

from .tokens import Token
from .errors import * # pylint: disable=wildcard-import,unused-wildcard-import

class JsonLexer:

    ###JDG TODO: Consider making these instance variables so this lexer can be extended to support other lexers (like JSON5 in particular).
    JSON_MAX_CODEPOINT = 0x10FFFF
    JSON_MIN_CODEPOINT = 0x000020
    JSON_FORBIDDEN = {'"', '\\'}
    JSON_ESCAPABLE = {'"', '\\', '/', 'b', 'f', 'n', 'r', 't'}
    JSON_DECIMAL_DIGIT = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    JSON_ONENINE_DIGIT = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
    JSON_HEXIDECIMAL_DIGIT = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F'}

    @staticmethod
    def is_forbidden(char):
        forbidden = False
        if char in JsonLexer.JSON_FORBIDDEN:
            forbidden = True
        elif ord(char) < JsonLexer.JSON_MIN_CODEPOINT:
            forbidden = True
        elif ord(char) > JsonLexer.JSON_MAX_CODEPOINT:
            forbidden = True
        return forbidden

    @staticmethod
    def is_decimal(char):
        return char in JsonLexer.JSON_DECIMAL_DIGIT

    @staticmethod
    def is_hex(char):
        return char in JsonLexer.JSON_HEXIDECIMAL_DIGIT

    @staticmethod
    def is_escapable(char):
        return char in JsonLexer.JSON_ESCAPABLE

    def __init__(self, json_str, callbacks=None, debug=False):

        self._json_str = json_str
        self._index = 0
        self._line_number = 1
        self._callbacks = {
            "on_parse_start": [],
            "on_parse_end": [],
            "on_object_start": [],
            "on_object_end": [],
            "on_members_start": [],
            "on_members_end": [],
            "on_member_start": [],
            "on_member_end": [],
            "on_array_start": [],
            "on_array_end": [],
            "on_whitespace_start": [],
            "on_whitespace_end": [],
            "on_string_start": [],
            "on_string_end": [],
            "on_characters_start": [],
            "on_characters_end": [],
            "on_character_start": [],
            "on_character_end": [],
            "on_number_start": [],
            "on_number_end": [],
            "on_integer_start": [],
            "on_integer_end": [],
            "on_fraction_start": [],
            "on_fraction_end": [],
            "on_exponent_start": [],
            "on_exponent_end": [],
            "on_onenine_start": [],
            "on_onenine_end": [],
            "on_digits_start": [],
            "on_digits_end": [],
            "on_digit_start": [],
            "on_digit_end": [],
            "on_true_start": [],
            "on_true_end": [],
            "on_false_start": [],
            "on_false_end": [],
            "on_null_start": [],
            "on_null_end": [],
            "on_key_start": [],
            "on_key_end": [],
            "on_value_start": [],
            "on_value_end": [],
            "on_elements_start": [],
            "on_elements_end": [],
            "on_element_start": [],
            "on_element_end": [],
            "on_escape_start": [],
            "on_escape_end": [],
            "on_literal_start": [],
            "on_literal_end": [],
        }

        if debug:
            for event in self._callbacks: # pylint: disable=consider-using-dict-items
                self._callbacks[event].append(self._debug_event_handler)

        self.add_callbacks(callbacks)

    ###JDG TODO: Rename this to "tokenize". It should eventually yield token objects instead of pushing strings via callbacks.
    ###JDG TODO: In the meantime, change the parse functions to push token objects.
    def parse(self):

        self._call_callbacks("on_parse_start", string="", line_number=self._line_number)
        element_str = self._parse_element()
        self._call_callbacks("on_parse_end", string="", line_number=self._line_number)

        if char := self._get_current_chars(1):
            raise EndOfJsonError(f"Unexpected character ({char}) after JSON parsing completed on line {self._line_number}")

        return element_str

    def add_callback(self, event, callback):
        if isinstance(callback, list):
            for c in callback:
                self.add_callback(event, c)
        else:
            try:
                self._callbacks[event].append(callback)
            except JsonKeyError as e:
                raise UnknownEventError(f"Unknown event ({event}). Unable to add callback.") from e

    def remove_callback(self, event, callback):
        try:
            self._callbacks[event].remove(callback)
        except JsonKeyError as e:
            raise UnknownEventError(f"Unknown event ({event}). Unable to remove callback.") from e

    def add_callbacks(self, callbacks):
        if isinstance(callbacks, dict):
            for event, callback in callbacks.items():
                self.add_callback(event, callback)
        else:
            raise TypeError("Callbacks must be provided as a dictionary with event names as keys and callback functions as values.")

    def remove_callbacks(self, callbacks):
        for event, callback in callbacks.items():
            self.remove_callback(event, callback)

    def _debug_event_handler(self, event, string, line_number):
        if event in ["on_string_end", "on_number_end", "on_true_end", "on_false_end", "on_null_end", "on_key_end", "on_literal_end"]:
            print(f"DEBUG: event:{event:20} string:{string} line_number:{line_number}")
        else:
            print(f"DEBUG: event:{event:20} line_number:{line_number}")

    def _call_callbacks(self, event=None, string=None, line_number=None):

        if event not in self._callbacks:
            raise UnknownEventError(f"Unknown event ({event}). Unable to call callbacks.")

        for callback in self._callbacks[event]:
            try:
                callback(event=event, string=string, line_number=line_number)
            except Exception as e:
                raise UnknownEventError(f"Error calling callback for event '{event}'") from e

    def _increment_index(self, increment):

        self._index += increment

    def _get_current_chars(self, num_chars):

        try:
            return self._json_str[self._index:self._index + num_chars]
        except IndexError:
            # Note that if this exception isn't handled properly, it means this parser can't handle streaming. Streaming would allow parsing to resume
            # when more data becomes available. TODO: Handle this exception properly to allow for streaming.
            raise EndOfJsonError(f"Unexpected end of JSON string while trying to read {num_chars} characters on line {self._line_number}")

    ###JDG TODO: Convert these parsers to use the Token class and return/push tokens instead of strings. This will allow for better handling of the JSON
    # structure and types.

    def _parse_value(self):

        parsers = [
            (self._parse_object, ObjectStartError),
            (self._parse_array,  ArrayStartError),
            (self._parse_string, StringStartError),
            (self._parse_number, NumberError),
            (self._parse_true,   TrueError),
            (self._parse_false,  FalseError),
            (self._parse_null,   NullError),
        ]

        self._call_callbacks("on_value_start", string="", line_number=self._line_number)
        for parser, exception in parsers:
            #print(f"{parser.__name__=} {self._line_number=}")  # DEBUG
            try:
                value = parser()
                self._call_callbacks("on_value_end", string="", line_number=self._line_number)
                return value
            except exception:
                continue

        raise ValueError(f"No valid JSON value could be found on line {self._line_number}")

    def _parse_object(self):

        try:
            self._parse_literal("{")
            self._call_callbacks("on_object_start", string="", line_number=self._line_number)
        except LiteralError:
            raise ObjectStartError(f"Expected '{{' to start an object on line {self._line_number}")

        try:
            members_str = self._parse_members()
        except Exception as e:
            raise ObjectMembersError(f"Error parsing object members on line {self._line_number}") from e

        try:
            self._parse_literal("}")
        except LiteralError:
            raise ObjectEndError(f"Expected '}}' to end an object on line {self._line_number}")

        ###JDG TODO: Consider whether its even useful to return anything here. It's not even currently used and the callbacks will handle the object start and
        # end events.
        self._call_callbacks("on_object_end", string="}", line_number=self._line_number)
        return f"{{{members_str}}}"

    def _parse_members(self):

        self._call_callbacks("on_members_start", string="", line_number=self._line_number)

        members = []

        while True:
            member_str = self._parse_member()
            members.append(member_str)
            try:
                self._parse_literal(",")
            except LiteralError:
                break # No comma indicates the end of the members list, so break the loop.

        self._call_callbacks("on_members_end", string="", line_number=self._line_number)

        return ', '.join(members)

    def _parse_member(self):

        self._call_callbacks("on_member_start", string="", line_number=self._line_number)

        key_str = self._parse_key()
        self._parse_literal(":")
        element_str = self._parse_element()

        self._call_callbacks("on_member_end", string="", line_number=self._line_number)

        return f"{key_str}: {element_str}"

    def _parse_key(self):

        self._call_callbacks("on_key_start", string="", line_number=self._line_number)

        self._parse_whitespace()
        string_str = self._parse_string()
        self._parse_whitespace()

        self._call_callbacks("on_key_end", string=string_str, line_number=self._line_number)

        return string_str

    def _parse_array(self):

        try:
            self._parse_literal("[")
            self._call_callbacks("on_array_start", string="", line_number=self._line_number)
        except LiteralError:
            raise ArrayStartError(f"Expected '[' to start an array on line {self._line_number}")

        try:
            elements_str = self._parse_elements()
        except Exception as e:
            raise ArrayElementsError(f"Error parsing array elements on line {self._line_number}") from e

        try:
            self._parse_literal("]")
        except LiteralError:
            raise ArrayEndError(f"Expected ']' to end an array on line {self._line_number}")

        self._call_callbacks("on_array_end", string="]", line_number=self._line_number)
        return f"[{elements_str}]"

    def _parse_elements(self):

        self._call_callbacks("on_elements_start", string="", line_number=self._line_number)

        elements = []

        while True:
            element_str = self._parse_element()
            elements.append(element_str)
            try:
                self._parse_literal(",")
            except LiteralError:
                break # No comma indicates the end of the elements list, so break the loop.

        self._call_callbacks("on_elements_end", string="", line_number=self._line_number)

        return ', '.join(elements)

    def _parse_element(self):

        self._call_callbacks("on_element_start", string="", line_number=self._line_number)

        self._parse_whitespace()
        value_str = self._parse_value()
        self._parse_whitespace()

        self._call_callbacks("on_element_end", string="", line_number=self._line_number)

        return value_str

    ###JDG TODO: The lexer should produce tokens and the string itself is the token. So, should this fully parse and return the string to avoid re-parsing it
    # later?
    def _parse_string(self):

        self._call_callbacks("on_string_start", string="", line_number=self._line_number)

        try:
            self._parse_literal('"')
        except LiteralError:
            raise StringStartError(f"Expected '\"' to start a string on line {self._line_number}")

        try:
            characters_str = self._parse_characters()
        except Exception as e:
            raise StringCharactersError(f"Error parsing string characters on line {self._line_number}") from e

        try:
            self._parse_literal('"')
        except LiteralError:
            raise StringEndError(f"Expected '\"' to end a string on line {self._line_number}")

        string = f'"{characters_str}"'

        self._call_callbacks("on_string_end", string=string, line_number=self._line_number)
        return string

    def _parse_characters(self):

        self._call_callbacks("on_characters_start", string="", line_number=self._line_number)

        characters = []

        while character_str := self._parse_character():
            characters.append(character_str)

        self._call_callbacks("on_characters_end", string=characters, line_number=self._line_number)

        return "".join(characters)

    def _parse_character(self):

        self._call_callbacks("on_character_start", string="", line_number=self._line_number)

        char = self._get_current_chars(1)

        # If the character is the double quote, don't parse it. In particular, don't advance the JSON string index. The double quote character here indicates
        # the end of a string that's being parsed by the callers up the stack.
        if char == '"':
            char = ''

        # If the character is the escape, parse the following escaped characters.
        elif char == '\\':
            self._increment_index(1)
            try:
                escaped = self._parse_escape()
            except EscapeError as e:
                raise CharacterError(f"Invalid escape sequence on line {self._line_number}") from e
            char = f"\\{escaped}"

        # Character is not special, so just advance the index and fall into the return.
        else:
            self._increment_index(1)

        self._call_callbacks("on_character_end", string=char, line_number=self._line_number)

        return char

    def _parse_escape(self):

        self._call_callbacks("on_escape_start", string="", line_number=self._line_number)
        # Try to parse the escape character as a literal first.
        for escape in JsonLexer.JSON_ESCAPABLE:
            try:
                escape_literal = self._parse_literal(escape)
                self._call_callbacks("on_escape_end", string=escape_literal, line_number=self._line_number)
                return escape_literal
            except LiteralError:
                continue

        escaped_char = self._get_current_chars(1)
        if escaped_char != 'u':
            raise EscapeError(f"Expected hex escape character 'u' but found '{escaped_char}' at line {self._line_number}")

        escaped_str = self._get_current_chars(5)  # Get the 'u' character and the next 4 characters.
        escaped_hex = escaped_str[1:]  # Skip the 'u' character and get the next 4 characters.
        if len(escaped_hex) != 4 or not all(JsonLexer.is_hex(c) for c in escaped_hex):
            raise EscapeError(f"Expected four hex digits but found '{escaped_hex}' at line {self._line_number}")

        self._increment_index(5)
        self._call_callbacks("on_escape_end", string=escaped_str, line_number=self._line_number)
        return escaped_str

    def _parse_number(self):

        self._call_callbacks("on_number_start", string="", line_number=self._line_number)

        try:
            integer_str = self._parse_integer()
        except IntegerError as e:
            raise NumberError(f"Invalid integer part of number on line {self._line_number}") from e

        try:
            fraction_str = self._parse_fraction()
        except FractionError:
            fraction_str = ""

        try:
            exponent_str = self._parse_exponent()
        except ExponentError:
            exponent_str = ""

        number_str = f"{integer_str}{fraction_str}{exponent_str}"
        self._call_callbacks("on_number_end", string=number_str, line_number=self._line_number)
        return number_str

    def _parse_integer(self):

        self._call_callbacks("on_integer_start", string="", line_number=self._line_number)

        integer_str = ""

        try:
            integer_str += self._parse_literal("-")
        except LiteralError:
            pass

        try:
            integer_str += self._parse_literal("0")
            self._call_callbacks("on_integer_end", string=integer_str, line_number=self._line_number)
            return integer_str
        except LiteralError:
            pass

        try:
            integer_str += self._parse_onenine()
        except OneNineError as e:
            raise IntegerError(f"Expected a digit from 1 to 9 on line {self._line_number}") from e

        try:
            integer_str += self._parse_digits()
        except DigitsError as e:
            pass

        self._call_callbacks("on_integer_end", string=integer_str, line_number=self._line_number)
        return integer_str

    def _parse_fraction(self):

        self._call_callbacks("on_fraction_start", string="", line_number=self._line_number)
        digits_str = ""

        try:
            digits_str = self._parse_literal(".")
        except LiteralError:
            self._call_callbacks("on_fraction_end", string=digits_str, line_number=self._line_number)
            return digits_str

        try:
            digits_str += self._parse_digits()
            self._call_callbacks("on_fraction_end", string=digits_str, line_number=self._line_number)
            return digits_str
        except DigitsError as e:
            raise FractionError(f"Expected digits after decimal point on line {self._line_number}") from e

    def _parse_exponent(self):

        self._call_callbacks("on_exponent_start", string="", line_number=self._line_number)

        try:
            exponent_str = self._parse_literal("e")
        except LiteralError:
            try:
                exponent_str = self._parse_literal("E")
            except LiteralError:
                raise ExponentError(f"Expected 'e' or 'E' for exponent on line {self._line_number}")

        try:
            sign_str = self._parse_literal("-")
        except LiteralError:
            try:
                sign_str = self._parse_literal("+")
            except LiteralError:
                sign_str = ""

        try:
            digits_str = self._parse_digits()
        except DigitsError as e:
            raise ExponentError(f"Expected digits after exponent sign on line {self._line_number}") from e

        exponent_str = f"{exponent_str}{sign_str}{digits_str}"
        self._call_callbacks("on_exponent_end", string=exponent_str, line_number=self._line_number)
        return exponent_str

    def _parse_onenine(self):

        self._call_callbacks("on_onenine_start", string="", line_number=self._line_number)

        try:
            onenine_str = self._get_current_chars(1)
        except IndexError:
            raise OneNineIndexError(f"Unexpected end of JSON string while expecting a digit from 1 to 9 on line {self._line_number}")

        if onenine_str not in JsonLexer.JSON_ONENINE_DIGIT:
            raise OneNineError(f"Expected a digit from 1 to 9 but found '{onenine_str}' on line {self._line_number}")

        self._increment_index(1)
        self._call_callbacks("on_onenine_end", string=onenine_str, line_number=self._line_number)
        return onenine_str

    def _parse_digits(self):

        self._call_callbacks("on_digits_start", string="", line_number=self._line_number)

        try:
            digits_str = self._parse_digit()
        except DigitError as e:
            raise DigitsError(f"Invalid digit on line {self._line_number}") from e

        while True:
            try:
                digits_str += self._parse_digit()
            except DigitError as e:
                break

        self._call_callbacks("on_digits_end", string=digits_str, line_number=self._line_number)
        return digits_str

    def _parse_digit(self):

        self._call_callbacks("on_digit_start", string="", line_number=self._line_number)

        try:
            digit_str = self._parse_literal("0")
            self._call_callbacks("on_digit_end", string=digit_str, line_number=self._line_number)
            return digit_str
        except LiteralError as e:
            pass

        try:
            digit_str = self._parse_onenine()
            self._call_callbacks("on_digit_end", string=digit_str, line_number=self._line_number)
            return digit_str
        except OneNineError as e:
            raise DigitError(f"Invalid digit on line {self._line_number}") from e

    def _parse_true(self):

        self._call_callbacks("on_true_start", string="", line_number=self._line_number)

        try:
            true_str = self._parse_literal("true")
        except LiteralError as e:
            raise TrueError(f"Expected 'true' on line {self._line_number}") from e

        self._call_callbacks("on_true_end", string=true_str, line_number=self._line_number)
        return true_str

    def _parse_false(self):

        self._call_callbacks("on_false_start", string="", line_number=self._line_number)

        try:
            false_str = self._parse_literal("false")
        except LiteralError as e:
            raise FalseError(f"Expected 'false' on line {self._line_number}") from e

        self._call_callbacks("on_false_end", string=false_str, line_number=self._line_number)
        return false_str

    def _parse_null(self):

        self._call_callbacks("on_null_start", string="", line_number=self._line_number)

        try:
            null_str = self._parse_literal("null")
        except LiteralError as e:
            raise NullError(f"Expected 'null' on line {self._line_number}") from e

        self._call_callbacks("on_null_end", string=null_str, line_number=self._line_number)
        return null_str

    def _parse_whitespace(self):

        self._call_callbacks("on_whitespace_start", string="", line_number=self._line_number)

        whitespace_str = ""

        try:
            while (char := self._get_current_chars(1)).isspace():
                whitespace_str += char
                if char == '\n':
                    self._line_number += 1
                self._increment_index(1)
        except (EndOfJsonError, IndexError):
            pass

        self._call_callbacks("on_whitespace_end", string=whitespace_str, line_number=self._line_number)
        return whitespace_str

    def _parse_literal(self, literal):

        self._call_callbacks("on_literal_start", string="", line_number=self._line_number)

        literal_str = self._get_current_chars(len(literal))
        if literal != literal_str:
            raise LiteralError(f"Expected '{literal}' but found '{literal_str}' on line {self._line_number}")

        self._increment_index(len(literal))

        self._call_callbacks("on_literal_end", string=literal_str, line_number=self._line_number)
        return literal_str
