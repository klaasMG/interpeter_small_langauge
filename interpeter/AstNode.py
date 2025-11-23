class ASTNode:
    pass

# Leaf nodes
class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value
        
class BoolNode(ASTNode):
    def __init__(self, value):
        self.value = value

class VarNode(ASTNode):
    def __init__(self, name):
        self.name = name

# Internal nodes
class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.opp = op
        self.right = right

# Statements
class DeclNode(ASTNode):
    def __init__(self, var_type, name, expr):
        self.var_type = var_type
        self.name = name
        self.expr = expr

class SetNode(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class PrintNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr
        
class IfNode(ASTNode):
    def __init__(self, condition, if_block, else_block):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block