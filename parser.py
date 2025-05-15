from tokens import TokenType, KEYWORDS

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.errors = 0
        self.line_report = {}

    def parse(self):
        grouped = self.group_tokens_by_line()
        for line_num in sorted(grouped.keys()):
            tokens = grouped[line_num]

            # Check invalid type tokens first
            invalid_types = [t for t in tokens if t.type == TokenType.INVALID_TYPE]
            if invalid_types:
                self.line_report[line_num] = f"Line {line_num}: Not Matched Error: Invalid Type ({invalid_types[0].value})"
                self.errors += 1
                continue

            # Check invalid keywords (case mismatch or unknown)
            invalid_kw = self.check_invalid_keywords(tokens)
            if invalid_kw:
                self.line_report[line_num] = f"Line {line_num}: Not Matched Error: Invalid keyword '{invalid_kw}'"
                self.errors += 1
                continue

            # Try matching grammar rules
            rule = self.match_line_rules(tokens)
            if rule:
                self.line_report[line_num] = f"Line {line_num}: Matched Rule used: {rule}"
            else:
                self.line_report[line_num] = f"Line {line_num}: Not Matched Error: Syntax does not match any rule"
                self.errors += 1

        self.print_report()

    def group_tokens_by_line(self):
        grouped = {}
        for t in self.tokens:
            grouped.setdefault(t.line, []).append(t)
        return grouped

    def check_invalid_keywords(self, tokens):
        for t in tokens:
            if t.type == TokenType.IDENTIFIER:
                for kw in KEYWORDS.keys():
                    if t.value.lower() == kw.lower() and t.value != kw:
                        return t.value
                if t.value == 'in':  # not a Project#2 keyword
                    return t.value
        return None

    def match_line_rules(self, tokens):
        if (len(tokens) >= 3 and
            tokens[0].type == TokenType.START_SYMBOL and
            tokens[1].value == 'Type' and
            tokens[2].type == TokenType.IDENTIFIER):
            return "Program and ClassDeclaration"

        if (len(tokens) >= 5 and
            tokens[0].value == 'Func' and
            tokens[1].type in [TokenType.INTEGER, TokenType.SINTEGER, TokenType.CHARACTER,
                               TokenType.STRING, TokenType.FLOAT, TokenType.SFLOAT,
                               TokenType.VOID, TokenType.BOOLEAN] and
            tokens[2].type == TokenType.IDENTIFIER and
            tokens[3].value == '('):
            return "Func Decl"

        if (len(tokens) >= 4 and
            tokens[0].type in [TokenType.BOOLEAN, TokenType.INTEGER, TokenType.SINTEGER,
                               TokenType.CHARACTER, TokenType.STRING, TokenType.FLOAT,
                               TokenType.SFLOAT, TokenType.VOID] and
            tokens[1].type == TokenType.IDENTIFIER and
            tokens[2].value == '(' and tokens[-1].value in ['{', ';']):
            return "Func Decl"

        if (len(tokens) >= 3 and
            tokens[0].type in [TokenType.INTEGER, TokenType.SINTEGER, TokenType.CHARACTER,
                               TokenType.STRING, TokenType.FLOAT, TokenType.SFLOAT,
                               TokenType.VOID, TokenType.BOOLEAN] and
            tokens[1].type == TokenType.IDENTIFIER and
            tokens[-1].value == ';'):
            return "Variable Decl"

        # Array declaration: Type ID [ Constant ];
        if (len(tokens) >= 5 and
            tokens[0].type in [TokenType.INTEGER, TokenType.SINTEGER, TokenType.CHARACTER,
                              TokenType.STRING, TokenType.FLOAT, TokenType.SFLOAT,
                              TokenType.VOID, TokenType.BOOLEAN] and
            tokens[1].type == TokenType.IDENTIFIER and
            tokens[2].value == '[' and tokens[3].type == TokenType.CONSTANT and
            tokens[4].value == ']'):
            return "Array Decl"

        if (len(tokens) >= 4 and
            tokens[0].type == TokenType.IDENTIFIER and
            tokens[1].value == '=' and
            tokens[-1].value == ';'):
            return "Assignment"

        if (tokens[0].type == TokenType.IDENTIFIER and
            tokens[1].value == '(' and tokens[-1].value == ';'):
            return "Func Call"

        if tokens[0].value == 'When':
            return "WhenStmt"

        if tokens[0].value == 'However' and tokens[1].value == '(' and tokens[-1].value == '{':
            return "HoweverStmt"

        if tokens[0].value == 'TrueFor' and tokens[1].value == '(' and tokens[-1].value == '{':
            return "TrueForStmt"

        if tokens[0].value == 'Endthis' and tokens[-1].value == ';':
            return "EndthisStmt"

        if tokens[0].value == 'Scan' and tokens[1].value == '(' and tokens[2].value == 'Conditionof':
            return "ScanStmt"

        if tokens[0].value == 'Srap' and tokens[1].value == '(' and tokens[-1].value == ';':
            return "SrapStmt"

        if tokens[0].type == TokenType.INCLUSION and tokens[-1].value == ';':
            return "Require Command"

        if tokens[0].value == 'Respondwith' and tokens[-1].value == ';':
            return "RespondwithStmt"

        # Expression statements with relational or logic operators ending with ';'
        if tokens[-1].value == ';' and any(
            t.type in [TokenType.RELATIONAL_OP, TokenType.LOGIC_OP] for t in tokens):
            return "ExpressionStmt"

        if len(tokens) == 1 and tokens[0].type in [TokenType.BRACES, TokenType.END_SYMBOL]:
            return "End Symbol or Braces"

        return None

    def print_report(self):
        for line in sorted(self.line_report):
            print(self.line_report[line])
        print(f"\nTotal NO of errors: {self.errors}")
