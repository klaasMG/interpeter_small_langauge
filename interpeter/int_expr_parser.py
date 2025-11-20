from tokenizer import Tokens

# operator precedence
PRECEDENCE = {
    "+": 10,
    "-": 10,
    "*": 20,
    "/": 20,
}

class ExprParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self):
        if self.i >= len(self.tokens):
            return None
        return self.tokens[self.i]

    def next(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse_expr(self, min_bp=0):
        tok = self.next()

        # prefix / value
        if tok.token_type == Tokens.Number:
            left = int(tok.value)
        elif tok.token_type == Tokens.Ident:
            left = ("var", tok.value)
        else:
            raise Exception("Unexpected token in expression")

        # infix loop
        while True:
            op_tok = self.peek()
            if op_tok is None:
                break
            op = op_tok.token_type.value
            if op not in PRECEDENCE:
                break
            bp = PRECEDENCE[op]
            if bp < min_bp:
                break
            self.next()  # consume operator
            right = self.parse_expr(bp + 1)
            left = (op, left, right)

        return left