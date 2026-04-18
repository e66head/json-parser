"""
Custom stack implementation that extends the built-in list type.

This module provides a custom stack class that inherits from Python's built-in list type. But it adds explicit methods for stack operations so that stack
behavior is specific and clear. It supports the basic stack operations push, pop, peek, as well as providing a pretty-print representation of the stack's
contents when it's printed.
"""

###JDG TODO: Fix these pylint errors.
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=raise-missing-from

class Stack(list):

    def __init__(self, item=None, debug=False):
        super().__init__()  # explicitly initialize the list
        if item:
            if isinstance(item, list):
                self.extend(item)
            else:
                self.push(item)
        self._debug = debug

    def __repr__(self):
        return f"Stack: {"".join([f"\n| {item}" for item in self]) if self else " empty"}\n"

    def push(self, item):
        self.append(item)
        if self._debug:
            print(f"\nPushed: {item}\n{self}")

    def pop(self):
        # Ensure the stack is not empty before attempting to pop from it.
        if not self:
            raise IndexError("Attempted to pop from an empty stack")
        item = super().pop()
        if self._debug:
            print(f"\nPopped: {item}\n{self}")
        return item

    def peek(self):
        try:
            return self[-1]
        except IndexError:
            raise IndexError("Attempted to peek from an empty stack")
