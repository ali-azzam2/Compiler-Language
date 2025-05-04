class ParseTreeNode:
    def __init__(self, rule, children=None, token=None):
        self.rule = rule
        self.children = children if children is not None else []
        self.token = token

    def __repr__(self, level=0):
        indent = '  ' * level
        s = f"{indent}{self.rule}"
        if self.token:
            s += f" (Token: {self.token})"
        s += '\n'
        for child in self.children:
            if isinstance(child, ParseTreeNode):
                s += child.__repr__(level + 1)
            else:
                s += f"{indent}  {child}\n"
        return s

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_token = None
        self.error_count = 0
        self.matched_rules = []
        self.parse_tree_root = None  # Store the root of the parse tree
        
        # Initialize with first token if available
        if tokens:
            self.current_token = tokens[0]

    def advance(self):
        """Move to the next token"""
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def match(self, token_type=None, token_text=None):
        """Match the current token against expected type or text"""
        if not self.current_token:
            return False
            
        matches = True
        if token_type and self.current_token['type'] != token_type:
            matches = False
        if token_text and self.current_token['text'] != token_text:
            matches = False
            
        if matches:
            self.advance()
            return True
        return False

    def expect(self, token_type=None, token_text=None, rule=None):
        """Expect a certain token, report error if not found"""
        if self.match(token_type, token_text):
            if rule:
                self.add_matched_rule(rule)
            return True
        else:
            self.add_error()
            return False

    def add_matched_rule(self, rule):
        """Add a matched rule to the list"""
        line_num = self.current_token['line'] if self.current_token else 0
        if self.index > 0 and self.index <= len(self.tokens):
            line_num = self.tokens[self.index - 1]['line']
        self.matched_rules.append({
            'line': line_num,
            'rule': rule
        })

    def add_error(self):
        """Add an error to the count"""
        self.error_count += 1
        line_num = self.current_token['line'] if self.current_token else 0
        self.matched_rules.append({
            'line': line_num,
            'rule': 'Not Matched'
        })

    def print_results(self):
        """Print the parsing results in line order"""
        # Sort by line number
        sorted_results = sorted(self.matched_rules, key=lambda x: x['line'])
        for result in sorted_results:
            if result['rule'] == 'Not Matched':
                print(f"Line #: {result['line']} Not Matched")
            else:
                print(f"Line #: {result['line']} Matched Rule Used: {result['rule']}")
        print(f"Total NO of errors: {self.error_count}")

    # Grammar rule implementations
    def parse(self):
        """Start parsing with the Program rule, continue on error."""
        self.parse_tree_root = None
        while self.current_token:
            node = self.program()
            if self.parse_tree_root is None and node:
                self.parse_tree_root = node
            # If not at the end, advance to avoid infinite loop
            if self.current_token:
                self.advance()
        return self.matched_rules, self.error_count
    
    def program(self):
        """Program -> Start_Symbols ClassDeclaration End_Symbols"""
        children = []
        start = self.start_symbols()
        if start:
            children.append(start)
            self.add_matched_rule("Program -> Start_Symbols ClassDeclaration End_Symbols")
            class_decl = self.class_declaration()
            if class_decl:
                children.append(class_decl)
            end = self.end_symbols()
            if end:
                children.append(end)
            return ParseTreeNode("Program", children)
        else:
            self.add_error()
            return None
    
    def start_symbols(self):
        """Start_Symbols -> @ | ^"""
        if self.match(token_text='@'):
            self.add_matched_rule("Start_Symbols -> @ | ^")
            return ParseTreeNode("Start_Symbols", token='@')
        elif self.match(token_text='^'):
            self.add_matched_rule("Start_Symbols -> @ | ^")
            return ParseTreeNode("Start_Symbols", token='^')
        else:
            return None
    
    def end_symbols(self):
        """End_Symbols -> $ | #"""
        if self.match(token_text='$'):
            self.add_matched_rule("End_Symbols -> $ | #")
            return ParseTreeNode("End_Symbols", token='$')
        elif self.match(token_text='#'):
            self.add_matched_rule("End_Symbols -> $ | #")
            return ParseTreeNode("End_Symbols", token='#')
        else:
            self.add_error()
            return None
    
    def class_declaration(self):
        """ClassDeclaration -> Type ID ClassBody | Type ID DerivedFrom ClassBody"""
        children = []
        t = self.type()
        if t:
            children.append(t)
            if self.match(token_type="Identifier"):
                children.append(ParseTreeNode("ID", token=self.tokens[self.index-1]['text']))
                if self.match(token_text="DerivedFrom"):
                    self.add_matched_rule("ClassDeclaration -> Type ID DerivedFrom ClassBody")
                    # Should match another identifier here for inherited class
                    if self.match(token_type="Identifier"):
                        children.append(ParseTreeNode("ID", token=self.tokens[self.index-1]['text']))
                    cb = self.class_body()
                    if cb:
                        children.append(cb)
                    return ParseTreeNode("ClassDeclaration", children)
                else:
                    self.add_matched_rule("ClassDeclaration -> Type ID ClassBody")
                    cb = self.class_body()
                    if cb:
                        children.append(cb)
                    return ParseTreeNode("ClassDeclaration", children)
            else:
                self.add_error()
        else:
            self.add_error()
        return None
    
    def class_body(self):
        """ClassBody -> { ClassMembers }"""
        children = []
        if self.match(token_text='{'):
            self.add_matched_rule("ClassBody -> { ClassMembers }")
            cm = self.class_members()
            if cm:
                children.append(cm)
            if not self.match(token_text='}'):
                self.add_error()
            return ParseTreeNode("ClassBody", children)
        else:
            self.add_error()
            return None
    
    def class_members(self):
        """ClassMembers -> ClassMember ClassMembers | ε"""
        children = []
        while self.current_token and self.current_token['text'] != '}':
            cm = self.class_member()
            if cm:
                self.add_matched_rule("ClassMembers -> ClassMember ClassMembers")
                children.append(cm)
            else:
                self.add_error()
                self.advance()  # Error recovery: skip to next token
        if children:
            return ParseTreeNode("ClassMembers", children)
        else:
            return None
    
    def class_member(self):
        """ClassMember -> VariableDecl | MethodDecl | FuncCall | Comment | RequireCommand"""
        token_type = self.current_token['type'] if self.current_token else None
        token_text = self.current_token['text'] if self.current_token else None
        
        if token_type == "Comment":
            self.add_matched_rule("ClassMember -> Comment")
            self.comment()
            return ParseTreeNode("Comment")
        elif token_text == "Require":
            self.add_matched_rule("ClassMember -> RequireCommand")
            self.require_command()
            return ParseTreeNode("RequireCommand")
        elif token_type == "Identifier" and self.peek_next_token_text() == '(':
            self.add_matched_rule("ClassMember -> FuncCall")
            self.func_call()
            return ParseTreeNode("FuncCall")
        elif self.is_type_token(token_text):
            # Check if this is variable or method declaration
            # Look ahead to see if there's a "(" after the identifier
            self.add_matched_rule("ClassMember -> VariableDecl")
            saved_index = self.index
            saved_token = self.current_token
            
            # Try method declaration first
            if self.method_decl():
                return ParseTreeNode("MethodDecl")
                
            # If method_decl failed, reset and try variable_decl
            self.index = saved_index
            self.current_token = saved_token
            
            if self.variable_decl():
                return ParseTreeNode("VariableDecl")
            
            self.add_error()
            return None
        else:
            return None
    
    def peek_next_token_text(self):
        """Look ahead to the next token text without advancing"""
        if self.index + 1 < len(self.tokens):
            return self.tokens[self.index + 1]['text']
        return None

    def peek_token_ahead(self, positions=1):
        """Look ahead to a token without advancing"""
        if self.index + positions < len(self.tokens):
            return self.tokens[self.index + positions]
        return None
        
    def method_decl(self):
        """MethodDecl -> FuncDecl ; | FuncDecl { VariableDecls Statements }"""
        saved_index = self.index
        saved_token = self.current_token
        
        if self.func_decl():
            if self.match(token_text=';'):
                self.add_matched_rule("MethodDecl -> FuncDecl ;")
                return True
            elif self.match(token_text='{'):
                self.add_matched_rule("MethodDecl -> FuncDecl { VariableDecls Statements }")
                self.variable_decls()
                self.statements()
                if self.match(token_text='}'):
                    return True
                else:
                    self.add_error()
                    return False
            else:
                self.add_error()
                return False
        
        # Reset if we couldn't match method_decl
        self.index = saved_index
        self.current_token = saved_token
        return False
    
    def func_decl(self):
        """FuncDecl -> Type ID ( ParameterList )"""
        if self.type():
            if self.match(token_type="Identifier"):
                if self.match(token_text='('):
                    self.add_matched_rule("FuncDecl -> Type ID ( ParameterList )")
                    self.parameter_list()
                    if self.match(token_text=')'):
                        return True
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def parameter_list(self):
        """ParameterList -> ε | Parameters"""
        if self.current_token and self.current_token['text'] != ')':
            self.add_matched_rule("ParameterList -> Parameters")
            self.parameters()
        else:
            self.add_matched_rule("ParameterList -> ε")
            # epsilon case - do nothing
    
    def parameters(self):
        """Parameters -> Parameter | Parameters , Parameter"""
        if self.parameter():
            if self.current_token and self.current_token['text'] == ',':
                self.match(token_text=',')
                self.add_matched_rule("Parameters -> Parameters , Parameter")
                self.parameters()
            else:
                self.add_matched_rule("Parameters -> Parameter")
        else:
            self.add_error()
    
    def parameter(self):
        """Parameter -> Type ID"""
        if self.type():
            if self.match(token_type="Identifier"):
                self.add_matched_rule("Parameter -> Type ID")
                return True
            else:
                self.add_error()
        return False
    
    def variable_decl(self):
        """VariableDecl -> Type IDList ; | Type IDList [ ID ] ;"""
        if self.type():
            if self.id_list():
                if self.current_token and self.current_token['text'] == '[':
                    self.match(token_text='[')
                    if self.match(token_type="Identifier"):
                        if self.match(token_text=']'):
                            if self.match(token_text=';'):
                                self.add_matched_rule("VariableDecl -> Type IDList [ ID ] ;")
                                return True
                            else:
                                self.add_error()
                        else:
                            self.add_error()
                    else:
                        self.add_error()
                elif self.match(token_text=';'):
                    self.add_matched_rule("VariableDecl -> Type IDList ;")
                    return True
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def variable_decls(self):
        """VariableDecls -> VariableDecl VariableDecls | ε"""
        if self.current_token and self.is_type_token(self.current_token['text']):
            if self.variable_decl():
                self.add_matched_rule("VariableDecls -> VariableDecl VariableDecls")
                self.variable_decls()
            else:
                self.add_error()
        else:
            # epsilon case - do nothing
            pass
    
    def id_list(self):
        """IDList -> ID | IDList , ID"""
        if self.match(token_type="Identifier"):
            if self.current_token and self.current_token['text'] == ',':
                self.match(token_text=',')
                self.add_matched_rule("IDList -> IDList , ID")
                self.id_list()
            else:
                self.add_matched_rule("IDList -> ID")
            return True
        return False
    
    def statements(self):
        """Statements -> Statement Statements | ε"""
        while self.current_token and self.current_token['text'] != '}':
            if self.statement():
                self.add_matched_rule("Statements -> Statement Statements")
            else:
                self.add_error()
                self.advance()  # Error recovery: skip to next token
        # epsilon case - do nothing if '}'
    
    def statement(self):
        """Handles different statement types"""
        token_text = self.current_token['text'] if self.current_token else None
        token_type = self.current_token['type'] if self.current_token else None
        
        if token_type == "Identifier" and self.peek_token_ahead() and self.peek_token_ahead()['text'] == '=':
            self.add_matched_rule("Statement -> Assignment")
            return self.assignment()
        elif token_text == "TrueFor":
            self.add_matched_rule("Statement -> TrueForStmt")
            return self.truefor_stmt()
        elif token_text == "However":
            self.add_matched_rule("Statement -> HoweverStmt")
            return self.however_stmt()
        elif token_text == "When":
            self.add_matched_rule("Statement -> WhenStmt")
            return self.when_stmt()
        elif token_text == "Respondwith":
            self.add_matched_rule("Statement -> RespondwithStmt")
            return self.respondwith_stmt()
        elif token_text == "Endthis":
            self.add_matched_rule("Statement -> EndthisStmt")
            return self.endthis_stmt()
        elif token_text == "Scan" or token_text == "Conditionof":
            self.add_matched_rule("Statement -> ScanStmt")
            return self.scan_stmt()
        elif token_text == "Srap":
            self.add_matched_rule("Statement -> SrapStmt")
            return self.srap_stmt()
        elif token_type == "Identifier" and self.peek_token_ahead() and self.peek_token_ahead()['text'] == '(':
            self.add_matched_rule("Statement -> FuncCallStmt")
            return self.func_call_stmt()
        else:
            return False
    
    def assignment(self):
        """Assignment -> ID = Expression ;"""
        if self.match(token_type="Identifier"):
            if self.match(token_text='='):
                self.add_matched_rule("Assignment -> ID = Expression ;")
                if self.expression():
                    if self.match(token_text=';'):
                        return True
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def func_call(self):
        """FuncCall -> ID ( ArgumentList ) ;"""
        if self.match(token_type="Identifier"):
            if self.match(token_text='('):
                self.add_matched_rule("FuncCall -> ID ( ArgumentList ) ;")
                self.argument_list()
                if self.match(token_text=')'):
                    if self.match(token_text=';'):
                        return True
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def func_call_stmt(self):
        """FuncCallStmt -> FuncCall ;"""
        if self.func_call():
            self.add_matched_rule("FuncCallStmt -> FuncCall ;")
            return True
        return False
    
    def argument_list(self):
        """ArgumentList -> ε | ArgumentSequence"""
        if self.current_token and self.current_token['text'] != ')':
            self.add_matched_rule("ArgumentList -> ArgumentSequence")
            self.argument_sequence()
        else:
            self.add_matched_rule("ArgumentList -> ε")
            # epsilon case - do nothing
    
    def argument_sequence(self):
        """ArgumentSequence -> Expression | ArgumentSequence , Expression"""
        if self.expression():
            if self.current_token and self.current_token['text'] == ',':
                self.match(token_text=',')
                self.add_matched_rule("ArgumentSequence -> ArgumentSequence , Expression")
                self.argument_sequence()
            else:
                self.add_matched_rule("ArgumentSequence -> Expression")
        else:
            self.add_error()
    
    def truefor_stmt(self):
        """TrueForStmt -> TrueFor ( ConditionExpression ) Block
                           | TrueFor ( ConditionExpression ) Block TrueForElse Block"""
        if self.match(token_text="TrueFor"):
            if self.match(token_text='('):
                if self.condition_expression():
                    if self.match(token_text=')'):
                        if self.block():
                            # Check for else part
                            if self.current_token and self.current_token['text'] == "Else":
                                self.truefor_else()
                                if self.block():
                                    self.add_matched_rule("TrueForStmt -> TrueFor ( ConditionExpression ) Block TrueForElse Block")
                                    return True
                                else:
                                    self.add_error()
                            else:
                                self.add_matched_rule("TrueForStmt -> TrueFor ( ConditionExpression ) Block")
                                return True
                        else:
                            self.add_error()
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def truefor_else(self):
        """TrueForElse -> Else"""
        if self.match(token_text="Else"):
            self.add_matched_rule("TrueForElse -> Else")
            return True
        return False
    
    def however_stmt(self):
        """HoweverStmt -> However ( ConditionExpression ) Block"""
        if self.match(token_text="However"):
            if self.match(token_text='('):
                if self.condition_expression():
                    if self.match(token_text=')'):
                        if self.block():
                            self.add_matched_rule("HoweverStmt -> However ( ConditionExpression ) Block")
                            return True
                        else:
                            self.add_error()
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def when_stmt(self):
        """WhenStmt -> When ( Expression ; Expression ; Expression ) Block"""
        if self.match(token_text="When"):
            if self.match(token_text='('):
                if self.expression():
                    if self.match(token_text=';'):
                        if self.expression():
                            if self.match(token_text=';'):
                                if self.expression():
                                    if self.match(token_text=')'):
                                        if self.block():
                                            self.add_matched_rule("WhenStmt -> When ( Expression ; Expression ; Expression ) Block")
                                            return True
                                        else:
                                            self.add_error()
                                    else:
                                        self.add_error()
                                else:
                                    self.add_error()
                            else:
                                self.add_error()
                        else:
                            self.add_error()
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def respondwith_stmt(self):
        """RespondwithStmt -> Respondwith Expression ; | Respondwith ID ;"""
        if self.match(token_text="Respondwith"):
            if self.current_token and self.current_token['type'] == "Identifier":
                if self.match(token_type="Identifier"):
                    if self.match(token_text=';'):
                        self.add_matched_rule("RespondwithStmt -> Respondwith ID ;")
                        return True
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                if self.expression():
                    if self.match(token_text=';'):
                        self.add_matched_rule("RespondwithStmt -> Respondwith Expression ;")
                        return True
                    else:
                        self.add_error()
                else:
                    self.add_error()
        return False
    
    def endthis_stmt(self):
        """EndthisStmt -> Endthis ;"""
        if self.match(token_text="Endthis"):
            if self.match(token_text=';'):
                self.add_matched_rule("EndthisStmt -> Endthis ;")
                return True
            else:
                self.add_error()
        return False
    
    def scan_stmt(self):
        """ScanStmt -> Scan(Conditionof ID) ;"""
        if self.match(token_text="Scan"):
            if self.match(token_text='('):
                if self.match(token_text="Conditionof"):
                    if self.match(token_type="Identifier"):
                        if self.match(token_text=')'):
                            if self.match(token_text=';'):
                                self.add_matched_rule("ScanStmt -> Scan(Conditionof ID) ;")
                                return True
                            else:
                                self.add_error()
                        else:
                            self.add_error()
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def srap_stmt(self):
        """SrapStmt -> Srap ( Expression ) ;"""
        if self.match(token_text="Srap"):
            if self.match(token_text='('):
                if self.expression():
                    if self.match(token_text=')'):
                        if self.match(token_text=';'):
                            self.add_matched_rule("SrapStmt -> Srap ( Expression ) ;")
                            return True
                        else:
                            self.add_error()
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def block(self):
        """Block -> { Statements }"""
        if self.match(token_text='{'):
            self.add_matched_rule("Block -> { Statements }")
            self.statements()
            if self.match(token_text='}'):
                return True
            else:
                self.add_error()
                return False
        else:
            self.add_error()
            return False
    
    def condition_expression(self):
        """ConditionExpression -> Condition | Condition LogicalOp Condition"""
        if self.condition():
            if self.current_token and self.is_logical_op(self.current_token['text']):
                logical_op = self.current_token['text']
                self.match(token_text=logical_op)
                if self.condition():
                    self.add_matched_rule("ConditionExpression -> Condition LogicalOp Condition")
                    return True
                else:
                    self.add_error()
                    return False
            else:
                self.add_matched_rule("ConditionExpression -> Condition")
                return True
        return False
    
    def is_logical_op(self, text):
        """Check if token is a logical operator"""
        return text in ['&&', '||', '~']
    
    def condition(self):
        """Condition -> Expression ComparisonOp Expression"""
        if self.expression():
            if self.current_token and self.is_comparison_op(self.current_token['text']):
                comp_op = self.current_token['text']
                self.match(token_text=comp_op)
                if self.expression():
                    self.add_matched_rule("Condition -> Expression ComparisonOp Expression")
                    return True
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def is_comparison_op(self, text):
        """Check if token is a comparison operator"""
        return text in ['==', '!=', '>', '>=', '<', '<=']
    
    def expression(self):
        """Expression -> Term | Expression AddOp Term"""
        if self.term():
            if self.current_token and self.is_add_op(self.current_token['text']):
                add_op = self.current_token['text']
                self.match(token_text=add_op)
                if self.term():
                    self.add_matched_rule("Expression -> Expression AddOp Term")
                    # Check for more terms
                    self.handle_more_terms()
                    return True
                else:
                    self.add_error()
                    return False
            else:
                self.add_matched_rule("Expression -> Term")
                return True
        return False
    
    def handle_more_terms(self):
        """Helper method to handle expressions with multiple terms"""
        while self.current_token and self.is_add_op(self.current_token['text']):
            add_op = self.current_token['text']
            self.match(token_text=add_op)
            if not self.term():
                self.add_error()
                break
            self.add_matched_rule("Expression -> Expression AddOp Term")
    
    def is_add_op(self, text):
        """Check if token is an addition operator"""
        return text in ['+', '-']
    
    def term(self):
        """Term -> Factor | Term MulOp Factor"""
        if self.factor():
            if self.current_token and self.is_mul_op(self.current_token['text']):
                mul_op = self.current_token['text']
                self.match(token_text=mul_op)
                if self.factor():
                    self.add_matched_rule("Term -> Term MulOp Factor")
                    # Check for more factors
                    self.handle_more_factors()
                    return True
                else:
                    self.add_error()
                    return False
            else:
                self.add_matched_rule("Term -> Factor")
                return True
        return False
    
    def handle_more_factors(self):
        """Helper method to handle terms with multiple factors"""
        while self.current_token and self.is_mul_op(self.current_token['text']):
            mul_op = self.current_token['text']
            self.match(token_text=mul_op)
            if not self.factor():
                self.add_error()
                break
            self.add_matched_rule("Term -> Term MulOp Factor")
    
    def is_mul_op(self, text):
        """Check if token is a multiplication operator"""
        return text in ['*', '/']
    
    def factor(self):
        """Factor -> ID | Number | ( Expression )"""
        if not self.current_token:
            return False
            
        token_type = self.current_token['type']
        
        if token_type == "Identifier":
            self.match(token_type="Identifier")
            self.add_matched_rule("Factor -> ID")
            return True
        elif token_type == "Constant":
            self.match(token_type="Constant")
            self.add_matched_rule("Factor -> Number")
            return True
        elif self.current_token['text'] == '(':
            self.match(token_text='(')
            if self.expression():
                if self.match(token_text=')'):
                    self.add_matched_rule("Factor -> ( Expression )")
                    return True
                else:
                    self.add_error()
            else:
                self.add_error()
        
        return False
    
    def comment(self):
        """Comment -> /< STR >/ | /* STR"""
        if self.match(token_type="Comment"):
            self.add_matched_rule("Comment -> /< STR >/ | /* STR")
            return True
        return False
    
    def require_command(self):
        """RequireCommand -> Require ( F_name.txt ) ;"""
        if self.match(token_text="Require"):
            if self.match(token_text='('):
                # Need to check for filename
                if self.current_token and self.current_token['type'] == "Identifier":
                    self.match(token_type="Identifier")
                    if self.match(token_text=')'):
                        if self.match(token_text=';'):
                            self.add_matched_rule("RequireCommand -> Require ( F_name.txt ) ;")
                            return True
                        else:
                            self.add_error()
                    else:
                        self.add_error()
                else:
                    self.add_error()
            else:
                self.add_error()
        return False
    
    def type(self):
        """Type -> Ity | Sity | Cwq | CwqSequence | Ifity | Sifity | Valueless | Logical"""
        if self.current_token and self.is_type_token(self.current_token['text']):
            self.match(token_text=self.current_token['text'])
            self.add_matched_rule("Type -> Ity | Sity | Cwq | CwqSequence | Ifity | Sifity | Valueless | Logical")
            return True
        return False
    
    def is_type_token(self, text):
        """Check if token is a type"""
        return text in ["Ity", "Sity", "Cwq", "CwqSequence", "Ifity", "Sifity", "Valueless", "Logical", "Type"]


def process_file(filename):
    """Process a source code file with the scanner and parser"""
    try:
        with open(filename, 'r') as file:
            source_code = file.read()

        # Scanning phase
        scanner = Scanner()
        scanner.scan(source_code)
        scanner.print_results()
        tokens = scanner.get_tokens()
        
        # Parsing phase
        parser = Parser(tokens)
        parser.parse()
        parser.print_results()
        
        return tokens, parser.matched_rules
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return [], []