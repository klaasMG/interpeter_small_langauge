from enum import StrEnum, Enum, auto
from int_expr_parser import ExprParser
from tokenizer import Tokens, KeyWords, Token
from colorama import init, Fore

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

class Interpreter:
    def __init__(self):
        self.error = False
        self.value_stack: list[str] = []
        self.value_type_stack: list[Types] = []
        self.variables: list[Variable] = []
        self.variable_names_to_id = {}
        self.next_var_id = 0
        self.line_number = 0
        self.token_read = "how"
    
    def interpret_code(self , tokens):
        token_to_read = 0
        
        def next_token():
            nonlocal token_to_read
            self.token_read = token_to_read
            if token_to_read >= len(tokens):
                return None  # end of token list
            tok = tokens[token_to_read]
            token_to_read += 1
            return tok
        def invalid_token():
            nonlocal token_to_read
            token_to_read -= 1
        while token_to_read < len(tokens):
            token = next_token()
            if token.token_type == KeyWords.Dec:
                print("f")
                var_type_token = next_token()
                var_name_token = next_token()
                equals_token = next_token()
                
                print("DEBUG equals token:" , equals_token.token_type , "value:" , equals_token.value)
                if equals_token.token_type != Tokens.Equal:
                    self.send_error("hu")
                    break
                
                if var_type_token.token_type == KeyWords.Int:
                    var_type = Types.Int
                else:
                    self.send_error("Unknown variable type")
                    break
                    
                    # extract variable name string
                var_name = var_name_token.value if var_name_token.token_type == Tokens.Ident else None
                if var_name is None:
                    self.send_error("Expected variable name")
                    break
                expr: list[Token] = []
                is_valid = True
                while is_valid:
                    token = next_token()
                    if token.token_type == Tokens.SemiColon:
                        is_valid = False
                    else:
                        expr.append(token)
                invalid_token()
                result = self.solve_expression(expr)
                for value_type in Types:
                    if value_type == var_type:
                        var_type = value_type
                        break
                self.dec_variable(var_type, result,var_name)
            elif token.token_type == KeyWords.Set:
                print("l")
                var_name_token = next_token()
                var_name = var_name_token.value if var_name_token.token_type == Tokens.Ident else None
                if var_name is None:
                    self.send_error("Expected variable name")
                    break
                var_use = self.get_variable_by_name(var_name)
                var_type_token = var_use.type
                equals_token = next_token()
                if equals_token.token_type != Tokens.Equal:
                    self.send_error("hu")
                    break
                expr: list[Token] = []
                is_valid = True
                while is_valid:
                    token = next_token()
                    if token.token_type == Tokens.SemiColon:
                        is_valid = False
                    else:
                        expr.append(token)
                invalid_token()
                result = self.solve_expression(expr)
                for value_type in Types:
                    if value_type == var_type_token:
                        var_type_token = value_type
                        break
                self.set_variable(var_type_token , result , var_name)
            elif token.token_type == KeyWords.Print:
                left_parentece = next_token()
                if left_parentece.token_type != Tokens.LeftParentce:
                    self.send_error()
                    break
                expr: list[Token] = []
                is_valid = True
                while is_valid:
                    token = next_token()
                    if token.token_type == Tokens.RightParentce:
                        is_valid = False
                    else:
                        expr.append(token)
                invalid_token()
                right_parentece = next_token()
                if right_parentece.token_type != Tokens.RightParentce:
                    self.send_error("fg")
                    break
                result = self.solve_expression(expr)
                self.print_expression(result)
            semi_colon = next_token()
            if semi_colon.token_type != Tokens.SemiColon:
                self.send_error()
                break
    
    def solve_expression(self , expr: list[Token]):
        for i , token in enumerate(expr):
            if token.token_type == Tokens.Ident:
                var = self.get_variable_by_name(token.value)
                if var is None:
                    self.send_error(f"Unknown variable '{token.value}'")
                    return None
                value_type , value = self.get_value(var.value_stack_index)
                expr[i] = Token(Tokens.Number , value)
        parser = ExprParser(expr)
        ast = parser.parse_expr()
        result = self.eval_ast(ast)
        return str(result)
    
    def eval_ast(self , node):
        if isinstance(node , int):
            return node
        
        if isinstance(node , tuple):
            op = node[0]
            
            # variable lookup
            if op == "var":
                var = self.get_variable_by_name(node[1])
                if var is None:
                    self.send_error(f"Unknown variable {node[1]}")
                    return 0
                _ , val_str = self.get_value(var.value_stack_index)
                return int(val_str)
            
            # arithmetic
            left = self.eval_ast(node[1])
            right = self.eval_ast(node[2])
            
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/": return left // right  # integer division
        
        raise Exception("Unknown AST node")
            
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
        self.variable_names_to_id[name] = self.next_var_id
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
        var_id = self.variable_names_to_id[name]
        var = self.variables[var_id]
        var_value_type = var.type
        if var_value_type != value_type:
            return None
        return var
    
    def get_variable_by_name(self , name):
        if name not in self.variable_names_to_id:
            return None
        var_id = self.variable_names_to_id[name]
        var = self.variables[var_id]
        return var
    
    @staticmethod
    def print_expression(to_print):
        print(to_print)

    def send_error(self, error_message: str | None = None):
        self.error = True
        print(Fore.RED + f"Error at line {self.line_number}:")
        print(Fore.RED + f"Error at token {self.token_read}:")
        if error_message:
            print(Fore.RED + error_message)
        else:
            print(Fore.RED + "An unknown error occurred")
    
    def reset_interpeter(self):
        self.error = False
        self.value_stack = []
        self.value_type_stack = []
        self.variables = []
        self.variable_names_to_id = {}
        self.next_var_id = 0
        self.line_number = 0