#humzlanguage1.0
import sys
import BFPlus as BF
import math_parser2 as math_parse
from optimized_compiler import *

temp_variables = ["_copy_swap","_math_1","_math_2","_math_3","_math_4","_math_5","_math_6","_math_7","_asg_temp_1","_math_parse_1","_math_parse_2","_print_temp_1","_print_temp_2","_print_temp_3","_clear_list","_,","_b","_[","_]","_if_1","_if_2","_if_big","_if_small","_if_equal","_new_line","_return","_read_temp","_read_acc","_read_count","_s","_read_until"]

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
possible_commands["print"] = ["print_",1]
possible_commands["if"] = ["if_special",2]
possible_commands["while"] = ["while_special",0]
possible_commands["end_while"] = ["end_while",2]
possible_commands["new_line"] = ["new_line",2]
possible_commands["return"] = ["return_",2]
possible_commands["#"] = ["nothing",1]
possible_commands["read"] = ["read_special",1]

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
        self.raw,functions = self.check_imports(self.raw)
        self.raw = self.check_quotes(self.raw)
        self.raw,self.functions = self.get_functions(self.raw)
        self.functions.update(functions)
        #self.functions = self.functions + functions
        self.fix_functions()
        self.raw = self.expand_functions(self.raw)
        self.raw,self.variables,self.lists = self.get_variables(self.raw)
        self.parsed = self.parse(self.raw)
        return self.parsed,self.variables,self.lists,self.raw,self.functions

    def check_imports(self,raw):
        output = []
        parsed = []
        var = []
        lists = []
        raw_ = []
        functions = {}
        for line in raw:
            if line[0] == "import":
                parsed,var,lists,raw_,new_functions = self.get_parsed(line[1])
                functions.update(new_functions)
            else:
                output.append(line)
        output = raw_ + output
        return output,functions

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
            if len(command) > 2:
                if command[1] == "=":
                    temp = ["asg"] + command
                elif command[2] == "=" and command[0] == "var":
                    output.append(["var",command[1]])
                    temp = ["asg"] + command[1:]
                elif command[0] == "list" and command[2] == "=":
                    if command[3][0] == '"':
                        length = len(command[3])-2
                    elif command[3][0] == "[":
                        length = len(command[3][1:-1].split(","))
                    output.append(["list",command[1],str(length)])
                    temp = ["asg"] + command[1:]
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

    def expand_functions(self,raw,return_number=0):
        output = []
        for command in raw:
            if command[0] in self.functions:
                new_args = command[1:]
                _func = self.functions[command[0]]
                _commands = _func.func
                _args = _func.args
                new_commands = []
                for line in _commands:
                    for word in line:
                        if "[" in word:
                            list_name = word.split('[')[0]
                            list_index = word.split('[')[1][:-1]
                            if list_name in _args:
                                list_name = new_args[_args.index(list_name)]
                            if list_index in _args:
                                list_index = new_args[_args.index(list_index)]
                            new_word = list_name + '[' + list_index + ']'
                            _args.append(word)
                            new_args.append(new_word)
                for line in _commands:
                    new_commands.append(replace_bulk(line,_args,new_args))
                output.append(["var","_return" + str(return_number)])
                return_number += 1
                            #if word.split
                output = output + new_commands
            elif command[0] == "asg" or command[0] == "print" or command[0] == "if" or command[0] == "while":
                x = 0
                has_func = False
                while x < len(command):
                    if command[x] in self.functions:
                        has_func = True
                        _func = self.functions[command[x]]
                        _commands = _func.func
                        _args = _func.args
                        new_args = command[x+1:x+len(_args)+1]
                        new_commands = []
                        for line in _commands:
                            for word in line:
                                if "[" in word:
                                    list_name = word.split('[')[0]
                                    list_index = word.split('[')[1][:-1]
                                    if list_name in _args:
                                        list_name = new_args[_args.index(list_name)]
                                    if list_index in _args:
                                        list_index = new_args[_args.index(list_index)]
                                    new_word = list_name + '[' + list_index + ']'

                                    if not word in _args:
                                        _args.append(word)
                                    if not new_word in new_args:
                                        new_args.append(new_word)

                        for line in _commands:
                            if not len(_args) == 0:
                                new_commands.append(replace_bulk(line,_args,new_args))
                        output = output + new_commands
                        add = 1
                        if command[0] == "if" or command[0] == "while":
                            add = 0
                        command[x:x+len(_args)+add] = ["_return" + str(return_number)]
                        output.append(["var","_return" + str(return_number)])
                        return_number += 1
                        output.append(command)
                        output = self.expand_functions(output,return_number)
                    x += 1
                if not has_func:
                    output.append(command)
            else:
                output.append(command)
        return output

    def get_variables(self,raw):
        output = []
        variables = []
        lists = {}
        x = 0
        for command in raw:
            if command[0] == "var":
                variables.append(command[1])
            elif command[0] == "while":
                variables.append("while" + str(x))
                x += 1
                output.append(command)
            elif command[0] == "list":
                lists[command[1]] = command[2]
                output.append(command)
            else:
                output.append(command)
        return output,variables,lists

    def parse(self,raw):
        parsed = []
        for command in raw:
            try:
                temp = self.possible_commands[command[0]]
                temp_command = com(temp[0],command[1:])
                parsed.append(temp_command)
            except:
                throw("function " + command[0] + " doesn't exist")
        return parsed

class compiler:
    def __init__(self,parser,file,is_file=True):
        global temp_variables
        self.parsed,self.variables,self.lists,self.raw,self.functions = parser.get_parsed(file,is_file)
        self.variables = self.variables + temp_variables
        self.strings = []
        self.addresses = self.get_memory_locations()
        self.current_while = 0
        self.bf_out = ""
        self.unts = []
        self.whiles = []
        self.return_count = 0
        self.set_constants()
        self.compile()

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
            for i in range(int(self.lists[list_])+1):
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
            try:
                value = int(value_)
            except:
                throw(value_ + " is not an integer")
        elif type_ == "str":
            if len(value_) == 3:
                value = value_[1:-1]
            try:
                value = ord(value)
            except:
                if len(value_) > 3:
                    throw("cannot assign " + value_ + " to variable (must be string)")
                else:
                    throw(value_ + " is not str")
        else:
            throw("type " + type_ + " doesn't exist")
        character = ["+","-"][value < 0]
        return value,character

    def get_address(self,value):
        asg_temp = ["dir","_asg_temp_1"]
        if value in self.variables:
            return ["dir",value],"var"
        elif value in self.lists:
            return ["dir",value],"list"
        elif "[" in value:
            if value.split('[')[0] in self.lists:
                value,index = value.split('[')
                index = index[:-1]
                if value in self.lists:
                    if index in self.variables:
                        self.add(["dir",value,"dir",index] + asg_temp)
                        self.inc(asg_temp + ["int",1])
                    else:
                        self.cpy(["dir",value] + asg_temp)
                        try:
                            self.inc(asg_temp + ["int",int(index)+1])
                        except:
                            throw("variable " + index + " doesn't exist")
                return ["!dir","_asg_temp_1"],"var"
            else:
                throw("list " + value.split('[')[0] + " doesn't exist")
        else:
            throw("variable " + value + " doesn't exist")

    def get_value_complex(self,value):
        temp = ""
        for i in value:
            temp = temp + " " + i
        value = temp[1:]
        try:
            value = int(value)
            self.set(['dir','_math_parse_1','int',value])
            return ['dir','_math_parse_1']
        except:
            pass
        if value in self.variables:
            self.cpy(self.get_address(value)[0] + ['dir','_math_parse_1'])
            return ['dir','_math_parse_1']
        if not len(value.split('[')) == 1:
            if value.split('[')[0] in self.lists and len(value.split('[')[1].split(' ')) == 1:
                return self.get_address(value)[0]
        value = math_parse.get_rpn(value)
        return self.parse_rpn(value,len(self.addresses))

    def parse_rpn(self,rp,mem_start):
        try:
            stack = []
            current_mem = mem_start
            for val in rp.split(' '):
                if val in ['-','+','*','/','^','%']:
                    op1 = stack.pop()
                    if op1.isdigit():
                        self.set(['dir','_math_parse_1','int',op1])
                        op1 = ['dir','_math_parse_1']
                    elif op1 in self.variables:
                        op1 = ['dir',op1]
                    elif op1.split('[')[0] in self.lists:
                        op1 = self.get_address(op1)[0]
                    elif op1[:2] == "_p":
                        op1 = ['dir',op1[2:]]

                    op2 = stack.pop()
                    if op2.isdigit():
                        self.set(['dir','_math_parse_2','int',op2])
                        op2 = ['dir','_math_parse_2']
                    elif op2 in self.variables:
                        op2 = ['dir',op2]
                    elif op2.split('[')[0] in self.lists:
                        op2 = self.get_address(op2)[0]
                    elif op2[:2] == "_p":
                        op2 = ['dir',op2[2:]]

                    out = ['dir',current_mem]
                    result = str("_p" + str(current_mem))
                    current_mem += 1

                    if val == "+":
                        self.add(op1 + op2 + out)
                    if val == "-":
                        self.sub(op2 + op1 + out)
                    if val == "*":
                        self.mul(op1 + op2 + out)
                    if val == "/":
                        self.div(op2 + op1 + out)
                    #if val == "^":
                        #self.pwr(op1 + op2 + out)

                    stack.append(result)

                else:
                    stack.append(val)
        except:
            throw("math parsing error")
        return ['dir',stack.pop()[2:]]


    def set_constants(self):
        self.set(['dir','_new_line','int','10'])
        self.set(['dir','_,','str','","'])
        self.set(['dir','_b','int','8'])
        self.set(['dir','_[','str','"["'])
        self.set(['dir','_]','str','"]"'])
        self.set(['dir','_s','int','32'])


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

    def div (self,args):
        first = args[:2]
        second = args[2:4]
        output = args[4:]
        temp = ["dir","_math_4"]
        temp_1 = ["dir","_math_5"]
        temp_2 = ["dir","_math_6"]
        temp_3 = ["dir","_math_7"]
        self.set(output + ["int",0])
        self.set(temp_1 + ["int",0])
        self.cpy(first + temp)
        self.unt(temp)
        self.sub(temp + second + temp_2)
        self.cpy(temp_2 + temp)
        self.add(second + temp_1 + temp_3)
        self.cpy(temp_3 + temp_1)
        self.inc(output + ["int",1])
        self.end_unt([])
        self.sub(temp_1 + first + temp)
        self.if_not_zero(temp)
        self.inc(output + ["int",-1])
        self.end_if([])

    def asg (self,args):
        output,type = self.get_address(args[0])
        if type == "var":
            if args[2][0] == '"':
                self.set(output + ['str',args[2]])
            else:
                try:
                    input = self.get_value_complex(args[2:])
                    #self.out(input + ['int'])
                    self.cpy(input + output)
                except:
                    string_ = ""
                    for i in args[2:]:
                        string_ = string_ + " " + i
                    string_ = string_[1:]
                    throw("expression " + string_ + " not valid")
        if type == "list":
            self.clear_list([args[0]])
            input = "".join(args[2:])
            if input in self.lists:
                self.cpy(['dir',input] + output)
            elif input[0] == '"':
                self.strings.append(args[0])
                for idx,val in enumerate(input[1:-1]):
                    self.asg([str(args[0] + "[" + str(idx) + "]"),'=','"' + val + '"'])
            elif input[0] == '[':
                if args[0] in self.strings:
                    self.strings.remove(args[0])
                for idx,val in enumerate(input[1:-1].split(",")):
                    self.asg([str(args[0] + "[" + str(idx) + "]"),'=',val])

    def clear_list (self,args):
        value = args[0]
        self.asg(['_clear_list','=',str(value + '[-1]')])
        self.inc(['dir','_clear_list','int','-1'])
        self.unt(['dir','_clear_list'])
        self.asg([str(value + '[' + '_clear_list' + ']'),'=','0'])
        self.inc(['dir','_clear_list','int','-1'])
        self.end_unt([])

    def print_ (self,args):
        value = ""
        for i in args:
            value = value + " " + i
        value = value[1:]
        if value in self.strings:
            self.set(['dir','_print_temp_1','int','0'])
            self.asg(['_print_temp_2','=',str(value + '[' + '_print_temp_1' + ']')])
            self.unt(['dir','_print_temp_2'])
            self.out(['dir','_print_temp_2','str'])
            self.inc(['dir','_print_temp_1','int','1'])
            self.asg(['_print_temp_2','=',str(value + '[' + '_print_temp_1' + ']')])
            self.end_unt([])
        elif value in self.lists:
            self.out(['dir','_[','str'])
            self.asg(['_print_temp_3','=',str(value + '[-1]')])
            self.set(['dir','_print_temp_1','int','0'])
            self.unt(['dir','_print_temp_3'])
            self.asg(['_print_temp_2','=',str(value + '[' + '_print_temp_1' + ']')])
            self.out(['dir','_print_temp_2','int'])
            self.out(['dir','_,','str'])
            self.inc(['dir','_print_temp_3','int','-1'])
            self.inc(['dir','_print_temp_1','int','1'])
            self.end_unt([])
            self.out(['dir','_b','str'])
            self.out(['dir','_]','str'])
        elif value[0] == '"':
            for i in value[1:-1]:
                self.set(['dir','_print_temp_3','str','"' + i + '"'])
                self.out(['dir','_print_temp_3','str'])
        elif value[0] == "[":
            for i in value:
                self.set(['dir','_print_temp_3','str','"' + i + '"'])
                self.out(['dir','_print_temp_3','str'])
        else:
            self.asg(['_print_temp_3','=',value])
            self.out(['dir','_print_temp_3','int'])

    def if_special (self,args):
        x = 0
        operators = "!=><"
        while not args[x][0] in operators:
            x += 1
        first = args[:x]
        second = args[x+1:]
        op1 = ""
        op2 = ""
        for i in first:
            op1 = op1 + " " + i
        op1 = op1[1:]
        for i in second:
            op2 = op2 + " " + i
        op2 = op2[1:]
        self.asg(['_if_1','=',op1])
        self.asg(['_if_2','=',op2])
        self.sub(['dir','_if_1','dir','_if_2','dir','_if_big'])
        self.sub(['dir','_if_2','dir','_if_1','dir','_if_small'])
        self.add(['dir','_if_big','dir','_if_small','dir','_if_equal'])
        if args[x] == "==":
            self.if_zero(['dir','_if_equal'])
        elif args[x] == "!=":
            self.if_not_zero(['dir','_if_equal'])
        elif args[x] == ">":
            self.if_not_zero(['dir','_if_big'])
        elif args[x] == "<":
            self.if_not_zero(['dir','_if_small'])
        elif args[x] == ">=":
            self.if_zero(['dir','_if_small'])
        elif args[x] == "<=":
            self.if_zero(['dir','_if_big'])

    def while_special (self,args):
        while_var = ['dir','while' + str(self.current_while)]
        self.whiles.append([args,while_var])
        self.current_while += 1
        self.set(while_var + ['int','1'])
        self.unt(while_var)
        self.set(while_var + ['int','0'])

    def end_while(self,args):
        stuff = self.whiles.pop(-1)
        self.if_special(stuff[0])
        self.set(stuff[1] + ['int','1'])
        self.end_if([])
        self.end_unt([])

    def new_line(self,args):
        self.out(['dir','_new_line','str'])

    def return_(self,args):
        value = ""
        for i in args:
            value = value + " " + i
        value = value[1:]
        self.asg(['_return' + str(self.return_count),'=',value])
        self.return_count += 1

    def nothing(self,args):
        pass

    def read_special(self,args):
        acc = ['dir','_read_acc']
        temp = ['dir','_read_temp']
        count = ['dir','_read_count']
        until = ['dir','_read_until']
        self.set(acc + ['int','0'])
        output,type = self.get_address(args[0])
        if type == "var":
            self.set(count + ['int','1'])
            self.unt(count)
            self.inp(temp)
            self.if_special(['_read_temp','!=','13'])
            self.if_special(['_read_temp','!=','8'])
            self.asg(['_read_acc','=','_read_acc','*','10','+','_read_temp','-','48'])
            self.out(temp + ['str'])
            self.end_if([])
            self.end_if([])
            self.cpy(temp + count)
            self.if_special(['_read_temp','==','8'])
            self.asg(['_read_acc','=','_read_acc','/','10'])
            self.out(['dir','_b','str'])
            self.out(['dir','_s','str'])
            self.out(['dir','_b','str'])
            self.end_if([])
            self.if_special(['_read_temp','==','13'])
            self.set(count + ['int','0'])
            self.end_if([])
            self.end_unt([])
            self.cpy(acc + output)

        if type == "list":
            self.strings.append(args[0])
            self.set(count + ['int','0'])
            self.asg(["_read_until","=",args[0] + "[-1]"])
            self.unt(until)
            self.inp(temp)
            self.if_special(['_read_temp','!=','13'])
            self.if_special(['_read_temp','!=','8'])
            self.asg([args[0] + "[_read_count]","=","_read_temp"])
            self.out(temp + ['str'])
            self.inc(until + ['int','-1'])
            self.inc(count + ['int','1'])
            self.end_if([])
            self.end_if([])
            self.if_special(['_read_temp','==','8'])
            self.out(['dir','_b','str'])
            self.out(['dir','_s','str'])
            self.out(['dir','_b','str'])
            self.inc(until + ['int','1'])
            self.inc(count + ['int','-1'])
            self.end_if([])
            self.if_special(['_read_until','>',args[0] + "[-1]"])
            self.asg(["_read_until","=",args[0] + "[-1]"])
            self.end_if([])
            self.end_unt([])



def throw(error):
    print("================")
    print("ERROR")
    print(error)
    print("================")
    sys.exit()

editor = False

if __name__ == "__main__":
    args = sys.argv[:]
    if not len(args) == 1 or editor:
        parser = parser(possible_commands)
        if editor:
            compiler = compiler(parser,'test.hl')
            compiler_bf_exe(compiler.bf_out,"test.exe")
        else:
            #try:
            compiler = compiler(parser,args[-1])
            #except:
                #throw("file " + args[-1] + " doesn't exist")
        memory = False
        if "-show_memory" in args:
            memory = True
        if not "-compile" in args:
            BF.run(BF.optimize_brain(compiler.bf_out),memory)
        else:
            compiler_bf_exe(compiler.bf_out,args[-1].split(".")[0] + ".exe")
    else:
        program = []
        print("====================================================")
        print("HUMZLANGUAGE SHELL")
        print("====================================================")
        print("")
        new_input = []
        whole_program = []
        new_input_raw = ""
        while True:
            new_input_raw = input(">>>")
            if new_input_raw == "":
                while new_input_raw == "":
                    new_input_raw = input(">>>")
            if new_input_raw == "exit":
                break
            new_input.append(new_input_raw)
            if new_input_raw.split()[0] in ["if","if_zero","if_not_zero"]:
                new_input_raw_1 = ""
                while not new_input_raw_1 == "end_if":
                    new_input_raw_1 = input("...")
                    new_input.append(new_input_raw_1)
            if new_input_raw.split()[0] == "while":
                new_input_raw_1 = ""
                while not new_input_raw_1 == "end_while":
                    new_input_raw_1 = input("...")
                    new_input.append(new_input_raw_1)
            if new_input_raw.split()[0] == "unt":
                new_input_raw_1 = ""
                while not new_input_raw_1 == "end_unt":
                    new_input_raw_1 = input("...")
                    new_input.append(new_input_raw_1)
            if new_input_raw.split()[0] == "fnc":
                new_input_raw_1 = ""
                while not new_input_raw_1 == "}":
                    new_input_raw_1 = input("...")
                    new_input.append(new_input_raw_1)
            try:
                old_program = whole_program
                whole_program = whole_program + new_input
                parse = parser(possible_commands)
                compile = compiler(parse,whole_program,is_file=False)
                BF.run(BF.optimize_brain(compile.bf_out),False)
                to_remove = []
                has_print = False
                for command in whole_program:
                    if len(command.split()) > 1:
                        if command.split()[0] == "print" or command.split()[0] == "out":
                            to_remove.append(command)
                            has_print = True
                for command in to_remove:
                    whole_program.remove(command)
                if has_print:
                    print("")
            except:
                print("ERROR")
                whole_program = old_program
            new_input = []
