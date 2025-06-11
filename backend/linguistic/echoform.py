"""Minimal EchoForm parser with quoting and basic atom types.

This module provides :func:`parse_echoform` to transform a text string written
in a small subset of EchoForm into a nested list representation.  The syntax
resembles s-expressions where parentheses denote nested structures.  In
addition to plain tokens separated by whitespace, the parser understands
quoted tokens using single or double quotes and will convert numeric atoms to
``int`` or ``float`` values.  No advanced escaping is implemented; the goal is
to keep this lightweight for unit testing.
"""

from __future__ import annotations

import re
from typing import Any, List, Tuple

# Tokenizer supporting quoted strings and the quote operator. Quotes themselves
# are preserved so the parser can strip them after tokenisation. The single
# quote character is treated as a separate token so `'expr` can be expanded to
# ``['quote', expr]`` during parsing.
_TOKEN_RE = re.compile(r"\(|\)|[^\s()]+")


def _tokenize(text: str) -> List[str]:
    """Tokenize the input EchoForm text."""
    tokens: List[str] = []
    i = 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c in "()":
            tokens.append(c)
            i += 1
            continue
        if c == "'":
            tokens.append("'")
            i += 1
            continue
        if c == '"':
            j = i + 1
            buf = []
            while j < len(text):
                if text[j] == '"' and text[j - 1] != "\\":
                    break
                buf.append(text[j])
                j += 1
            else:
                raise ValueError("Unterminated string literal")
            tokens.append('"' + ''.join(buf) + '"')
            i = j + 1
            continue

        j = i
        while j < len(text) and not text[j].isspace() and text[j] not in "()'":
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def _atom(tok: str) -> Any:
    """Convert a token to an atomic Python value."""
    if (tok.startswith('"') and tok.endswith('"')) or (
        tok.startswith("'") and tok.endswith("'")
    ):
        return tok[1:-1]
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    if re.fullmatch(r"-?\d*\.\d+", tok):
        return float(tok)
    return tok


def _parse_item(tokens: List[str], pos: int) -> Tuple[Any, int]:
    """Parse a single item starting at ``pos`` and return it with next index."""
    if pos >= len(tokens):
        raise ValueError("Unexpected end of input")

    tok = tokens[pos]
    if tok == "(":
        lst, pos = _parse_tokens(tokens, pos + 1)
        return lst, pos
    if tok == "'":
        item, pos = _parse_item(tokens, pos + 1)
        return ["quote", item], pos
    if tok == ")":
        raise ValueError("Unexpected ')' in EchoForm")
    return _atom(tok), pos + 1


def _parse_tokens(tokens: List[str], pos: int = 0) -> Tuple[List[Any], int]:
    """Recursive descent parser returning a nested list and next position."""
    result: List[Any] = []
    while pos < len(tokens):
        if tokens[pos] == ")":
            return result, pos + 1
        item, pos = _parse_item(tokens, pos)
        result.append(item)
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
    tokens = _tokenize(text)
    ast, pos = _parse_tokens(tokens)
    if pos != len(tokens):
        raise ValueError("Unbalanced parentheses in EchoForm")
    return ast

