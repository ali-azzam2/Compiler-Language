# Project#2 Language Compiler

This project implements a compiler (scanner and parser) for the Project#2 Language as described in the provided specification.

## Features
- Case-sensitive, object-oriented language
- Scanner (lexer) for tokenizing input, handling comments, whitespace, and file inclusion
- Parser for grammar rules and syntax checking
- Error reporting for both scanner and parser phases
- Sample input and output
- Output formatting matches the official project requirements

## Project Structure

```
project2_compiler/
│
├── main.py                # Entry point
├── scanner.py             # Scanner (lexer) implementation
├── parser.py              # Parser implementation
├── tokens.py              # Token types, keyword dictionary
├── grammar.py             # Grammar rules (for reference/LL(1) table)
├── utils.py               # Helper functions (file handling, etc.)
├── sample_input.txt       # Example input file
├── README.md              # How to run and use the project
└── requirements.txt       # Python dependencies (if any)
```

## How to Run

1. Place your Project#2 source code in `sample_input.txt` or another file.
2. Run the compiler:
   ```bash
   python main.py sample_input.txt
   ```
3. The output will show the scanner and parser results as specified.

---

## Output Interpretation
- **Scanner Output:**
  - Lists each token with its line number, text, and type.
  - Errors are reported with line number and error description.
  - The total number of errors is shown at the end.
- **Parser Output:**
  - For each matched rule, the line number and rule used are shown.
  - Errors are reported with line number, error type, and description.
  - The total number of errors is shown at the end.
- Output formatting and wording match the official project requirements.

## Sample Output
```
Scanner Output:
Line : 1 Token Text: @    Token Type: Stat Symbol
Line : 1 Token Text: Type    Token Type: Class
Line : 1 Token Text: Person    Token Type: Identifier
Line : 1 Token Text: {    Token Type: Braces
...
Total NO of errors: 0

Parser Output:
Line : 1 Matched    Rule used: Program and ClassDeclaration
Line : 1 Matched    Rule used: ClassBody
Line : 2 Matched    Rule used: MethodDecl
...
Total NO of errors: 0
```

---

## Notes
- The scanner supports file inclusion using the `Require` command.
- Comments and whitespace are ignored.
- All keywords, symbols, and grammar rules are implemented as per the specification.
- Error cases and edge cases are covered in the sample input.

---

For more details, see the code and comments in each file. 