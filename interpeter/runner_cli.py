from enum import StrEnum
from sys import flags

from tokenizer import Tokenizer
import os
from run_interpeter import Interpreter
import subprocess
import sys

class InterpeterActions(StrEnum):
    Run = "run"
    Parse = "parse"
    Done = "done"

class Runner:
    def __init__(self):
        self.language_is_running = True

    @staticmethod
    def run_program_in_terminal(file_use, close_terminal_when_done=True):
        if not os.path.exists(f"{file_use}.code"):
            print("file not found")
            return

        interpreter_script = os.path.abspath(__file__)
        cmd = [sys.executable, interpreter_script, "run_file", file_use]
        cmd_str = " ".join(f'"{c}"' for c in cmd)  # quote paths with spaces

        if os.name == "nt":  # Windows
            if close_terminal_when_done:
                # /c closes the terminal after execution
                subprocess.Popen(f'start cmd /c {cmd_str}', shell=True)
            else:
                # /k keeps the terminal open
                subprocess.Popen(f'start cmd /k {cmd_str}', shell=True)

        elif sys.platform == "darwin":  # macOS
            if close_terminal_when_done:
                subprocess.Popen([
                    "osascript", "-e",
                    f'tell application "Terminal" to do script "{cmd_str}; exit"'
                ])
            else:
                subprocess.Popen([
                    "osascript", "-e",
                    f'tell application "Terminal" to do script "{cmd_str}"'
                ])

        else:  # Linux
            if close_terminal_when_done:
                subprocess.Popen(["xterm", "-e", f"{cmd_str}; exit"])
            else:
                subprocess.Popen(["xterm", "-e", cmd_str])

    def run(self):
        while self.language_is_running:
            command = input("What file to run: ").strip()
            if not command:
                continue

            command_lst = command.split()
            action = command_lst[0]

            if action == InterpeterActions.Done.value:
                self.language_is_running = False
                return

            file_use = command_lst[1]
            
            flags = command_lst[2:]
            
            for flag in flags:
                if not flag.startswith("-"):
                    print("flag is not a flag")
                if flag == "-force_close=False":
                    pass
                elif flag == "-local":
                    pass
                else:
                    print("flag does not exist")
                    return

            if action == InterpeterActions.Run.value:
                self.run_program_in_terminal(file_use)
            else:
                print("unknown command")
                


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "run_file":
        file_use = sys.argv[2]
        with open(f"{file_use}.code", "r") as f:
            content = f.read()
        tokenizer = Tokenizer(content)
        tokens = tokenizer.tokenize()
        interpreter = Interpreter()
        interpreter.interpret_code(tokens)
    else:
        runner = Runner()
        runner.run()
