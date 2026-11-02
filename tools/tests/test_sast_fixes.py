from xml.sax.saxutils import escape

import pytest

from refua_tests.utils.meditik_seed import escape_xml_text
from tools.update_bdd_tags import parse_tag_line


@pytest.mark.parametrize("text", [
    "", "a&b", "<x>&amp;\"'>", "שלום <b>", "&&&<<>>",
    "<!DOCTYPE a [<!ENTITY x SYSTEM 'file:///c:/x'>]>&x;",
])
def test_escape_xml_text_matches_the_previous_saxutils_behaviour(text):
    assert escape_xml_text(text) == escape(text)
    assert "<" not in escape_xml_text(text) and ">" not in escape_xml_text(text)


@pytest.mark.parametrize("line, expected", [
    ("  @bdd @meditik @home  ", ["bdd", "meditik", "home"]),
    ("@a\t@b", ["a", "b"]),
    ("@a", ["a"]),
    ("@", None),
    ("@a b", None),
    ("Feature: x", None),
    ("   ", None),
])
def test_parse_tag_line(line, expected):
    assert parse_tag_line(line) == expected


def test_parse_tag_line_handles_long_input_without_backtracking():
    assert parse_tag_line(" " * 200000 + "x") is None
    assert parse_tag_line("@a " * 100000 + "x") is None
