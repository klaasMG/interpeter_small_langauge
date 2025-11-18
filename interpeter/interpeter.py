class Variable:
    def __init__(self , type , name , value_stack_index , var_id):
        self.name = name
        self.value_stack_index = value_stack_index
        self.type = type
        self.var_id = var_id


class interpreter:
    def __init__(self):
        self.error = False
        self.value_stack = []
        self.value_type_stack = []
        self.variables = []
        self.variable_names_to_id = {}
        self.next_var_id = 0
    
    def run_code(self):
        self.interpret_code("code.txt")
    
    def parse_code(self , lines_of_code: list[str]):
        code_lines = []
        for line in lines_of_code:
            line = line.strip()  # <-- FIXED
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
        
        return code_lines
    
    def interpret_code(self, file):
        with open(file , "r") as code_file:
            read_lines = []
            for line in code_file:
                read_lines.append(line)
            code_lines = self.parse_code(read_lines)
            for line in code_lines:
                if not self.error:
                    if line.startswith("dec"):
                        line = line.split()
                        if line[3] != "=":
                            self.send_error("Syntax Error")
                            break
                        self.dec_variable(line[1] , line[2] , line[4:])
                    elif line.startswith("set"):
                        line = line.split()
                        if line[2] != "=":
                            self.send_error()
                            break
                    elif line.startswith("print"):
                        line = line[len("print"):].strip()
                        check = self.print_expression(line)
                        if check is None:
                            self.send_error("Syntax Error")
                    else:
                        self.send_error("Syntax Error")
                else:
                    break
    
    def pop_value(self):
        type = self.value_type_stack.pop()
        var = self.value_stack.pop()
        return type , var
    
    def push_value(self , type , value):
        self.value_type_stack.append(type)
        self.value_stack.append(value)
    
    def get_value(self , value_stack_index: int):
        value = self.value_stack[value_stack_index]
        type = self.value_type_stack[value_stack_index]
        return type , value
    
    def set_value(self , value_stack_index: int , type , value):
        if type != self.value_type_stack[value_stack_index]:
            self.send_error("Type Error")
            return None
        self.value_stack[value_stack_index] = value
        return True
    
    def dec_variable(self , type , name , value):
        var: Variable = Variable(type , name , len(self.value_stack) , self.next_var_id)
        self.next_var_id += 1
        check = self.solve_expression(value)
        self.variables.append(var)
        self.variable_names_to_id[name] = var.var_id
        value = self.pop_value()
        self.push_value(type , value[1])
    
    def get_variable(self , value_type: str , name: str):
        var_id = self.variable_names_to_id.get(name)
        if var_id is None:
            self.send_error(f"Variable {name} not found")
            return None
        var = self.variables[var_id]
        if var.type != value_type:
            self.send_error(f"Type Error: Expected {value_type}, got {var.type}")
            return None
        return var
    
    def print_expression(self , expression):
        Error: bool = False
        expression = expression.split()
        check = self.solve_expression(expression)
        if check is None:
            Error = True
        if Error:
            return None
        else:
            print(self.pop_value()[1])
            return True
    
    def solve_expression(self , expression):
        Error: bool = False
        posible_opperators = ["+" , "-" , "*" , "/" , "%" , ">>" , "<<"]
        opperator_stack = []
        if 1 == len(expression):
            if expression[0].lstrip("-").isdigit():
                self.push_value("int" , expression[0])
            elif expression[0] in self.variable_names_to_id:
                var = self.get_variable("int" , expression[0])
                if var is not None:
                    var_value = self.get_value(var.value_stack_index)
                    var_value = var_value[1]
                    self.push_value("int" , var_value)
                else:
                    Error = True
        else:
            for value in expression:
                if value in posible_opperators:
                    opperator_stack.append(value)
                elif value.lstrip("-").isdigit():
                    self.push_value("int" , value)
                elif value in self.variable_names_to_id:
                    var = self.get_variable("int" , value)
                    if var is not None:
                        var_value = self.get_value(var.value_stack_index)
                        var_value = var_value[1]
                        self.push_value("int" , var_value)
                    else:
                        Error = True
                        break
                else:
                    Error = True
                    break
            if not Error:
                val_first = self.pop_value()[1]
                result: int = int(val_first)
                result_str:str = ""
                while len(opperator_stack) > 0:
                    opperator = opperator_stack.pop()
                    val = self.pop_value()[1]
                    val = int(val)
                    if opperator == "+":
                        result = result + val
                    elif opperator == "-":
                        result = result - val
                    elif opperator == "*":
                        result = result * val
                    elif opperator == "/":
                        result = result // val
                    elif opperator == "%":
                        result = result % val
                    elif opperator == ">>":
                        result = result >> val
                    elif opperator == "<<":
                        result = result << val
                    else:
                        Error = True
                        break
                    result_str:str = str(result)
                self.push_value("int",result_str)
        if Error:
            return None
        else:
            return True
    
    def send_error(self , error_message: str | None = None):
        self.error = True
        if error_message:
            print(error_message)
        else:
            print("An error has occured")
            
interpreter_run = interpreter()
interpreter_run.run_code()