from copy import deepcopy
from enum import StrEnum

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
    
class Types(StrEnum):
    Int = "int"
    Bool = "bool"

class Interpreter:
    def __init__(self):
        self.error = False
        self.value_stack = []
        self.value_type_stack = []
        self.variables = []
        self.variable_names_to_id = {}
        self.next_var_id = 0
    
    def run_code(self):
        langauge_is_running = True
        while langauge_is_running:
            command = input("What file to run:")
            command_lst = command.split()
            action = command_lst[0]
            if action != InterpeterActions.Done.value:
                file_use = command_lst[1]
                if action == InterpeterActions.Parse.value:
                    self.parse_code(file_use)
                elif action == InterpeterActions.Run.value:
                    self.parse_code(file_use)
                    self.interpret_code(file_use)
                else:
                    print("unknown command")
            elif action == InterpeterActions.Done.value:
                return
            else:
                print("unknown command")
    
    def parse_code(self, lines_of_code: str):
        
        code_lines = []  # for the return code lines
        read_lines = []
        with open(F"{lines_of_code}.code" , "r") as code_file:
            for line in code_file:
                read_lines.append(line)
        for line in read_lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(";")
            for p in parts:
                p = p.strip()
                if p:
                    code_lines.append(p)
        
        for index , expression in enumerate(code_lines):
            if expression.startswith("print("):
                expression = expression.replace("(" , " ")
                expression = expression.replace(")" , " ")
                code_lines[index] = expression
        
        for index, line in enumerate(code_lines):
            line:str = line
            if line.startswith("print"):
                expr: list = line.split()
                expr: list = expr[1:]
                operator_precedence = [["*" , "/" , "%"] , ["+" , "-"] , [">>" , "<<"] , ]
                operators = ["*" , "/" , "%" , "+" , "-" , ">>" , "<<"]
                operation = self.parse_expression(expr , operators , operator_precedence)
                replace = " ".join(expr)
                line = line.replace(replace , operation)
            elif line.startswith("set") or line.startswith("dec"):
                expr: list = line.split()
                expr: list = expr[4:]
                operator_precedence = [["*" , "/" , "%"] ,["+" , "-"] ,[">>" , "<<"],]
                operators = ["*" , "/" , "%","+" , "-",">>" , "<<"]
                operation = self.parse_expression(expr,operators,operator_precedence)
                replace = " ".join(expr)
                line = line.replace(replace, operation)
            else:
                line = line
            code_lines[index] = line
        
        with open(f"{lines_of_code}.run" , "w") as run_ready_file:
            for line in code_lines:
                run_ready_file.write(f"{line}\n")
    
    def parse_expression(self , tokens: list[str] , operators: list[str], operator_precedence: list[list[str]]):
        # separate nums and ops WITH THEIR ORIGINAL POSITIONS
        ops = []
        for i , tok in enumerate(tokens):
            if tok in operators:
                ops.append(i)
        
        # reorder ops by precedence
        ordered_ops = self.build_vov_tree([tokens[i] for i in ops] , operator_precedence)
        
        # build (val, opp, val) groups in correct evaluation order
        result = []
        results_stack = []  # for "r0", "r1", ...
        
        for op_index in ordered_ops:
            tok_pos = ops[op_index]  # position in tokens
            left_tok = tokens[tok_pos - 1]
            right_tok = tokens[tok_pos + 1]
            opp = tokens[tok_pos]
            
            # replace left with result ref if needed
            if left_tok.startswith("r"):
                left = left_tok
            else:
                left = left_tok
            
            # replace right with result ref if needed
            if right_tok.startswith("r"):
                right = right_tok
            else:
                right = right_tok
            
            result.append([left , opp , right])
            
            # store result reference for later replacements
            result_ref = f"r{len(results_stack)}"
            results_stack.append(result_ref)
            
            # rewrite tokens so later operations see the rX
            tokens[tok_pos] = result_ref
            tokens[tok_pos - 1] = result_ref
            tokens[tok_pos + 1] = result_ref
        
        return self.vov_to_string(result)
    
    @staticmethod
    def vov_to_string(vov_list):
        return ",\n".join(str(item) for item in vov_list)
    
    @staticmethod
    def build_vov_tree(opp_stack, precedence_groups):
        # Work on a copy so we don't destroy the original
        ops = deepcopy(opp_stack)
        order = []
        for group in precedence_groups:
            for i , op in enumerate(ops):
                if op in group:
                    order.append(i)
        return order
    
    def interpret_code(self , file):
        file_for_run = f"{file}.run"
        with open(file_for_run , "r") as code_file:
            read_lines = []
            for line in code_file:
                read_lines.append(line)
            for line_number, line in enumerate(read_lines):
                self.line_number = line_number
                if not self.error:
                    if line.startswith("dec"):
                        line = line.split()
                        if line[3] != "=":
                            self.send_error("Syntax Error")
                            break
                        self.dec_variable(line[1] , line[2] , line[4:])
                    elif line.startswith("set"):
                        line = line.split()
                        if line[3] != "=":
                            self.send_error("1")
                            break
                        check = self.set_variable(line[1] , line[2] , line[4:])
                        if check is None:
                            self.send_error("2")
                            break
                    elif line.startswith("print"):
                        line = line[len("print"):].strip()
                        check = self.print_expression(line)
                        if check is None:
                            self.send_error("Syntax Error")
                            break
                    else:
                        self.send_error("Syntax Error")
                        break
                else:
                    self.reset_interpeter()
                    break
    
    def pop_value(self):
        value_type = self.value_type_stack.pop()
        var = self.value_stack.pop()
        return value_type , var
    
    def push_value(self , value_type , value):
        self.value_type_stack.append(value_type)
        self.value_stack.append(value)
    
    def get_value(self , value_stack_index: int):
        value = self.value_stack[value_stack_index]
        value_type = self.value_type_stack[value_stack_index]
        return value_type , value
    
    def set_value(self , value_stack_index: int , value_type , value):
        if self.compare_type(value_type, value_stack_index):
            self.value_stack[value_stack_index] = value
            return True
        else:
            return None
    
    def get_type(self, value_stack_index):
        type_return = self.value_type_stack[value_stack_index]
        return type_return
    
    def compare_type(self, expected_type, value_stack_index):
        type_check = self.get_type(value_stack_index)
        if type_check != expected_type:
            return False
        return True
    
    @staticmethod
    def possible_type(type_check):
        if type_check in Types:
            return True
        else:
            return False
    
    def dec_variable(self , value_type , name , value):
        var: Variable = Variable(value_type , name , len(self.value_stack) , self.next_var_id)
        self.next_var_id += 1
        check = self.solve_expression(value, value_type)
        if check is None:
            self.send_error("3")
            return None
        self.variables.append(var)
        self.variable_names_to_id[name] = var.var_id
        value = self.pop_value()
        check_type = self.possible_type(value_type)
        if not check_type:
            self.send_error("4")
            return None
        self.push_value(value_type , value[1])
        return True
    
    def get_variable(self , value_type: str , name: str):
        var_id = self.variable_names_to_id.get(name)
        if var_id is None:
            self.send_error(f"Variable {name} not found")
            return None
        var = self.variables[var_id]
        if not self.compare_type(value_type, var.value_stack_index):
            self.send_error("5")
            return None
        return var
    
    def set_variable(self , value_type , name , expression):
        error = False
        var: Variable = self.get_variable(value_type , name)
        if var is None:
            error = True
            return None
        
        if not self.compare_type(value_type, var.value_stack_index):
            self.send_error("6")
            return None
        check = self.solve_expression(expression, value_type)
        if check is None:
            error = True
            return None
        set_value = self.pop_value()[1]
        self.set_value(var.value_stack_index , value_type , set_value)
        if error:
            return None
        else:
            return True
    
    def print_expression(self , expression):
        error: bool = False
        expression = expression.split()
        check = self.solve_expression(expression, Types.Int)
        if check is not None:
            print(self.pop_value()[1])
            return True
        else:
            self.send_error("7")
            return None
    
    @staticmethod
    def solve_vov_expression(value1 , opp , value2):
        value1 = int(value1)
        value2 = int(value2)
        if opp == "+":
            result = value1 + value2
        elif opp == "-":
            result = value1 - value2
        elif opp == "*":
            result = value1 * value2
        elif opp == "/":
            result = value1 // value2
        elif opp == "%":
            result = value1 % value2
        elif opp == ">>":
            result = value1 >> value2
        elif opp == "<<":
            result = value1 << value2
        else:
            return None
        return str(result)
    
    def send_error(self , error_message: str | None = None):
        self.error = True
        print(f"error line:{self.line_number}")
        if error_message:
            print(error_message)
        else:
            print("An error has occurred")
    
    def reset_interpeter(self):
        self.error = False
        self.value_stack = []
        self.value_type_stack = []
        self.variables = []
        self.variable_names_to_id = {}
        self.next_var_id = 0
        self.line_number = 0


interpreter_run = Interpreter()
interpreter_run.run_code()