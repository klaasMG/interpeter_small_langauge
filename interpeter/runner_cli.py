from enum import StrEnum
from tokenizer import Tokenizer
import os
from run_interpeter import Interpreter

class InterpeterActions(StrEnum):
    Run = "run"
    Parse = "parse"
    Done = "done"
    Set = "set"

class InterpeterFlagsGlobal:
    def __init__(self):
        self.global_set_local = True
        self.global_set_force_close = False
        
    def set_global(self, flag, state:bool):
        if flag == "-local":
            self.Local = state
        elif flag == "-force_close":
            self.ForceClose = state
        else:
            print("flag not found:", flag)

global_flags = InterpeterFlagsGlobal()
class InterpeterFlags:
    def __init__(self, interpeter_flag_global):
        self.interpeter_flag_global = interpeter_flag_global
        self.Local: bool = self.interpeter_flag_global.global_set_local
        self.ForceClose: bool = self.interpeter_flag_global.global_set_force_close  # default: close terminal when done

    def set_flag(self, flag, state: bool):
        if flag == "-local":
            self.Local = state
        elif flag == "-force_close":
            self.ForceClose = state
        else:
            print("flag not found:", flag)

    def get_flag(self, flag) -> bool:
        if flag == "-local":
            return self.Local
        elif flag == "-force_close":
            return self.ForceClose
        else:
            print("flag not found:", flag)
            return False
    
    def set_global(self, flag, state:bool):
        self.interpeter_flag_global.set_global(flag,state)

class Runner:
    def __init__(self):
        self.language_is_running = True
        self.standard_flags = InterpeterFlags(global_flags)

    # ---------------------------------------------------------
    # RUN IN SAME TERMINAL
    # ---------------------------------------------------------
    def run_program_in_current(self, file_use):
        # allow user to pass either "foo" or "foo.code"
        if not file_use.endswith(".code"):
            file_use = f"{file_use}.code"
        file_path = os.path.abspath(file_use)

        if not os.path.exists(file_path):
            print("file not found:", file_path)
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tokenizer = Tokenizer(content)
        tokens = tokenizer.tokenize()
        interpreter = Interpreter()
        interpreter.interpret_code(tokens)

    # ---------------------------------------------------------
    # RUN IN NEW TERMINAL WINDOW (cross-platform)
    # ---------------------------------------------------------
    @staticmethod
    def run_program_in_terminal(file_use, close_terminal_when_done=True):
        raise RuntimeError("not yet implemented")

    # ---------------------------------------------------------
    # MAIN CLI LOOP
    # ---------------------------------------------------------
    def run(self):
        while self.language_is_running:
            try:
                command = input("What file to run: ").strip()
            except EOFError:
                return
            if not command:
                continue

            parts = command.split()
            action = parts[0]

            if action == InterpeterActions.Done.value:
                self.language_is_running = False
                print("closing")
                return
            
            if action == InterpeterActions.Run.value:
                file_use = parts[1]
                flags = parts[2:]
                
                # reset flags every command
                self.standard_flags = InterpeterFlags(global_flags)
                
                # process flags
                for flag in flags:
                    if not flag.startswith("-"):
                        print("flag is not a flag:" , flag)
                        break
                    # handle supported flags
                    if flag == "-local":
                        self.standard_flags.set_flag("-local" , True)
                    elif flag == "-force_close":
                        self.standard_flags.set_flag("-force_close" , True)
                    else:
                        print("flag does not exist:" , flag)
                        break
                
                run_local = self.standard_flags.get_flag("-local")
                force_close = self.standard_flags.get_flag("-force_close")
                if run_local:
                    self.run_program_in_current(file_use)
                else:
                    self.run_program_in_terminal(file_use, close_terminal_when_done=force_close)
            elif action == InterpeterActions.Set:
                flags_to_set = parts[1:]
                for flag in flags_to_set:
                    flag_and_bool:list[str] = flag.split("=")
                    self.standard_flags.set_global(flag_and_bool[0],bool(flag_and_bool[1]))
            else:
                print("unknown command")


# ---------------------------------------------------------
# CHILD MODE: when started in a new terminal with "run_file"
# ---------------------------------------------------------
if __name__ == "__main__":
    # Normal interactive mode
    runner = Runner()
    runner.run()