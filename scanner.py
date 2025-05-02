#!/usr/bin/env python3

class Scanner:
    def __init__(self):
        # Dictionary of keywords with their corresponding token types
        self.keywords = {
            "Type": "Class",
            "DerivedFrom": "Inheritance",
            "TrueFor": "Condition",
            "Else": "Condition",
            "Ity": "Integer",
            "Sity": "SInteger",
            "Cwq": "Character",
            "CwqSequence": "String",
            "Ifity": "Float",
            "Sifity": "SFloat",
            "Valueless": "Void",
            "Logical": "Boolean",
            "Endthis": "Break",
            "However": "Loop",
            "When": "Loop",
            "Respondwith": "Return",
            "Srap": "Struct",
            "Scan": "Switch",
            "Conditionof": "Switch"
        }

        # Dictionary of special symbols
        self.special_symbols = {
            "@": "Start Symbol",
            "^": "Start Symbol",
            "$": "End Symbol",
            "#": "End Symbol",
            "+": "Arithmetic Operation",
            "-": "Arithmetic Operation",
            "*": "Arithmetic Operation",
            "/": "Arithmetic Operation",
            "&&": "Logic operators",
            "||": "Logic operators",
            "~": "Logic operators",
            "==": "relational operators",
            "<": "relational operators",
            ">": "relational operators",
            "!=": "relational operators",
            "<=": "relational operators",
            ">=": "relational operators",
            "=": "Assignment operator",
            "->": "Access Operator",
            "{": "Braces",
            "}": "Braces",
            "[": "Braces",
            "]": "Braces",
            "(": "Braces",
            ")": "Braces",
            ";": "Line Delimiter",
            ",": "Separator"
        }

        # Types in the language
        self.types = {
            "Ity", "Sity", "Cwq", "CwqSequence", "Ifity", "Sifity", "Valueless", "Logical"
        }

        # For tracking position in source code
        self.line_num = 1
        self.error_count = 0
        self.tokens = []
        self.included_files = set()  # Keep track of included files to avoid infinite recursion

    def is_digit(self, char):
        return char.isdigit()

    def is_letter(self, char):
        return char.isalpha()

    def is_whitespace(self, char):
        return char in [' ', '\t', '\n', '\r']

    def handle_require_statement(self, source_code, i):
        """Handle the Require command for file inclusion"""
        # Skip "Require" keyword
        while i < len(source_code) and source_code[i] != '(':
            i += 1

        if i >= len(source_code):
            self.add_error("Require", "Incomplete Require statement")
            return i

        i += 1  # Skip '('
        start = i

        # Find the file name
        while i < len(source_code) and source_code[i] != ')':
            i += 1

        if i >= len(source_code):
            self.add_error("Require", "Incomplete Require statement")
            return i

        file_name = source_code[start:i].strip()
        i += 1  # Skip ')'

        # Skip to the end of the statement
        while i < len(source_code) and source_code[i] != ';':
            i += 1

        if i < len(source_code):
            i += 1  # Skip ';'

        self.add_token(f"Require({file_name})", "Inclusion")

        # Process the included file if it's not already included
        if file_name not in self.included_files:
            try:
                self.included_files.add(file_name)
                with open(file_name, 'r') as file:
                    included_code = file.read()
                    # Store current line number
                    original_line_num = self.line_num
                    # Process the included file
                    self.scan(included_code)
                    # Restore original line number for continuing with the parent file
                    self.line_num = original_line_num
                    print(f"Successfully included file: {file_name}")
            except FileNotFoundError:
                print(f"Warning: File '{file_name}' not found for inclusion.")

        return i

    def check_for_using_command(self, source_code, line_start):
        """Check if the current line begins with a 'using' command"""
        i = line_start
        # Skip any whitespace at beginning of line
        while i < len(source_code) and self.is_whitespace(source_code[i]) and source_code[i] != '\n':
            i += 1

        # Check if line starts with "using"
        if i + 5 <= len(source_code) and source_code[i:i+5] == "using":
            # Found 'using' keyword at the beginning of line
            i += 5  # Skip 'using'
            
            # Skip whitespace after 'using'
            while i < len(source_code) and self.is_whitespace(source_code[i]) and source_code[i] != '\n':
                i += 1

            start = i
            # Read file name until end of line or whitespace
            while i < len(source_code) and not self.is_whitespace(source_code[i]):
                i += 1

            file_name = source_code[start:i].strip()
            
            # Process the included file
            self.add_token(f"using {file_name}", "File Inclusion")
            
            if file_name not in self.included_files:
                try:
                    self.included_files.add(file_name)
                    with open(file_name, 'r') as file:
                        included_code = file.read()
                        self.scan(included_code)
                except FileNotFoundError:
                    print(f"Warning: File '{file_name}' not found for inclusion. Continuing with current file.")
                    # Note: As per requirements, we just ignore the command if file not found
            
            # Skip to the end of line
            while i < len(source_code) and source_code[i] != '\n':
                i += 1
                
            if i < len(source_code):
                i += 1  # Skip the newline
                self.line_num += 1
                
            return True, i
            
        return False, line_start

    def scan(self, source_code):
        """Main scanning function that processes the input source code"""
        i = 0
        source_length = len(source_code)

        while i < source_length:
            # Check if we're at the beginning of a line for using command
            if i == 0 or (i > 0 and source_code[i-1] == '\n'):
                using_found, new_pos = self.check_for_using_command(source_code, i)
                if using_found:
                    i = new_pos
                    continue

            char = source_code[i]

            # Handle whitespace and line counting
            if char == '\n':
                self.line_num += 1
                i += 1
                continue
            elif self.is_whitespace(char):
                i += 1
                continue

            # Check for identifiers (keywords or user-defined IDs)
            if self.is_letter(char) or char == '_':
                start = i
                while i < source_length and (
                        self.is_letter(source_code[i]) or self.is_digit(source_code[i]) or source_code[i] == '_'):
                    i += 1

                word = source_code[start:i]

                # Check if it's a keyword
                if word in self.keywords:
                    self.add_token(word, self.keywords[word])
                # Handle the Require keyword for file inclusion
                elif word == "Require":
                    # Add the Require keyword as a token
                    self.add_token("Require", "File Inclusion Keyword")
                    i = self.handle_require_statement(source_code, i)
                    continue
                else:
                    self.add_token(word, "Identifier")
                continue

            # Check for numbers (constants)
            if self.is_digit(char):
                start = i
                has_decimal = False

                while i < source_length:
                    if source_code[i] == '.' and not has_decimal:
                        has_decimal = True
                        i += 1
                    elif self.is_digit(source_code[i]):
                        i += 1
                    else:
                        break

                number = source_code[start:i]
                self.add_token(number, "Constant")
                continue

            # Check for strings with double quotes
            if char == '"':
                start = i
                i += 1  # Skip opening quote
                while i < source_length and source_code[i] != '"':
                    if source_code[i] == '\n':
                        self.line_num += 1
                    i += 1

                if i >= source_length:
                    self.add_error(source_code[start:i], "Unterminated string")
                else:
                    i += 1  # Skip closing quote
                    string = source_code[start:i]
                    self.add_token(string, "String Literal")
                continue

            # Check for character literals with single quotes
            if char == "'":
                start = i
                i += 1  # Skip opening quote
                while i < source_length and source_code[i] != "'":
                    if source_code[i] == '\n':
                        self.line_num += 1
                    i += 1

                if i >= source_length:
                    self.add_error(source_code[start:i], "Unterminated character literal")
                else:
                    i += 1  # Skip closing quote
                    char_lit = source_code[start:i]
                    self.add_token(char_lit, "Character Literal")
                continue

            # Check for comments
            if char == '/' and i + 1 < source_length:
                if source_code[i + 1] == '*':  # Single line comment /*
                    start = i
                    i += 2  # Skip /*
                    while i < source_length and source_code[i] != '\n':
                        i += 1
                    comment = source_code[start:i]
                    self.add_token(comment, "Comment")
                    continue

                elif source_code[i + 1] == '<':  # Multi-line comment /<
                    start = i
                    i += 2  # Skip /<
                    end_found = False

                    while i < source_length - 1:
                        if source_code[i] == '>' and source_code[i + 1] == '/':
                            end_found = True
                            i += 2  # Skip >/
                            break
                        if source_code[i] == '\n':
                            self.line_num += 1
                        i += 1

                    if not end_found:
                        self.add_error(source_code[start:i], "Unterminated multi-line comment")
                    else:
                        comment = source_code[start:i]
                        self.add_token(comment, "Comment")
                    continue

            # Check for two-character operators
            if i + 1 < source_length:
                two_char = char + source_code[i + 1]
                if two_char in self.special_symbols:
                    self.add_token(two_char, self.special_symbols[two_char])
                    i += 2
                    continue

            # Check for single-character operators and symbols
            if char in self.special_symbols:
                self.add_token(char, self.special_symbols[char])
                i += 1
                continue

            # If we get here, the character is not recognized
            self.add_error(char, "Invalid token")
            i += 1

    def add_token(self, text, token_type):
        """Add a valid token to the token list"""
        self.tokens.append({
            'line': self.line_num,
            'text': text,
            'type': token_type
        })

    def add_error(self, text, error_msg=None):
        """Add an error token to the token list"""
        self.error_count += 1
        self.tokens.append({
            'line': self.line_num,
            'text': text,
            'type': 'ERROR',
            'error_msg': error_msg or "Invalid token"
        })

    def print_results(self):
        """Print the scanning results"""
        for token in self.tokens:
            if token['type'] == 'ERROR':
                print(f"Line #: {token['line']} Error in Token Text: {token['text']}")
            else:
                print(f"Line #: {token['line']} Token Text: {token['text']} Token Type: {token['type']}")

        print(f"Total NO of errors: {self.error_count}")

    def get_tokens(self):
        """Return the list of tokens for parser use"""
        return self.tokens


def process_file(filename):
    """Process a source code file with the scanner"""
    try:
        with open(filename, 'r') as file:
            source_code = file.read()

        scanner = Scanner()
        scanner.scan(source_code)
        scanner.print_results()
        return scanner.tokens

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        process_file(filename)
    else:
        print("Please provide a source code file as argument.")
        print("Usage: python scanner.py <source_file>")