"""Minimal EchoForm parser.

This module provides :func:`parse_echoform` to transform a text string written
in a very small subset of EchoForm into a nested list representation. The
supported syntax resembles s-expressions where parentheses denote nested
structures. Tokens are separated by whitespace. No quoting or escaping is
implemented -- this is intentionally lightweight for the unit tests.
"""

from __future__ import annotations

import re
from typing import List, Tuple

_TOKEN_RE = re.compile(r"\(|\)|[^\s()]+")


def _parse_tokens(tokens: List[str], pos: int = 0) -> Tuple[List, int]:
    """Recursive descent parser returning a nested list and next position."""
    result: List = []
    while pos < len(tokens):
        tok = tokens[pos]
        if tok == "(":
            sub, pos = _parse_tokens(tokens, pos + 1)
            result.append(sub)
        elif tok == ")":
            return result, pos + 1
        else:
            result.append(tok)
            pos += 1
    return result, pos


def parse_echoform(text: str) -> List:
    """Parse a string of EchoForm into a nested list structure.

    Parameters
    ----------
    text: str
        Raw EchoForm text. Parentheses must be balanced.

    Returns
    -------
    list
        Nested list representation of the form.
    """
    tokens = _TOKEN_RE.findall(text)
    ast, pos = _parse_tokens(tokens)
    if pos != len(tokens):
        raise ValueError("Unbalanced parentheses in EchoForm")
    return ast
