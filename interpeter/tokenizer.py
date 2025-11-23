from enum import Enum

class Tokens(Enum):
    Ident = "ident"
    Number = "number"
    BoolTrue = "True"
    BoolFalse = "False"
    Assign = "="
    Add = "+"
    Sub = "-"
    Mul = "*"
    Div = "/"
    Bigger = ">"
    Smaller = "<"
    Not = "!"
    Or = "||"
    And = "&&"
    Xor = "^^"
    SemiColon = ";"
    LeftParentce = "("
    RightParentce = ")"
    Equal = "=="
    LesThenOrEqual = ("<=", "=<")
    BiggerThenOrEqual = (">=","=>")
    NotEqual = "!="
    Increment = "++"
    Decrement = "--"
    AddToCurent = "+="
    SubToCurent = "-="
    MulToCurent = "*="
    DivToCurent = "/="
    RightShift = "<<"
    LeftShift = ">>"
    LeftSquiglyBrace = "{"
    RightSquiglyBrace = "}"

class KeyWords(Enum):
    Dec = "dec"
    Set = "set"
    Print = "print"
    Int = "int"
    Bool = "bool"
    If = "if"
    Else = "else"
    For = "for"
    While = "while"

class Token:
    def __init__(self, token_type, value = None):
        self.token_type = token_type
        self.value = value

class Tokenizer:
    def __init__(self, file):
        self.file = file
        self.i = 0
        self.expression_num = 0
        
    def next_char(self):
        if self.i >= len(self.file):
            return None
        ch = self.file[self.i]
        self.i += 1
        return ch
    
    def peek_char(self):
        if self.i >= len(self.file):
            return None
        ch = self.file[self.i]
        return ch
    
    @staticmethod
    def is_alpha(ch):
        return ch.isalpha() or ch == "_"
    
    @staticmethod
    def is_number(ch: str):
        return ch.isdigit()

    def tokenize(self):
        tokens = []
        while self.i < len(self.file):
            char = self.next_char()
            if char in [t.value for t in Tokens]:
                next_c = self.peek_char()
                # combine current char and next char if needed, e.g., for multi-char operators
                combined = char + (next_c if next_c else "")
                
                # check if combined is a valid token first
                token_type = next((t for t in Tokens if t.value == combined) , None)
                if token_type:
                    token = Token(token_type)
                    tokens.append(token)
                    if len(combined) == 2:  # we used next char as well
                        self.next_char()  # consume it
                else:
                    # fallback to single-character tokens
                    token_type = next(t for t in Tokens if t.value == char)
                    token = Token(token_type)
                    tokens.append(token)
            elif self.is_alpha(char):
                word = char
                while True:
                    next_c = self.peek_char()
                    if next_c is not None and self.is_alpha(next_c):
                        word += self.next_char()
                    else:
                        break
                    
                # check if word is a keyword
                keyword = next((k for k in KeyWords if k.value == word) , None)
                if keyword:
                    tokens.append(Token(keyword))
                    continue
                
                # 2. boolean literal?
                if word == "True":
                    tokens.append(Token(Tokens.BoolTrue , "True"))
                    continue
                elif word == "False":
                    tokens.append(Token(Tokens.BoolFalse , "False"))
                    continue
                
                # 3. otherwise identifier
                tokens.append(Token(Tokens.Ident , word))
            
            elif self.is_number(char):
                number = char
                while True:
                    next_c = self.peek_char()
                    if next_c is not None and self.is_number(next_c):
                        number += self.next_char()
                    else:
                        break
                
                tokens.append(Token(Tokens.Number,number))
            
            elif char.isspace():
                pass
            
            else:
                print("syntax error" + f"char {char}")
                
        return tokens