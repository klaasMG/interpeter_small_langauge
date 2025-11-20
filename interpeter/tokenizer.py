from enum import Enum

class Tokens(Enum):
    Ident = "ident"
    Number = "number"
    Space = " "
    Equal = "="
    Add = "+"
    Sub = "-"
    Mul = "*"
    Div = "/"
    Bigger = ">"
    Smaller = "<"
    Not = "!"
    Or = "|"
    And = "&"
    Xor = "^"
    SemiColon = ";"
    LeftParentce = "("
    RightParentce = ")"

class KeyWords(Enum):
    Dec = "dec"
    Set = "set"
    Print = "print"
    Int = "int"

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
        if self.i > len(self.file):
            return None
        ch = self.file[self.i]
        self.i += 1
        return ch
    
    @staticmethod
    def is_alpha(ch):
        return ch.isalpha() or ch == "_"
    
    @staticmethod
    def is_number(ch: str):
        return ch.isdigit()

    def tokenize(self):
        tokens = []
        char = "hold"
        while char is not None:
            char = self.next_char()
            if char in [t.value for t in Tokens]:
                token_type = next(t for t in Tokens if t.value == char)
                token = Token(token_type)
                tokens.append(token)
            elif self.is_alpha(char):
                word = char
                
                while self.is_alpha(self.file[self.i]):
                    word += self.next_char()
                    
                # check if word is a keyword
                keyword = next((k for k in KeyWords if k.value == word) , None)
                if keyword:
                    tokens.append(Token(keyword))
                else:
                    tokens.append(Token(Tokens.Ident , word))
            
            elif self.is_number(char):
                number = char
                while self.is_number(self.file[self.i]):
                    number += self.next_char()
                
                tokens.append(Token(Tokens.Number,number))
            
            elif char == Tokens.Space.value:
                pass
            
            else:
                print("syntax error")
                
        return tokens