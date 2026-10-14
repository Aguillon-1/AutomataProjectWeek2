#!/usr/bin/env python3
"""Mini Tokenizer / Lexer -- standard library only, no `re`.

Each token type is a formal language with one small hand-written recognizer.
The main loop tries every recognizer at the current position and keeps the
longest match. On a tie, the recognizer listed first wins (KEYWORD > IDENTIFIER).
"""
import sys
import argparse
from collections import Counter

# ---------------------------------------------------------------- alphabets
KEYWORDS  = ("if", "else", "while", "print")
OPERATORS = ("==", "!=", "<=", ">=", "+", "-", "*", "/", "=", "<", ">")
DELIMS    = ("(", ")", ";")
WS_CHARS  = (" ", "\t", "\n")


def is_letter(c):            # Letter = {a-z, A-Z, _}
    return c == "_" or "a" <= c <= "z" or "A" <= c <= "Z"


def is_digit(c):             # Digit = {0-9}
    return "0" <= c <= "9"


def in_sigma(c):             # Sigma = printable ASCII
    return 32 <= ord(c) <= 126


# -------------------------------------------------- recognizers (return length)
def rec_keyword(s, i):
    best = 0
    for kw in KEYWORDS:
        if s.startswith(kw, i) and len(kw) > best:
            best = len(kw)
    return best


def rec_identifier(s, i):    # Letter (Letter U Digit)*
    if i >= len(s) or not is_letter(s[i]):
        return 0
    j = i + 1
    while j < len(s) and (is_letter(s[j]) or is_digit(s[j])):
        j += 1
    return j - i


def rec_number(s, i):        # Digit+ ( '.' Digit+ | epsilon )
    j = i
    while j < len(s) and is_digit(s[j]):
        j += 1
    if j == i:
        return 0
    if j < len(s) and s[j] == "." and j + 1 < len(s) and is_digit(s[j + 1]):
        j += 1
        while j < len(s) and is_digit(s[j]):
            j += 1
    return j - i


def rec_string(s, i):        # '"' (Sigma - {'"'})* '"'
    if i >= len(s) or s[i] != '"':
        return 0
    j = i + 1
    while j < len(s) and s[j] != '"' and in_sigma(s[j]):
        j += 1
    if j < len(s) and s[j] == '"':
        return j - i + 1
    return 0                 # unfinished -> handled as an error by the main loop


def rec_operator(s, i):
    best = 0
    for op in OPERATORS:
        if s.startswith(op, i) and len(op) > best:
            best = len(op)
    return best


def rec_delimiter(s, i):
    return 1 if i < len(s) and s[i] in DELIMS else 0


def rec_whitespace(s, i):    # {space, tab, newline}+
    j = i
    while j < len(s) and s[j] in WS_CHARS:
        j += 1
    return j - i


# Order = tie-break priority (first wins on equal length).
RECOGNIZERS = [
    ("KEYWORD",    rec_keyword),
    ("IDENTIFIER", rec_identifier),
    ("NUMBER",     rec_number),
    ("STRING",     rec_string),
    ("OPERATOR",   rec_operator),
    ("DELIMITER",  rec_delimiter),
    ("WHITESPACE", rec_whitespace),
]
TYPE_ORDER = [n for n, _ in RECOGNIZERS if n != "WHITESPACE"] + ["ERROR"]

RULES = """\
Let Letter = {a..z, A..Z, _}   Digit = {0..9}   Sigma = printable ASCII

KEYWORD     = {if, else, while, print}
IDENTIFIER  = Letter . (Letter U Digit)*
NUMBER      = Digit+ . ( ({.} . Digit+) U {epsilon} )
STRING      = {"} . (Sigma - {"})* . {"}
OPERATOR    = {+, -, *, /, =, ==, !=, <, >, <=, >=}
DELIMITER   = {(, ), ;}
WHITESPACE  = {space, tab, newline}+      (skipped, not output)

L_lex = (L_KEYWORD U L_IDENT U L_NUMBER U L_STRING U L_OP U L_DELIM U L_WS)*

Overlap rules:
  1. Longest match wins        ("iffy" is one IDENTIFIER, not 'if' + 'fy')
  2. On a tie, KEYWORD beats IDENTIFIER   ("if" is a KEYWORD)
"""

COLORS = {
    "KEYWORD": "\033[35m", "IDENTIFIER": "\033[36m", "NUMBER": "\033[33m",
    "STRING": "\033[32m", "OPERATOR": "\033[34m", "DELIMITER": "\033[37m",
    "ERROR": "\033[1;31m",
}
RESET = "\033[0m"


# ------------------------------------------------------------------- scanner
class Token:
    def __init__(self, type_, lexeme, line, col, note="", candidates=None):
        self.type, self.lexeme, self.line, self.col = type_, lexeme, line, col
        self.note = note                    # error message for ERROR tokens
        self.candidates = candidates or []  # [(type, length)] for explain mode


def tokenize(text):
    tokens, i, line, col = [], 0, 1, 1
    while i < len(text):
        cands = [(name, f(text, i)) for name, f in RECOGNIZERS]
        cands = [(n, l) for n, l in cands if l > 0]
        if cands:
            best = max(l for _, l in cands)
            winner = next(n for n, l in cands if l == best)   # list order = priority
            lexeme = text[i:i + best]
            if winner != "WHITESPACE":
                tokens.append(Token(winner, lexeme, line, col, candidates=cands))
        else:
            if text[i] == '"':   # opening quote with no valid close
                end = text.find("\n", i)
                end = len(text) if end == -1 else end
                lexeme = text[i:end]
                tokens.append(Token("ERROR", lexeme, line, col,
                                    note="unfinished string"))
            else:
                lexeme = text[i]
                tokens.append(Token("ERROR", lexeme, line, col,
                                    note=f"unrecognized symbol {lexeme!r}"))
        for ch in lexeme:        # advance position
            if ch == "\n":
                line, col = line + 1, 1
            else:
                col += 1
        i += len(lexeme)
    return tokens


# -------------------------------------------------------------------- output
def explain(tok):
    if tok.type == "ERROR":
        return tok.note + " (no recognizer matched)"
    parts = ", ".join(f"{n} matched {l} character{'s' if l != 1 else ''}"
                      for n, l in tok.candidates)
    lens = [l for _, l in tok.candidates]
    if len(tok.candidates) == 1:
        return f"{tok.type} was the only match"
    if lens.count(max(lens)) > 1:
        return f"{parts}; tie, so {tok.type} wins by priority"
    return f"{parts}; so {tok.type} wins"


def render(tokens, text, use_color=False, show_explain=False):
    out = [f"{'LINE:COL':<9} {'TYPE':<11} LEXEME"]
    for t in tokens:
        pos = f"{t.line}:{t.col}"
        if t.type == "ERROR":
            body = f"{t.note}" if t.note.startswith("unrec") else f"{t.note} {t.lexeme}"
            row = f"{pos:<9} {'ERROR':<11} {body}"
        else:
            row = f"{pos:<9} {t.type:<11} {t.lexeme}"
        if use_color:
            row = COLORS[t.type] + row + RESET
        out.append(row)
        if show_explain:
            out.append(f"{'':<9} {'':<11} -> {t.lexeme}: {explain(t)}")
    counts = Counter(t.type for t in tokens)
    per = ", ".join(f"{n}={counts[n]}" for n in TYPE_ORDER if counts[n])
    good = sum(v for k, v in counts.items() if k != "ERROR")
    out.append("")
    out.append(f"Summary: {len(text)} characters, {len(tokens)} tokens "
               f"({good} valid, {counts['ERROR']} errors)"
               + (f" | {per}" if per else ""))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Mini Tokenizer / Lexer")
    ap.add_argument("file", nargs="?", help=".txt source file")
    ap.add_argument("-l", "--line", help="tokenize a single typed line")
    ap.add_argument("--rules", action="store_true", help="print token languages")
    ap.add_argument("--explain", action="store_true", help="show why each token won")
    ap.add_argument("--no-color", action="store_true", help="disable colors")
    a = ap.parse_args()

    if a.rules:
        print(RULES)
        return 0

    if a.file:
        with open(a.file, encoding="utf-8") as f:
            text = f.read()
    elif a.line is not None:
        text = a.line
    else:
        text = input("lexer> ")

    color = sys.stdout.isatty() and not a.no_color
    if color:
        try:
            import colorama
            colorama.init()
        except ImportError:
            pass
    tokens = tokenize(text)
    print(render(tokens, text, color, a.explain))
    return 1 if any(t.type == "ERROR" for t in tokens) else 0


if __name__ == "__main__":
    sys.exit(main())
