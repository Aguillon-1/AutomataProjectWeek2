# Mini Tokenizer / Lexer: User Guide

Python 3, standard library only (`colorama` is optional for color on older Windows).

## Run it
    python lexer.py samples/ok1_assign.txt        # a .txt source file
    python lexer.py -l "total = price * 3;"       # one typed line
    python lexer.py                               # prompts you to type a line

## Options
| Flag | What it does |
|---|---|
| `--rules` | Prints the formal language of every token type |
| `--explain` | Shows why each token won (match length per recognizer) |
| `--no-color` | Turns off colored output (color is auto-off when piped) |

## Reading the output
`LINE:COL TYPE LEXEME`, with 1-based positions (a tab counts as 1 column).
Whitespace is skipped. The last line is the summary: characters, tokens, per-type counts.
Exit code is 1 if any ERROR token was found, else 0.

## Errors (scanning keeps going)
- `unrecognized symbol '@'`: no token language contains that character. One character is skipped.
- `unfinished string`: a `"` with no closing `"` on the same line. The rest of the line is consumed.

## Overlap rules
1. Longest match wins: `iffy` is one IDENTIFIER.
2. On a tie, KEYWORD beats IDENTIFIER: `if` is a KEYWORD.

## Limits
Lexing only (`5 + + 3` is fine). Strings are single-line, no escapes. No comments.
No negative literals (`-` is an operator). `3.` lexes as NUMBER `3` then an error for `.`.

## Samples
Clean: `ok1_assign.txt`, `ok2_loop.txt`, `ok3_mixed.txt`
Errors: `err1_bad_symbol.txt`, `err2_unfinished_string.txt`

## Web version
Open `web/index.html` in a browser.
- Type in the Source box: tokens update live, and the code below it is colored by token type.
- Hover a token (in the colored code or the table) to highlight its match.
- Tick "Explain why each token won" to see match lengths per recognizer.
- Use the sample buttons or "Open .txt" to load code.
- Open "Token languages" at the bottom for the formal definitions.
The page loads IBM Plex fonts from Google Fonts when online and falls back to system fonts offline.
