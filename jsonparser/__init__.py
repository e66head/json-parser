"""
jsonparser package initialization.

This module imports and exposes the main components of the jsonparser package:
- JsonLexer: Responsible for tokenizing a Python string representing JSON.
- JsonParser: Parses the tokenized output of the JsonLexer producing Python data structures.
- Token: Represents individual tokens in the JSON input.
- errors: Contains custom exception classes for error handling.

Importing this package provides direct access to these core classes and error types.
"""

__version__ = "0.2.0"

from .lexer import JsonLexer
from .parser import JsonParser
from .tokens import Token
from .errors import *
