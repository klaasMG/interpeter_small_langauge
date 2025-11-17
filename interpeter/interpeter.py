class Variable:
    def __init__(self, type, name, valeu_stack_index, var_id):
        self.name = name
        self.valeu_stack_index = valeu_stack_index
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
    def interpret_code(self):
        with open("code.txt", "r") as code_file:
            read_lines = []
            for line in code_file:
                read_lines.append(line)
            for line in read_lines:
                if not self.error:
                    line_commands = line.split()
                    for line_command in line_commands:
                        if line_command == "dec":
                            if line_commands[3] != "=":
                                self.send_error("Syntax Error")
                                break
                            self.variable_stack.append(Variable(line_commands[1],line_commands[2], len(self.value_stack),self.next_var_id))
                            self.var_to_id[line_commands[2]] = self.next_var_id
                            self.next_var_id += 1
                            var_lst = line_commands[4:]
                            var = self.solve_expression(var_lst)
                            if var is None:
                                self.send_error("Syntax Error")
                                print("None Found")
                            else:
                                self.value_stack.append(int(var))
                                self.value_type_stack.append(line_commands[1])
                            break
                        elif line_command.startswith("print("):
                            print("a")
                            print_list = line_command.split("(")
                            str_for_print = print_list[1].replace(")","")
                            if str_for_print.startswith('"') and str_for_print.endswith('"'):
                                str_for_print = str_for_print[1:-1]
                                print(str_for_print)
                            else:
                                print("b")
                                str_for_print = self.get_var(str_for_print)
                                if str_for_print is None:
                                    self.send_error("syntax error")
                                print(self.get_var(str_for_print))
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
            var = self.value_stack[self.variable_stack[self.var_to_id[variable_name]].valeu_stack_index]
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
            if self.value_type_stack[self.var_to_id[value]] != expected_type:
                use_value = None
        else:
            use_value = value
            if self.get_type(use_value) != expected_type:
                use_value = None
        return use_value
    
    def get_type(self, value_type):
        value_type_check = value_type
        return value_type_check
    
interpreter_run = interpreter()
interpreter_run.interpret_code()