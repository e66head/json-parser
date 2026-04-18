"""
A module for defining the JSON parser's token structure.
"""

###JDG TODO: Fix these pylint errors.
# pylint: disable=missing-class-docstring

from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: any = None
    line: int = 0
