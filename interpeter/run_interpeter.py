from enum import StrEnum, Enum, auto
from colorama import init, Fore

from interpeter.AstNode import IfNode
from tokenizer import Tokens
from AstNode import NumberNode, SetNode, VarNode, PrintNode, DeclNode, BinOpNode, BoolNode

init(autoreset=True)
class Variable:
    def __init__(self , var_type , name , value_stack_index , var_id):
        self.name = name
        self.value_stack_index = value_stack_index
        self.type = var_type
        self.var_id = var_id

class InterpeterActions(StrEnum):
    Run = "run"
    Parse = "parse"
    Done = "done"
    
class Types(Enum):
    Int = auto()
    Bool = auto()

class Interpreter:
    def __init__(self):
        self.error = False
        self.value_stack: list[str] = []
        self.value_type_stack: list[Types] = []
        self.variables: list[Variable] = []
        self.next_var_id = 0
        self.scopes: list[dict[str,int]] = [{}]
    
    def interpret_code(self , nodes):
        for node in nodes:
            if isinstance(node,IfNode):
                value_type, value = self.eval_expr(node.condition)
                if value_type != Types.Bool:
                    raise Exception("not the right output")
                if value:
                    body = node.if_block
                    self.interpret_code(body)
                else:
                    body = node.else_block
                    self.interpret_code(body)
            else:
                self.execute_statement(node)
            
    def execute_statement(self, node):
        if isinstance(node , DeclNode):
            value = self.eval_expr(node.expr)
            self.dec_variable(node.var_type , value[1] , node.name)
        elif isinstance(node , SetNode):
            value = self.eval_expr(node.expr)
            self.set_variable(value[0] , value[1] , node.name)
        elif isinstance(node , PrintNode):
            value = self.eval_expr(node.expr)
            self.print_expression(value[1])
                
    def eval_expr(self, expr):
        if isinstance(expr,VarNode):
            var = self.get_variable_by_name(expr.name)
            if var is None:
                raise Exception(f"Unknown variable {expr.name}")
            return self.get_value(var.value_stack_index)
        if isinstance(expr, BoolNode):
            return Types.Bool, bool(expr.value)
        if isinstance(expr, NumberNode):
            return Types.Int,int(expr.value)
        if isinstance(expr,BinOpNode):
            left = self.eval_expr(expr.left)
            opp = expr.opp
            right = self.eval_expr(expr.right)
            value_type_left , left = left
            
            value_type_right , right = right
            
            if value_type_right == value_type_left and value_type_right == Types.Int:
                if opp == Tokens.Add:
                    return Types.Int, left + right
                elif opp == Tokens.Sub:
                    return Types.Int, left - right
                elif opp == Tokens.Mul:
                    return Types.Int, left * right
                elif opp == Tokens.Div:
                    return Types.Int, left // right
                else:
                    raise Exception(f"Unknown operator {opp}")
                
            if value_type_right == value_type_left:
                if opp == Tokens.Bigger:
                    return Types.Bool, left > right
                elif opp == Tokens.Smaller:
                    return Types.Bool, left < right
                elif opp == Tokens.Equal:
                    return Types.Bool, left == right
                elif opp == Tokens.NotEqual:
                    return Types.Bool, left != right
                else:
                    raise Exception(f"Unknown operator {opp}")
            
            if value_type_right == value_type_left and value_type_right == Types.Bool:
                if opp == Tokens.And:
                    return Types.Bool, left and right
                elif opp == Tokens.Or:
                    return Types.Bool, left or right
                elif opp == Tokens.Xor:
                    return Types.Bool, left ^ right
                else:
                    raise Exception(f"Unknown operator {opp}")
                
            else:
                raise Exception(f"Unknown operator {opp}")
        else:
            raise Exception(f"Unknown")
    
    def push_scope(self):
        self.scopes.append({})
        
    def pop_scope(self):
        self.scopes.pop()
            
    def push_value(self, value_type, value):
        self.value_stack.append(value)
        self.value_type_stack.append(value_type)
        
    def pop_value(self):
        value = self.value_stack.pop()
        value_type = self.value_type_stack.pop()
        return value_type, value
    
    def set_value(self, value_type, value, value_stack_index:int):
        self.value_stack[value_stack_index] = value
        type_check:Types = self.value_type_stack[value_stack_index]
        if type_check != value_type:
            return None
        return True
    
    def get_value(self, value_stack_index: int):
        value = self.value_stack[value_stack_index]
        value_type = self.value_type_stack[value_stack_index]
        return value_type, value
    
    def dec_variable(self , value_type , value , name):
        self.scopes[-1][name] = self.next_var_id
        value_stack_index = len(self.value_stack)
        var: Variable = Variable(value_type , name , value_stack_index , self.next_var_id)
        self.push_value(value_type , value)
        self.variables.append(var)
        self.next_var_id += 1
    
    def set_variable(self , value_type , value , name):
        var = self.get_variable(value_type,name)
        if var is None:
            return None
        value_stack_index = var.value_stack_index
        self.value_stack[value_stack_index] = value
        return True
    
    def get_variable(self, value_type, name):
        var_id = self.resolve_variable(name)
        if not var_id:
            return None
        var = self.variables[var_id]
        var_value_type = var.type
        if var_value_type != value_type:
            return None
        return var
    
    def resolve_variable(self , name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def get_variable_by_name(self , name):
        var_id = self.resolve_variable(name)
        if not var_id:
            return None
        var = self.variables[var_id]
        return var
    
    @staticmethod
    def print_expression(to_print):
        print(to_print)

    def send_error(self, error_message: str | None = None):
        self.error = True
        if error_message:
            print(Fore.RED + error_message)
        else:
            print(Fore.RED + "An unknown error occurred")
    
    def reset_interpeter(self):
        self.error = False
        self.value_stack = []
        self.value_type_stack = []
        self.variables = []
        self.next_var_id = 0