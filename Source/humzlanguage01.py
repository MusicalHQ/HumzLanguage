#humzlanguage1.0
import sys
import BFPlus as BF

temp_variables = ["_copy_swap","_math_1","_math_2","_math_3"]

possible_commands = {}
possible_commands["asg"] = ["asg",3]
possible_commands["list"] = ["list",2]
possible_commands["jmp"] = ["jmp",2]
possible_commands["inc"] = ["inc",4]
possible_commands["set"] = ["set",4]
possible_commands["unt"] = ["unt",2]
possible_commands["end_unt"] = ["end_unt",0]
possible_commands["out"] = ["out",3]
possible_commands["cpy"] = ["cpy",4]
possible_commands["bf"] = ["bf",0]
possible_commands["inp"] = ["inp",2]
possible_commands["add"] = ["add",6]
possible_commands["sub"] = ["sub",6]
possible_commands["mul"] = ["mul",6]
possible_commands["div"] = ["div",6]
possible_commands["if_not_zero"] = ["if_not_zero",2]
possible_commands["if_zero"] = ["if_zero",2]
possible_commands["end_if"] = ["end_if",0]



editor = False

class func: #name,args,func
    def __init__(self,name,args,func):
        self.args,self.func,self.name = args,func,name

class com: #function,arguments
    def __init__(self,function,arguments):
        self.function,self.arguments = function,arguments

def replace(list_to_replace,value,replacement):
    output = []
    for i in list_to_replace:
        if i == value:
            if type(replacement).__name__ == "list":
                output = output + replacement
            else:
                output.append(replacement)
        else:
            output.append(i)
    return output

def replace_bulk(list_to_replace,values,replacements):
    output = list_to_replace[:]
    for idx,value in enumerate(values):
        output = replace(output,value,replacements[idx])
    return output

class parser: #Parses Humzlanguage to a format readable by compiler
    def __init__(self,possible_commands,recursion_limit = 1000,import_limit = 100):
        global editor
        self.possible_commands,self.recursion_limit,self.import_limit = possible_commands,recursion_limit,import_limit

    def get_parsed(self,input,is_file=True):
        self.raw = self.read(input,is_file)
        self.raw = self.check_assigns(self.raw)
        self.raw = self.check_quotes(self.raw)
        self.raw,self.functions = self.get_functions(self.raw)
        self.fix_functions()
        self.raw = self.expand_functions(self.raw)
        self.raw,self.variables,self.lists = self.get_variables(self.raw)
        self.parsed = self.parse(self.raw)
        return self.parsed,self.variables,self.lists

    def read(self,input,is_file):
        output = []
        if is_file:
            with open(input,'r') as f:
                for line in f:
                    temp = []
                    for word in line.split():
                        temp.append(word)
                    if not temp == []:
                        output.append(temp)
        else:
            for line in input:
                temp = []
                for word in line.split():
                    temp.append(word)
                if not temp == []:
                    output.append(temp)
        return output

    def check_assigns(self,raw):
        output = []
        for command in raw:
            temp = []
            if len(command) > 1:
                if command[1] == "=":
                    temp = ["asg"] + command
                else:
                    temp = command
            else:
                temp = command
            output.append(temp)
        return output

    def check_quotes(self,raw):
        output = []
        has_quote = False
        combined = ""
        for function in raw:
            temp = []
            for word in function:
                if word[0] == '"':
                    combined = word
                    if not word[-1] == '"':
                        has_quote = True
                    else:
                        temp.append(combined)
                elif word[-1] == '"':
                    has_quote = False
                    combined = combined + " " + word
                    temp.append(combined)
                elif has_quote:
                    combined = combined + " " + word
                elif not has_quote:
                    temp.append(word)
            output.append(temp)
        return output

    def get_functions(self,raw):
        output = []
        functions = {}
        idx = 0
        while idx < len(raw):
            command = raw[idx]
            if command[0] == "fnc":
                name = command[1]
                arguments = command[2:-1]
                idx += 1
                function = []
                while not "}" in raw[idx]:
                    function.append(raw[idx])
                    idx += 1
                functions[name] = func(name,arguments,function)
            else:
                output.append(command)
            idx += 1
        return output,functions

    def fix_functions(self):
        while self.has_functions(self.functions):
            for name in self.functions:
                self.functions[name].func = self.expand_functions(self.functions[name].func)

    def has_functions(self,functions):
        has_functions = False
        for name in functions:
            for command in functions[name].func:
                if command[0] in functions:
                    has_functions = True
        return has_functions

    def expand_functions(self,raw):
        output = []
        for command in raw:
            if command[0] in self.functions:
                new_args = command[1:]
                _func = self.functions[command[0]]
                _commands = _func.func
                _args = _func.args
                new_commands = []
                for line in _commands:
                    new_commands.append(replace_bulk(line,_args,new_args))
                output = output + new_commands
            else:
                output.append(command)
        return output

    def get_variables(self,raw):
        output = []
        variables = []
        lists = {}
        for command in raw:
            if command[0] == "var":
                variables.append(command[1])
            elif command[0] == "list":
                lists[command[1]] = command[2]
                output.append(command)
            else:
                output.append(command)
        return output,variables,lists

    def parse(self,raw):
        parsed = []
        for command in raw:
            temp = self.possible_commands[command[0]]
            temp_command = com(temp[0],command[1:])
            parsed.append(temp_command)
        return parsed

class compiler:
    def __init__(self,parser,file):
        global temp_variables
        self.parsed,self.variables,self.lists = parser.get_parsed(file)
        self.variables = self.variables + temp_variables
        self.addresses = self.get_memory_locations()
        self.bf_out = ""
        self.unts = []
        print(self.addresses)
        self.compile()
        print(self.bf_out)
        BF.run(BF.optimize_brain(self.bf_out),True)

    def compile(self):
        for command in self.parsed:
            func_ = getattr(self,command.function)
            func_(command.arguments)

    def get_type_and_value(self,value):
        out_type = None
        if value in self.variables:
            out_type = "var"
        elif value in [row[0] for row in self.lists]:
            out_type = "list"
        elif type(value).__name__ == "int":
            out_type = "int"
        elif type(value).__name__ == "str":
            out_type = "str"
        return out_type,value

    def get_memory_locations(self):
        memory = [0]
        for variable in self.variables:
            memory.append(variable)
        for list_ in self.lists:
            memory.append(list_)
        for list_ in self.lists:
            memory.append(str(list_ + "_len"))
            for i in range(int(self.lists[list_])):
                memory.append(str(list_ + str(i)))
        return memory

    def get_var_address(self,variable):
        return self.addresses.index(variable)

    def fix_args_basic(self,args):
        out = []
        for g in args:
            if g in self.variables or g in self.lists:
                out.append(self.get_var_address(g))
            else:
                out.append(g)
        return out

    def add_bf(self,bf):
        self.bf_out = self.bf_out + bf

    def get_value(self,type_,value_):
        if type_ == "int":
            value = int(value_)
        elif type_ == "str":
            if len(value_) == 3:
                value = value_[1:-1]
            value = ord(value)
        character = ["+","-"][value < 0]
        return value,character

    ### HUMZLANGUAGE COMMANDS

    def jmp (self,args):
        args = self.fix_args_basic(args)
        address_type,location = args[0],int(args[1])
        self.add_bf("rc" + "+"*location + "p")
        if address_type == "!dir":
            self.add_bf("p")

    def inc (self,args):
        address_type,location,type_,value = args[0],args[1],args[2],args[3]
        self.jmp([address_type,location])
        value,character = self.get_value(type_,value)
        self.add_bf(character * abs(value))

    def set (self,args):
        address_type,location,type_,value = args[0],args[1],args[2],args[3]
        self.jmp([address_type,location])
        self.add_bf("c")
        value = self.get_value(type_,value)[0]
        self.add_bf("+" * value)

    def unt (self,args):
        self.jmp(args)
        self.unts.append(args)
        self.add_bf("[")

    def end_unt (self,args):
        args = self.unts.pop(-1)
        self.jmp(args)
        self.add_bf("]")

    def out (self,args):
        self.jmp(args[:-1])
        if args[2] == "int":
            self.add_bf("o")
        elif args[2] == "str":
            self.add_bf(".")

    def cpy (self,args):
        copying_from = args[:2]
        print(copying_from)
        copying_to = args[2:]
        swap = ["dir","_copy_swap"]
        self.set(swap + ["int",0])
        self.set(copying_to + ["int",0])
        self.unt(copying_from)
        self.inc(copying_from + ["int",-1])
        self.inc(copying_to + ["int",1])
        self.inc(swap + ["int",1])
        self.end_unt([])
        self.unt(swap)
        self.inc(copying_from + ["int",1])
        self.inc(swap + ["int",-1])
        self.end_unt([])

    def list(self,args):
        self.set(["dir",args[0],"int",self.addresses.index(str(args[0] + "_len"))])
        self.set(["!dir",args[0],"int",args[1]])

    def bf (self,args):
        self.add_bf(args[0])

    def inp (self,args):
        self.jmp(args)
        self.add_bf(",")

    def add (self,args):
        first = args[:2]
        second = args[2:4]
        output = args[4:]
        swap = ["dir","_math_1"]
        self.cpy(first + swap)
        self.cpy(second + output)
        self.unt(swap)
        self.inc(swap + ["int",-1])
        self.inc(output + ["int",1])
        self.end_unt([])

    def sub (self,args):
        first = args[:2]
        second = args[2:4]
        output = args[4:]
        swap = ["dir","_math_1"]
        self.cpy(first + output)
        self.cpy(second + swap)
        self.unt(swap)
        self.inc(swap + ["int",-1])
        self.inc(output + ["int",-1])
        self.end_unt([])

    def mul (self,args):
        first = args[:2]
        second = args[2:4]
        output = args[4:]
        temp = ["dir","_math_2"]
        temp_2 = ["dir","_math_3"]
        self.set(output + ["int",0])
        self.set(temp_2 + ["int",0])
        self.cpy(second + temp)
        self.unt(temp)
        self.add(first + temp_2 + output)
        self.cpy(output + temp_2)
        self.inc(temp + ["int",-1])
        self.end_unt([])

    def if_not_zero(self,args):
        temp = ["dir","_math_1"]
        self.cpy(args + temp)
        self.unt(temp)
        self.set(temp + ["int",0])

    def end_if(self,args):
        self.end_unt([])

    def if_zero(self,args):
        temp = ["dir","_math_2"]
        self.set(temp + ["int",1])
        self.if_not_zero(args)
        self.set(temp + ["int",0])
        self.end_if([])
        self.if_not_zero(temp)
        self.set(temp + ["int",0])

parser = parser(possible_commands)
compiler = compiler(parser,'test.hl')
