from enum import Enum

class TokenType(Enum):
    # Keywords
    CLASS = "Class"
    INHERITANCE = "Inheritance"
    CONDITION = "Condition"
    INTEGER = "Integer"
    SINTEGER = "SInteger"
    CHARACTER = "Character"
    STRING = "String"
    FLOAT = "Float"
    SFLOAT = "SFloat"
    VOID = "Void"
    BOOLEAN = "Boolean"
    BREAK = "Break"
    LOOP = "Loop"
    RETURN = "Return"
    STRUCT = "Struct"
    SWITCH = "Switch"
    INCLUSION = "Inclusion"

    # Symbols and Literals
    START_SYMBOL = "Stat Symbol"
    END_SYMBOL = "End Symbol"
    BRACES = "Braces"
    DELIMITER = "Delimiter"
    ACCESS_OP = "Access Operator"
    LOGIC_OP = "Logic operators"
    RELATIONAL_OP = "relational operators"
    ASSIGNMENT_OP = "Assignment operator"
    ARITHMETIC_OP = "Arithmetic Operation"
    QUOTATION = "Quotation Mark"
    COMMENT = "Comment"
    CONSTANT = "Constant"
    IDENTIFIER = "Identifier"
    ERROR = "Error"
    INVALID_TYPE = "InvalidType"

KEYWORDS = {
    'Type': TokenType.CLASS,
    'DerivedFrom': TokenType.INHERITANCE,
    'TrueFor': TokenType.CONDITION,
    'Else': TokenType.CONDITION,
    'Ity': TokenType.INTEGER,
    'Sity': TokenType.SINTEGER,
    'Cwq': TokenType.CHARACTER,
    'CwqSequence': TokenType.STRING,
    'Ifity': TokenType.FLOAT,
    'Sifity': TokenType.SFLOAT,
    'Valueless': TokenType.VOID,
    'Logical': TokenType.BOOLEAN,
    'Endthis': TokenType.BREAK,
    'However': TokenType.LOOP,
    'When': TokenType.LOOP,
    'Respondwith': TokenType.RETURN,
    'Srap': TokenType.STRUCT,
    'Scan': TokenType.SWITCH,
    'Conditionof': TokenType.SWITCH,
    'Require': TokenType.INCLUSION
}

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        type_name = self.type.value if isinstance(self.type, TokenType) else self.type
        return f"Token({type_name}, '{self.value}', line {self.line})"
