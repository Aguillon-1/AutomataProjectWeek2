# Mini Tokenizer / Lexer

A hand-written lexer where every token type is a formal language.
Python 3, standard library only (no `re`). `colorama` optional.

    python lexer.py samples/ok1_assign.txt
    python lexer.py -l "iffy if" --explain
    python lexer.py --rules
    python -m unittest test_lexer -v

## Layout
    lexer.py          scanner + CLI (recognizers, longest-match loop)
    test_lexer.py     unit tests
    samples/          3 clean files, 2 with deliberate errors
    USER_GUIDE.md     usage, flags, error behavior
    demo_output.txt   recorded demo run

## Web version
Open `web/index.html` in any browser (double-click, no server or install).
It is a JavaScript port of the same recognizers and rules, with live
highlighting, a token table, explain toggle, sample buttons, and .txt upload.
Everything runs in the browser; no code is sent anywhere.
