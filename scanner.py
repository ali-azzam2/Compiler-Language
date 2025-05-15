import re
from tokens import KEYWORDS, TokenType, Token

TOKEN_REGEX = [
    # Must be first to catch require statements before identifiers
    (r'Require\s*\(\s*([\w\.]+)\s*\)', TokenType.INCLUSION),

    (r'/<.*?>/', TokenType.COMMENT),
    (r'/\*.*?\*/', TokenType.COMMENT),
    (r'@|\^', TokenType.START_SYMBOL),
    (r'\$|#', TokenType.END_SYMBOL),
    (r'\{|\}|\(|\)', TokenType.BRACES),
    (r'\[|\]', TokenType.BRACES),
    (r';|,', TokenType.DELIMITER),
    (r'->', TokenType.ACCESS_OP),
    (r'&&|\|\||~', TokenType.LOGIC_OP),
    (r'==|!=|>=|<=|>|<', TokenType.RELATIONAL_OP),
    (r'=', TokenType.ASSIGNMENT_OP),
    (r'\+|\-|\*|/', TokenType.ARITHMETIC_OP),

    (r'\d+[a-zA-Z_][a-zA-Z0-9_]*', TokenType.ERROR),  # invalid identifiers starting with digits
    (r'\d+', TokenType.CONSTANT),
    (r'"[^"]*"', TokenType.STRING),
    (r"'[^']*'", TokenType.CHARACTER),
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER_OR_KEYWORD'),

    (r'\s+', None),  # whitespace ignored
]

class Scanner:
    def __init__(self, filename):
        self.filename = filename
        self.tokens = []
        self.errors = []
        self.line_num = 1
        self.in_multiline_comment = False
        self.visited_files = set()

    def scan_file(self, filename=None):
        filename = filename or self.filename
        if filename in self.visited_files:
            return
        self.visited_files.add(filename)

        try:
            with open(filename, 'r') as f:
                for line in f:
                    self.tokenize_line(line.rstrip('\n'))
                    self.line_num += 1
        except FileNotFoundError:
            self.errors.append(f"Line {self.line_num}: File not found: {filename}")

    def tokenize_line(self, line):
        if self.in_multiline_comment:
            if '>/' in line:
                self.in_multiline_comment = False
                line = line.split('>/', 1)[1]
            else:
                return

        if '/<' in line:
            self.in_multiline_comment = True
            line = line.split('/<', 1)[0]

        line = re.sub(r'/\*.*?\*/', '', line)

        pos = 0
        while pos < len(line):
            match = None
            for pattern, token_type in TOKEN_REGEX:
                regex = re.compile(pattern)
                match = regex.match(line, pos)
                if match:
                    text = match.group(0)
                    if token_type is None:
                        pass
                    elif token_type == TokenType.INCLUSION:
                        # Add inclusion token (Require)
                        self.tokens.append(Token(TokenType.INCLUSION, text, self.line_num))
                        include_file = match.group(1)
                        self.scan_file(include_file)
                    elif token_type == 'IDENTIFIER_OR_KEYWORD':
                        self.handle_identifier(text)
                    else:
                        self.tokens.append(Token(token_type, text, self.line_num))
                    pos = match.end()
                    break
            if not match:
                # Treat unrecognized tokens as identifiers instead of errors
                self.tokens.append(Token(TokenType.IDENTIFIER, line[pos], self.line_num))
                pos += 1

    def handle_identifier(self, text):
        if text in KEYWORDS:
            self.tokens.append(Token(KEYWORDS[text], text, self.line_num))
        elif text in ['int', 'float', 'char']:
            self.tokens.append(Token(TokenType.INVALID_TYPE, text, self.line_num))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, text, self.line_num))

    def print_tokens(self):
        error_count = 0
        for token in self.tokens:
            print(f"Line {token.line}: Token Text: {token.value} Token Type: {token.type.value}")
        print(f"\nTotal NO of errors: {error_count}")
