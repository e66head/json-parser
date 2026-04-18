"""
Custom stack implementation that extends the built-in list type.

This module provides a custom stack class that inherits from Python's built-in list type. But it adds explicit methods
for stack operations so that stack behavior is specific and clear. It supports the basic stack operations push, pop,
peek with the end of the list considered to be the top of the stack. It also includes methods for popping multiple
items based on depth or based on a "predicate" function that takes stack items and returns a boolean indicating whether
the item matches whatever condition the predicate function is checking for. It also provides a pretty-print
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

    def pop_to_depth(self, depth: int) -> list:
        """Pops a list of 'depth' items and returns them in LIFO (reversed) order."""
        return [self.pop() for _ in range(depth)]

    def pop_to_item(self, predicate: callable) -> list:
        """Pops a list of items to the item matching 'predicate'. Returns them in LIFO (reversed) order.

        Note: The item matching the predicate is included in the returned list.
        """
        items = []
        while not self.is_empty():
            item = self.pop()
            items.append(item)
            if predicate(item):
                return items
        raise IndexError("Item matching predicate not found on stack")

    def pop_from_depth(self, depth: int) -> list:
        """Pops a list of 'depth' items and returns them in FIFO (original) order."""
        if len(self) < depth:
            raise IndexError(f"Attempted to pop {depth} items, but stack only has {len(self)}")
        items = self[-depth:]
        del self[-depth:]
        self._logger.debug("Popped %d items from depth (FIFO)", len(items))
        return items

    def pop_from_item(self, predicate: callable) -> list:
        """Pops a list of items starting from the item matching 'predicate'. Returns them in FIFO (original) order.
        
        Note: The item matching the predicate is included in the returned list.
        """
        for i in range(len(self) - 1, -1, -1):
            if predicate(self[i]):
                # elements = the matching item and everything after it
                elements = self[i:]
                # Remove everything from the matching item to the top
                del self[i:]
                self._logger.debug("Popped to item matching predicate (FIFO)")
                return elements

        raise IndexError("Item matching predicate not found on stack")

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
