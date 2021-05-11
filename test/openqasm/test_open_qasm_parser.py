import unittest

from zxopt.openqasm import OpenQASMParserLegacy

COMMENT_INPUT = """Hello b/*loc*/k
//line
world"""

STATEMENTS_INPUT = """
doSth;
;
sth multi
line;
"""

class OpenQASMParserTest(unittest.TestCase):
    def test_get_statements(self):
        output = OpenQASMParserLegacy()._OpenQASMParser__get_statements(STATEMENTS_INPUT)
        self.assertEqual(["doSth", "sth multi line"], output)

    def test_eliminate_comments(self):
        output = OpenQASMParserLegacy()._OpenQASMParser__eliminate_comments(COMMENT_INPUT)
        self.assertEqual("Hello bk\nworld", output)
