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
    
    @staticmethod
    def parse_code(lines_of_code: str):
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
        
        with open(f"{lines_of_code}.run" , "w") as run_ready_file:
            for line in code_lines:
                run_ready_file.write(f"{line}\n")
    
    def interpret_code(self , file):
        file_for_run = f"{file}.run"
        with open(file_for_run , "r") as code_file:
            read_lines = []
            for line in code_file:
                read_lines.append(line)
            for line in read_lines:
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
                            self.send_error()
                            break
                        check = self.set_variable(line[1] , line[2] , line[4:])
                        if check is None:
                            self.send_error()
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
        type_return = self.value_stack[value_stack_index]
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
            self.send_error()
            return None
        self.variables.append(var)
        self.variable_names_to_id[name] = var.var_id
        value = self.pop_value()
        check_type = self.possible_type(value_type)
        if not check_type:
            self.send_error()
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
            self.send_error()
            return None
        return var
    
    def set_variable(self , value_type , name , expression):
        error = False
        var: Variable = self.get_variable(value_type , name)
        if var is None:
            error = True
            return None
        
        if not self.compare_type(value_type, var.value_stack_index):
            self.send_error()
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
        check = self.solve_expression_int(expression)
        check_bool = self.solve_expression_boolean(expression)
        if (check is not None) or (check_bool is not None):
            print(self.pop_value()[1])
            return True
        else:
            self.send_error()
            return None
        
    def solve_expression(self, expression, expr_type):
        if expr_type == Types.Int:
            self.solve_expression_int(expression)
            return True
        elif expr_type == Types.Bool:
            self.solve_expression_boolean(expression)
            return True
        else:
            return None
    
    def solve_expression_int(self , expression):
        error: bool = False
        possible_opperators = ["+" , "-" , "*" , "/" , "%" , ">>" , "<<"]
        opperator_stack = []
        value_stack_opp = []
        if 1 == len(expression):
            if expression[0].lstrip("-").isdigit():
                self.push_value(Types.Int , expression[0])
            elif expression[0] in self.variable_names_to_id:
                var = self.get_variable(Types.Int , expression[0])
                if var is not None:
                    var_value = self.get_value(var.value_stack_index)
                    var_value = var_value[1]
                    self.push_value(Types.Int , var_value)
                else:
                    error = True
                    return None
        else:
            for value in expression:
                if value in possible_opperators:
                    opperator_stack.append(value)
                elif value.lstrip("-").isdigit():
                    value_stack_opp.append(value)
                elif value in self.variable_names_to_id:
                    var = self.get_variable(Types.Int , value)
                    if var is not None:
                        var_value = self.get_value(var.value_stack_index)
                        var_value = var_value[1]
                        value_stack_opp.append(var_value)
                    else:
                        error = True
                        break
                else:
                    error = True
                    break
            if not error:
                opperator_stack.reverse()
                value_stack_opp.reverse()
                precedence = self.build_vov_tree(opperator_stack)
                result_stack = []
                result_stack_len = 0
                print(f"value stack longer than opp stack{len(value_stack_opp) > len(opperator_stack)}")
                for operation in precedence:
                    operator = opperator_stack[operation]
                    value1:str = value_stack_opp[operation]
                    value_store1 = "pr"
                    value_store2 = "pr"
                    if value1.startswith("r"):
                        value1 = value1.replace("r","")
                        value_store1 = value1
                        value1 = result_stack[int(value1)]
                    value2:str = value_stack_opp[operation + 1]
                    if value2.startswith("r"):
                        value2 = value2.replace("r", "")
                        value_store2 = value2
                        value2 = result_stack[int(value2)]
                    result = self.solve_vov_expression(value1, operator, value2)
                    result_stack.append(result)
                    for index, value in enumerate(value_stack_opp):
                        value:str = value
                        if value.startswith("r"):
                            value_use = value.replace("r", "")
                            if value_use == value_store1 or value_use == value_store2:
                                value_use = f"r{result_stack_len}"
                                value_stack_opp[index] = value_use
                    value_stack_opp[operation] = f"r{result_stack_len}"
                    value_stack_opp[operation + 1] = f"r{result_stack_len}"
                    result_stack_len += 1
                result = result_stack[-1]
                self.push_value(Types.Int, result)
        if error:
            return None
        else:
            return True
        
    def solve_expression_boolean(self, expression):
        if len(expression) == 1:
            if expression[0] == "False" or expression[0] == "True":
                self.push_value(Types.Int , expression[0])
                return True
            elif expression[0] in self.variable_names_to_id:
                var = self.get_variable(Types.Bool , expression[0])
                if var is not None:
                    var_value = self.get_value(var.value_stack_index)
                    var_value = var_value[1]
                    self.push_value(Types.Int , var_value)
                    return True
                else:
                    error = True
                    return None
            else:
                return None
    
    @staticmethod
    def build_vov_tree(opp_stack):
        # Work on a copy so we don't destroy the original
        ops = deepcopy(opp_stack)
        order = []
        # operator precedence groups, in descending priority
        precedence_groups = [
            ["*" , "/" , "%"] ,
            ["+" , "-"] ,
            [">>" , "<<"] ,
        ]
        for group in precedence_groups:
            for i , op in enumerate(ops):
                if op in group:
                    order.append(i)
        return order
    
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


interpreter_run = Interpreter()
interpreter_run.run_code()