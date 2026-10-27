import unittest
from lexer import tokenize


def kinds(src):
    return [(t.type, t.lexeme) for t in tokenize(src)]


class LexerTests(unittest.TestCase):
    def test_longest_match(self):
        self.assertEqual(kinds("iffy"), [("IDENTIFIER", "iffy")])

    def test_keyword_tie(self):
        self.assertEqual(kinds("if"), [("KEYWORD", "if")])

    def test_number_forms(self):
        self.assertEqual(kinds("12 3.14"), [("NUMBER", "12"), ("NUMBER", "3.14")])

    def test_two_char_operators(self):
        self.assertEqual([t for _, t in kinds("== != <= >=")], ["==", "!=", "<=", ">="])

    def test_bad_symbol_position(self):
        t = [x for x in tokenize("x = 5 @ 2") if x.type == "ERROR"][0]
        self.assertEqual((t.line, t.col), (1, 7))

    def test_scan_continues_after_error(self):
        self.assertEqual(tokenize("x = 5 @ 2")[-1].lexeme, "2")

    def test_unfinished_string(self):
        t = tokenize('print "hello;\nx')
        self.assertEqual(t[1].note, "unfinished string")
        self.assertEqual(t[-1].lexeme, "x")
        self.assertEqual((t[-1].line, t[-1].col), (2, 1))

    def test_grammar_not_checked(self):
        self.assertTrue(all(t.type != "ERROR" for t in tokenize("5 + + 3")))

    def test_python_like_tokens(self):
        self.assertEqual(
            kinds("def greet(name):\n    # hi\n    return 'Hello, ' + name\n"),
            [
                ("KEYWORD", "def"), ("IDENTIFIER", "greet"),
                ("DELIMITER", "("), ("IDENTIFIER", "name"),
                ("DELIMITER", ")"), ("DELIMITER", ":"),
                ("NEWLINE", "\\n"), ("COMMENT", "# hi"),
                ("NEWLINE", "\\n"), ("INDENT", "    "),
                ("KEYWORD", "return"), ("STRING", "'Hello, '"),
                ("OPERATOR", "+"), ("IDENTIFIER", "name"),
                ("NEWLINE", "\\n"), ("DEDENT", ""),
            ],
        )

    def test_python_operators_and_keywords(self):
        self.assertEqual(
            kinds("True and value ** 2 // 1"),
            [
                ("KEYWORD", "True"), ("KEYWORD", "and"),
                ("IDENTIFIER", "value"), ("OPERATOR", "**"),
                ("NUMBER", "2"), ("OPERATOR", "//"), ("NUMBER", "1"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
