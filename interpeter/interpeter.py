class Variable:
    def __init__(self, type, name, value_stack_index, var_id):
        self.name = name
        self.value_stack_index = value_stack_index
        self.type = type
        self.var_id = var_id
class interpreter:
    def __init__(self):
        self.error = False
        self.variable_stack = []
        self.var_to_id = {}
        self.next_var_id = 0
        self.value_stack = []
        self.value_type_stack = []
    def run_code(self):
        self.interpret_code()
    
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
        
        # Fix print(...) only AFTER splitting
        for index , expression in enumerate(code_lines):
            if expression.startswith("print("):
                expression = expression.replace("(" , " ")
                expression = expression.replace(")" , " ")
                code_lines[index] = expression
        
        return code_lines
    
    def interpret_code(self):
        with open("code.txt", "r") as code_file:
            read_lines = []
            for line in code_file:
                read_lines.append(line)
            code_lines = self.parse_code(read_lines)
            for line in code_lines:
                if not self.error:
                    if line.startswith("dec"):
                        line_command = line.split()
                        if line_command[3] != "=":
                            self.send_error("error")
                        self.variable_stack.append(Variable(line_command[1] , line_command[2] , len(self.value_stack) , self.next_var_id))
                        self.var_to_id[line_command[2]] = self.next_var_id
                        self.next_var_id += 1
                        var_lst = line_command[4:]
                        var = self.solve_expression(var_lst)
                        if var is None:
                            self.send_error("Error")
                            print("None Found")
                        else:
                            self.value_stack.append(int(var))
                            self.value_type_stack.append(line_command[1])
                    elif line.startswith("print"):
                        print_line = line.split(maxsplit = 1)
                        print_line = print_line[1]
                        if print_line.startswith('"') and print_line.endswith('"'):
                            str_for_print = print_line[1:-1]
                            print(str_for_print)
                        elif print_line == print_line.split()[0]:
                            str_for_print = self.get_var(print_line)
                            if str_for_print is None:
                                self.send_error()
                            else:
                                print(str_for_print)
                        else:
                            print_line = print_line.split()
                            self.solve_expression(print_line)
                else:
                    break
            print("Interpeter Debug:")
            for value in self.value_stack:
                print(value)
            for value in self.value_type_stack:
                print(value)
            
    def send_error(self,error_message=None):
        self.error = True
        if error_message is None:
            error_message = "Syntax Error"
        print(error_message)
        
    def get_var(self, variable_name):
        try:
            var = self.value_stack[self.variable_stack[self.var_to_id[variable_name]].value_stack_index]
        except KeyError:
            var = None
        return var
    
    def solve_expression(self, expression):
        if len(expression) == 1:
            return self.use_value(expression[0], int)
        elif len(expression) == 3:
            expr_vars = [self.use_value(expression[0], int),self.use_value(expression[2], int)]
            operator = expression[1]
            result = None
            if operator == "+":
                result = int(expr_vars[0]) + int(expr_vars[1])
            elif operator == "-":
                result = int(expr_vars[0]) - int(expr_vars[1])
            elif operator == "*":
                result = int(expr_vars[0]) * int(expr_vars[1])
            elif operator == "/":
                result = int(expr_vars[0]) / int(expr_vars[1])
            elif operator == "%":
                result = int(expr_vars[0]) % int(expr_vars[1])
            return result
        else:
            return None
        
    def use_value(self, value, expected_type):
        if value in self.var_to_id:
            use_value = self.value_stack[self.var_to_id[value]]
            if self.value_type_stack[self.var_to_id[value]] != str(expected_type):
                use_value = None
        else:
            use_value = value
            if self.get_type(use_value) != str(expected_type):
                print("f")
                use_value = None
            if expected_type == int:
                use_value = int(use_value)
        return use_value
    
    def get_type(self, value_type):
        value_type = int(value_type)
        value_type_check = self.value_type_stack[value_type]
        return value_type_check
    
interpreter_run = interpreter()
interpreter_run.interpret_code()