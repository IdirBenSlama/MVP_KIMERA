import os
import pytest

os.environ["ENABLE_JOBS"] = "0"
from backend.linguistic.echoform import parse_echoform

@pytest.mark.parametrize("text,expected", [
    ("(hello world)", [["hello", "world"]]),
    ("(greet 'world)", [["greet", ["quote", "world"]]]),
    ("(add 1 2.5)", [["add", 1, 2.5]]),
])
def test_parse_echoform_valid(text, expected):
    assert parse_echoform(text) == expected


