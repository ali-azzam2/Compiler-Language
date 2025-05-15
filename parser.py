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
        # Rule 1, 2, 3, 4: Program -> Start_Symbols ClassDeclaration End_Symbols
        if len(tokens) >= 3 and self.is_start_symbol(tokens[0]) and tokens[1].value == 'Type' and tokens[2].type == TokenType.IDENTIFIER:
            return "Program and ClassDeclaration"

        # Rule 5: ClassBody -> { ClassMembers }
        if len(tokens) >= 1 and tokens[0].value == '{':
            return "ClassBody"
        if len(tokens) >= 1 and tokens[0].value == '}':
            return "End of ClassBody"

        # Rule 9: FuncDecl -> Type ID ( ParameterList )
        if (len(tokens) >= 5 and 
            self.is_type(tokens[0]) and
            tokens[1].type == TokenType.IDENTIFIER and
            tokens[2].value == '(' and 
            ')' in [t.value for t in tokens]):
            if tokens[-1].value == ';':
                return "MethodDecl - FuncDecl ;"
            elif tokens[-1].value == '{':
                return "MethodDecl - FuncDecl {"
            return "FuncDecl"

        # Rule 13: VariableDecl -> Type IDList ; | Type IDList [ ID ] ;
        if (len(tokens) >= 3 and
            self.is_type(tokens[0]) and
            tokens[1].type == TokenType.IDENTIFIER and
            tokens[-1].value == ';'):
            if '[' in [t.value for t in tokens]:
                return "VariableDecl with array"
            return "VariableDecl"

        # Rule 18: Assignment -> ID = Expression ;
        if (len(tokens) >= 4 and
            tokens[0].type == TokenType.IDENTIFIER and
            tokens[1].value == '=' and
            tokens[-1].value == ';'):
            return "Assignment"

        # Rule 19-20: FuncCall -> ID ( ArgumentList ) ;
        if (tokens[0].type == TokenType.IDENTIFIER and
            tokens[1].value == '(' and 
            tokens[-1].value == ';'):
            return "FuncCall"

        # Rule 23: TrueForStmt -> TrueFor ( ConditionExpression ) Block
        if (len(tokens) >= 4 and
            tokens[0].value == 'TrueFor' and
            tokens[1].value == '(' and
            ')' in [t.value for t in tokens]):
            if 'Else' in [t.value for t in tokens]:
                return "TrueForStmt with Else"
            return "TrueForStmt"

        # Rule 25: HoweverStmt -> However ( ConditionExpression ) Block
        if (len(tokens) >= 4 and
            tokens[0].value == 'However' and
            tokens[1].value == '(' and
            ')' in [t.value for t in tokens] and
            tokens[-1].value == '{'):
            return "HoweverStmt"

        # Rule 26: WhenStmt -> When ( Expression ; Expression ; Expression ) Block
        if (len(tokens) >= 7 and
            tokens[0].value == 'When' and
            tokens[1].value == '(' and
            tokens[-1].value == '{'):
            return "WhenStmt"

        # Rule 27: RespondwithStmt -> Respondwith Expression ; | Respondwith ID ;
        if (len(tokens) >= 3 and
            tokens[0].value == 'Respondwith' and
            tokens[-1].value == ';'):
            return "RespondwithStmt"

        # Rule 28: EndthisStmt -> Endthis ;
        if (len(tokens) >= 2 and
            tokens[0].value == 'Endthis' and
            tokens[-1].value == ';'):
            return "EndthisStmt"

        # Rule 29: ScanStmt -> Scan(Conditionof ID) ;
        if (len(tokens) >= 4 and
            tokens[0].value == 'Scan' and
            tokens[1].value == '(' and
            'Conditionof' in [t.value for t in tokens] and
            tokens[-1].value == ';'):
            return "ScanStmt"

        # Rule 30: SrapStmt -> Srap ( Expression ) ;
        if (len(tokens) >= 4 and
            tokens[0].value == 'Srap' and
            tokens[1].value == '(' and
            tokens[-1].value == ';'):
            return "SrapStmt"

        # Rule 31: Block -> { Statements }
        if len(tokens) == 1 and tokens[0].value == '{':
            return "Block Start"
        if len(tokens) == 1 and tokens[0].value == '}':
            return "Block End"

        # Rule 34-35: Condition -> Expression ComparisonOp Expression
        if any(t.type == TokenType.RELATIONAL_OP for t in tokens):
            return "Condition"

        # Rule 32-33: ConditionExpression -> Condition | Condition LogicalOp Condition
        if any(t.type == TokenType.LOGIC_OP for t in tokens):
            return "ConditionExpression"

        # Rule 36-40: Expression operations
        if any(t.type == TokenType.ARITHMETIC_OP for t in tokens) and tokens[-1].value == ';':
            return "Expression Statement"

        # Rule 41: Comment
        if any(t.type == TokenType.COMMENT for t in tokens):
            return "Comment"

        # Rule 42: RequireCommand -> Require ( F_name.txt ) ;
        if (len(tokens) >= 1 and
            tokens[0].type == TokenType.INCLUSION and
            tokens[-1].value == ';'):
            return "Require Command"

        # End symbols (Rule 3)
        if len(tokens) == 1 and self.is_end_symbol(tokens[0]):
            return "End Symbol"

        return None

    def is_start_symbol(self, token):
        return token.type == TokenType.START_SYMBOL

    def is_end_symbol(self, token):
        return token.type == TokenType.END_SYMBOL

    def is_type(self, token):
        return token.type in [
            TokenType.INTEGER, TokenType.SINTEGER, TokenType.CHARACTER,
            TokenType.STRING, TokenType.FLOAT, TokenType.SFLOAT,
            TokenType.VOID, TokenType.BOOLEAN
        ]

    def print_report(self):
        for line in sorted(self.line_report):
            print(self.line_report[line])
        print(f"\nTotal NO of errors: {self.errors}")
