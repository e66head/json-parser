"""
Custom stack implementation that extends the built-in list type.

This module provides a custom stack class that inherits from Python's built-in list type. But it adds explicit methods
for stack operations so that stack behavior is specific and clear. It supports the basic stack operations push, pop,
peek with the end of the list considered to be the top of the stack. It also provides a pretty-print
representation of the stack's contents when it's printed.
"""

import logging

class Stack(list):
    """A simple stack implementation that extends the built-in list type."""

    def __init__(self, item=None):
        super().__init__()  # explicitly initialize the list
        if item:
            if isinstance(item, list):
                self.extend(item)
            else:
                self.push(item)
        self._logger = logging.getLogger(__name__)

    def __repr__(self):
        return f"Stack: {"".join([f"\n| {item}" for item in self]) if self else " empty"}\n"

    def push(self, item):
        """Pushes an item onto the stack."""
        self.append(item)
        self._logger.debug("Pushed: %s", item)

    def pop(self) -> any:
        """Pops an item from the stack."""

        # Ensure the stack is not empty before attempting to pop from it.
        if not self:
            raise IndexError("Attempted to pop from an empty stack")
        item = super().pop()
        self._logger.debug("Popped: %s", item)
        return item

    def pop_from_index(self, index: int) -> list:
        """Pops all items from the specified index to the top of the stack and returns them in FIFO order.
        
        The item at the specified index is included as the first item in the returned list.
        """
        if index < 0 or index >= len(self):
            raise IndexError(f"Index {index} is out of bounds for stack of size {len(self)}")

        # Python's slice syntax is used to get all items from the index to the top of the stack and to delete them from
        # the stack in one operation. Even though this is still O(K) where K is the number of items popped, it is
        # significantly faster than repeated individual pop() calls because the whole operation happens in the C layer.
        items = self[index:]
        del self[index:]
        self._logger.debug("Popped %d items from index %d to top (FIFO)", len(items), index)
        return items

    def peek(self):
        """Returns the top item of the stack without removing it.
        
        Note: Callers should check if the stack is empty to avoid an IndexError.
        """
        try:
            return self[-1]
        except IndexError as exc:
            raise IndexError("Attempted to peek from an empty stack") from exc

    def is_empty(self):
        """Returns True if the stack is empty, False otherwise."""
        return len(self) == 0

    def size(self):
        """Returns the number of items in the stack."""
        return len(self)
