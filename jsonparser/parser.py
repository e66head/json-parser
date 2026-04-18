
###JDG TODO: Fix these pylint errors.
# pylint: disable=missing-module-docstring    # This file needs a docstring.
# pylint: disable=unused-import               # This is due to the import of tokens.
# pylint: disable=missing-class-docstring     # Classes should have docstrings.
# pylint: disable=missing-function-docstring  # Functions should have docstrings.
# pylint: disable=raise-missing-from          # Exceptions are not being raised properly and should be fixed.
# pylint: disable=unused-variable             # This is due to raising exceptions as "e" but not using "e".
# pylint: disable=useless-parent-delegation   # This will get fixed by changing the relationship between JsonParser and JsonLexer to composition
# pylint: disable=unused-argument             # This will get fixed by converting to yielding/returning/passing tokens.

from .lexer import JsonLexer
from .errors import *  # pylint: disable=wildcard-import,unused-wildcard-import
from .stack import Stack

###JDG TODO: JsonParser should not extend JsonLexer using inheritence. Rather, it should import and use it in a composition manner.
class JsonParser(JsonLexer):
    """A simple JSON parser that uses the JsonLexer to parse JSON strings."""

    class JsonParserState:
        """A simple class to represent the state of the JSON parser."""
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return f"JsonParserState:{self.name}"

    # Create sentinel objects to represent the initial state and waiting states of the JSON context.
    NOT_SET = JsonParserState("NOT_SET")
    WAITING_FOR_OBJECT_KEY = JsonParserState("WAITING_FOR_OBJECT_KEY")
    WAITING_FOR_OBJECT_VALUE = JsonParserState("WAITING_FOR_OBJECT_VALUE")
    WAITING_FOR_ARRAY_VALUE = JsonParserState("WAITING_FOR_ARRAY_VALUE")
    WAITING_FOR_VALUE = JsonParserState("WAITING_FOR_VALUE")
    LEXING_DONE = JsonParserState("LEXING_DONE")

    def __init__(self, json_str, debug=False):

        self._str = json_str
        self._content = JsonParser.NOT_SET
        self._context = Stack(debug=debug)
        self._context.push(JsonParser.LEXING_DONE)
        self._context.push(JsonParser.WAITING_FOR_VALUE)
        self._debug = debug

        regular_callbacks = {
            "on_object_start": self._on_container_start,
            "on_object_end": self._on_container_end,
            "on_array_start": self._on_container_start,
            "on_array_end": self._on_container_end,
            "on_string_end": self._on_string_end,
            "on_number_end": self._on_scaler_end,
            "on_true_end": self._on_scaler_end,
            "on_false_end": self._on_scaler_end,
            "on_null_end": self._on_scaler_end,
            "on_key_end": self._on_key_end,
        }
        debug_callbacks = {
            "on_object_start": [self._debug_event_handler_enter],
            "on_object_end": [self._debug_event_handler_exit],
            "on_array_start": [self._debug_event_handler_enter],
            "on_array_end": [self._debug_event_handler_exit],
            "on_string_start": [self._debug_event_handler_enter],
            "on_string_end": [self._debug_event_handler_exit],
            "on_number_start": [self._debug_event_handler_enter],
            "on_number_end": [self._debug_event_handler_exit],
            "on_true_start": [self._debug_event_handler_enter],
            "on_true_end": [self._debug_event_handler_exit],
            "on_false_start": [self._debug_event_handler_enter],
            "on_false_end": [self._debug_event_handler_exit],
            "on_null_start": [self._debug_event_handler_enter],
            "on_null_end": [self._debug_event_handler_exit],
            "on_key_start": [self._debug_event_handler_enter],
            "on_key_end": [self._debug_event_handler_exit],
        }
        callbacks = regular_callbacks

        super().__init__(json_str, callbacks, debug=debug)

        if debug:
            super().add_callbacks(debug_callbacks)

    def parse(self):
        return super().parse()  # Call the base class's parse method.

        ###JDG TODO: The parser should call the lexer to receive tokens and process the tokens here to produce a python object.
        # tokens = self.lexer.tokenize()
        # for token in tokens:
        #     print(f"Received token: {token}")
        # return None

    def _debug_event_handler_enter(self, event, string, line_number):
        print(f"ENTERING handler for {event=} {self._context.peek()=} '{string=}' {self._line_number=}")

    def _debug_event_handler_exit(self, event, string, line_number):
        print(f"EXITING  handler for {event=} {self._context.peek()=} '{string=}' {self._line_number=}")

    def _on_container_start(self, event, string, line_number):

        match event:
            case "on_object_start":
                container = {}
                next_action = JsonParser.WAITING_FOR_OBJECT_KEY
            case "on_array_start":
                container = []
                next_action = JsonParser.WAITING_FOR_ARRAY_VALUE
            case _:
                # This is an error but it should never happen since this function should be used only for "on_object_start" and "on_array_start" events.
                raise UnknownEventError(f"Unknown event ({event}) in _on_container_start on line {line_number}")

        context = self._context.pop()
        match context:
            case JsonParser.WAITING_FOR_VALUE:
                self._content = container
                self._context.push(self._content)
                self._context.push(next_action)
            case JsonParser.WAITING_FOR_OBJECT_VALUE:
                key = self._context.pop()
                self._context.peek()[key] = container
                self._context.push(JsonParser.WAITING_FOR_OBJECT_KEY)
                self._context.push(container)
                self._context.push(next_action)
            case JsonParser.WAITING_FOR_ARRAY_VALUE:
                array = self._context.peek()
                array.append(container)
                self._context.push(JsonParser.WAITING_FOR_ARRAY_VALUE)
                self._context.push(container)
                self._context.push(next_action)
            case _:
                raise InvalidStateError(f"Invalid context state ({context}) for on-container-start event ({event}) on line {line_number}")

    def _on_container_end(self, event, string, line_number):

        context = self._context.pop()
        match context:
            case JsonParser.WAITING_FOR_OBJECT_KEY:
                assert event == "on_object_end", "Expected 'on_object_end' event for object end."
                self._context.pop()
            case JsonParser.WAITING_FOR_ARRAY_VALUE:
                assert event == "on_array_end", "Expected 'on_array_end' event for array end."
                self._context.pop()
            case _:
                raise InvalidStateError(f"Invalid context state ({context}) for on-container-end event ({event}) on line {line_number}")

    ###JDG TODO: This should move to the lexer.
    ###JDG TODO: This is complicated. Consider refactoring this to use a single state variable.
    def _convert_string(self, string):

        escape_conversions = {'"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}
        out_str = ""
        escape_found = False
        num_hex_chars = 0
        for char in string[1:-1]: # Skip the surrounding quotes
            if escape_found:
                escape_found = False
                if char == "u":
                    num_hex_chars = 1
                    hex_str = "\\u"
                else:
                    out_str += escape_conversions[char]
            elif num_hex_chars > 0:
                hex_str += char
                num_hex_chars += 1
                if num_hex_chars == 5:
                    num_hex_chars = 0
                    unicode_char = hex_str.encode('utf-8').decode('unicode_escape')
                    out_str += unicode_char
            elif char == '\\':
                escape_found = True
            else:
                out_str += char
        return out_str

    def _convert_number(self, string):

        try:
            return int(string)
        except ValueError:
            return float(string)

    def _on_string_end(self, event, string, line_number):

        # Check for the special case of a string end event while waiting for an object key. In this case, the string end event should be ignored in favor of
        # allowing the _on_key_end handler to process it.
        if self._context.peek() != JsonParser.WAITING_FOR_OBJECT_KEY:
            self._on_scaler_end(event, string, line_number)

    def _on_scaler_end(self, event, string, line_number):

        match event:
            case "on_string_end":
                scaler = self._convert_string(string)
            case "on_number_end":
                scaler = self._convert_number(string)
            case "on_true_end":
                scaler = True
            case "on_false_end":
                scaler = False
            case "on_null_end":
                scaler = None
            case _:
                # This is an error but it should never happen since this function should be used only for the above events.
                raise UnknownEventError(f"Unhandled event ({event}) in _on_scaler_end")

        context = self._context.pop()
        match context:
            case JsonParser.WAITING_FOR_VALUE:
                self._content = scaler
            case JsonParser.WAITING_FOR_OBJECT_VALUE:
                key = self._context.pop()
                self._context.peek()[key] = scaler
                self._context.push(JsonParser.WAITING_FOR_OBJECT_KEY)
            case JsonParser.WAITING_FOR_ARRAY_VALUE:
                array = self._context.peek()
                array.append(scaler)
                self._context.push(JsonParser.WAITING_FOR_ARRAY_VALUE)
            case _:
                raise InvalidStateError(f"Invalid context state ({context}) for on-scaler-end event ({event}) on line {line_number}")

    def _on_key_end(self, event, string, line_number):

        key = string
        context = self._context.pop()
        match context:
            case JsonParser.WAITING_FOR_OBJECT_KEY:
                self._context.push(key)
                self._context.push(JsonParser.WAITING_FOR_OBJECT_VALUE)
            case _:
                raise InvalidStateError(f"Invalid context state ({context}) for on-key-end event ({event}) on line {line_number}")
