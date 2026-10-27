# Lexer

A hand-written Python-like lexer where every token type is a formal language.
Python 3, standard library only (no `re`). `colorama` optional.

    python lexer.py samples/ok1_assign.txt
    python lexer.py -l "def greet(name):" --explain
    python lexer.py --rules
    python -m unittest test_lexer -v

## Layout
    lexer.py          scanner + CLI (recognizers, longest-match loop)
    test_lexer.py     unit tests
    samples/          Python-like clean files and deliberate errors
    USER_GUIDE.md     usage, flags, error behavior
    demo_output.txt   recorded demo run

## Web version
Open `index.html` in any browser (double-click, no server or install).
It is a JavaScript port of the same recognizers and rules, with live
highlighting, a token table, explain toggle, sample buttons, and .txt upload.
Everything runs in the browser; no code is sent anywhere.

## Supported language
The lexer supports a Python-like lexical language: Python keywords and
identifiers, integers and decimals, single- and double-quoted strings with
backslash escapes, `#` comments, common Python operators, delimiters,
`NEWLINE`, and indentation-sensitive `INDENT`/`DEDENT` tokens. It is a lexer,
not a full Python parser, so it identifies tokens without validating complete
program grammar.
