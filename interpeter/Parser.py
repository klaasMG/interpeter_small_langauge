from AstNode import VarNode , NumberNode , SetNode , DeclNode , PrintNode , BinOpNode , BoolNode
from interpeter.AstNode import IfNode, WhileNode
from tokenizer import Token , Tokens , KeyWords


def throw_syntax_error():
    raise Exception("syntax error")


class Parser:
    def __init__(self , tokens):
        self.i = 0
        self.tokens = tokens
    
    def peek_token(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None
    
    def get_token(self):
        tok: Token = self.peek_token()
        self.i += 1
        return tok
    
    def parse_program(self):
        statements = []
        while self.peek_token():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements
    
    def parse_statement(self):
        tok: Token = self.peek_token()
        if tok.token_type == KeyWords.Dec:
            return self.parse_dec()
        elif tok.token_type == KeyWords.Set:
            return self.parse_set()
        elif tok.token_type == KeyWords.If:
            return self.parse_if()
        elif tok.token_type == KeyWords.While:
            return self.parse_while()
        else:
            return None
        
    def parse_while(self):
        self.get_token()
        cond = self.parse_expr()
        if self.get_token().token_type != Tokens.LeftSquiglyBrace:
            raise Exception("hfj")
        body = self.parse_program()
        if self.get_token().token_type != Tokens.RightSquiglyBrace:
            raise Exception
        return WhileNode(cond,body)
    
    def parse_if(self):
        self.get_token()
        cond = self.parse_expr()
        if self.get_token().token_type != Tokens.LeftSquiglyBrace:
            raise Exception("{")
        body = self.parse_program()
        if self.get_token().token_type != Tokens.RightSquiglyBrace:
            raise Exception("}")
        if self.peek_token().token_type == KeyWords.Else:
            if self.get_token().token_type != Tokens.LeftSquiglyBrace:
                raise Exception("{")
            else_body = self.parse_program()
            if self.get_token().token_type != Tokens.RightSquiglyBrace:
                raise Exception("}")
        else:
            else_body = None
        
        return IfNode(cond,body,else_body)
    
    def parse_dec(self):
        self.get_token()
        var_type = self.get_token().token_type
        name = self.get_token().value
        eq = self.get_token()
        if eq.token_type != Tokens.Assign:
            raise Exception("Expected '='")
        expr = self.parse_expr()
        if self.get_token().token_type != Tokens.SemiColon:
            raise Exception("Expected ';'")
        return DeclNode(var_type , name , expr)
    
    def parse_set(self):
        self.get_token()
        name = self.get_token()
        eq = self.get_token()
        if eq.token_type != Tokens.Assign:
            raise Exception("=")
        expr = self.parse_expr()
        if self.get_token().token_type != Tokens.SemiColon:
            raise Exception(";")
        return SetNode(name , expr)
    
    def parse_print(self):
        self.get_token()
        if self.get_token().token_type != Tokens.LeftParentce:
            throw_syntax_error()
        expr = self.parse_expr()
        if self.get_token().token_type != Tokens.RightParentce:
            raise Exception("Expected ')'")
        if self.get_token().token_type != Tokens.SemiColon:
            raise Exception("Expected ';'")
        return PrintNode(expr)
    
    # Top-level expression parser (boolean OR)
    def parse_expr(self):
        return self.parse_or()
    
    def parse_or(self):
        left = self.parse_and()
        while self.peek_token() and self.peek_token().token_type == Tokens.Or:
            op = self.get_token().token_type
            right = self.parse_and()
            left = BinOpNode(left , op , right)
        return left
    
    def parse_and(self):
        left = self.parse_xor()
        while self.peek_token() and self.peek_token().token_type == Tokens.And:
            op = self.get_token().token_type
            right = self.parse_xor()
            left = BinOpNode(left , op , right)
        return left
    
    def parse_xor(self):
        left = self.parse_comparison()
        while self.peek_token() and self.peek_token().token_type == Tokens.Xor:
            op = self.get_token().token_type
            right = self.parse_comparison()
            left = BinOpNode(left , op , right)
        return left
    
    def parse_comparison(self):
        left = self.parse_add_sub()  # + / - layer
        if self.peek_token() and self.peek_token().token_type in [
            Tokens.Bigger , Tokens.Smaller , Tokens.Equal , Tokens.NotEqual
        ]:
            op = self.get_token().token_type
            right = self.parse_add_sub()
            left = BinOpNode(left , op , right)
        return left
    
    def parse_add_sub(self):
        left = self.parse_term()
        while self.peek_token() and self.peek_token().token_type in [Tokens.Add , Tokens.Sub]:
            op = self.get_token().token_type
            right = self.parse_term()
            left = BinOpNode(left , op , right)
        return left
    
    def parse_term(self):
        left = self.parse_factor()
        while self.peek_token() and self.peek_token().token_type in [Tokens.Mul , Tokens.Div]:
            op = self.get_token().token_type
            right = self.parse_factor()
            left = BinOpNode(left , op , right)
        return left
    
    def parse_factor(self):
        tok = self.get_token()
        if tok.token_type == Tokens.Number:
            return NumberNode(int(tok.value))
        elif tok.token_type in [Tokens.BoolTrue , Tokens.BoolFalse]:
            return BoolNode(tok.token_type == Tokens.BoolTrue)
        elif tok.token_type == Tokens.Ident:
            return VarNode(tok.value)
        elif tok.token_type == Tokens.LeftParentce:
            expr = self.parse_expr()
            if self.get_token().token_type != Tokens.RightParentce:
                raise Exception("Expected ')'")
            return expr
        else:
            raise Exception(f"Unexpected token in factor: {tok.token_type}")
