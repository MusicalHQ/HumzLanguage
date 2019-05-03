#mid_level_language to BFExtended


import BFPlus as BF
import copy
import sys
from optimized_compiler import *

possible_commands = [['list',2],['asg',3],['if',3],['if_true',5],['if_zero',2],['end_if',0],['if_not_zero',2],['mul',6],['sub',6],['add',6],['bf',1],['list_write_basic',2],['jmp',2],['out',3],['set',4],['unt',2],['inc',4],['end_unt',0],['cpy',4],['mve',4],['fwd',0],['bck',0],['plu',0],['loo',0],['end_loo',0],['out_now',1],['inp',2],['set_hidden_memory',1],['var',1]]

class parse:
    def __init__(self,file,possible_commands,recursion_limit = 1000,import_limit = 100,is_file = True):
        global editor
        self.recursion_limit = recursion_limit
        self.possible_commands = possible_commands
        self.raw = self.read(file,is_file)
        self.raw = self.combine_quotes(self.raw)
        self.file = file
        self.variables = None
        self.variable_addresses = None
        self.import_limit = import_limit
        self.imported = []
        self.ints = []
        self.lists = []
        counter = 0
        self.hidden_memory = 20
        while self.has_import(self.raw) and counter < self.import_limit:
            counter += 1
            self.raw = self.imports(self.raw)

        self.functions = self.get_functions(self.raw)
        self.raw = self.functions[0]
        self.functions = self.functions[1]
        print("raw",self.raw)
        self.raw = self.assigns(self.raw)
        self.parsed = self.parse(self.raw)
        self.parsed = self.check_writes(self.parsed)

        counter = 0
        while self.has_func(self.parsed) and counter < self.recursion_limit:
            counter += 1
            self.parsed = self.replace_func(self.parsed)
            self.parsed = self.check_writes(self.parsed)

        if self.has_func(self.parsed):
            print("Reached function limit")
            raise ValueError('Reached function in function limit')

        self.parsed = self.set_hidden_memory(self.parsed)
        #for i in self.parsed:
            #print(i)
        self.parsed = self.get_var_address(self.parsed)
        if editor:
            for idx,variable in enumerate(self.variables):
                print(variable + ':',self.variable_addresses[idx])

    def assigns(self,parsed):
        x = 0
        print(parsed)
        while x < len(parsed):
            if parsed[x] == "=":
                parsed.insert(x-1,'asg')
                x += 1
            x += 1
        return parsed

    def combine_quotes(self,parsed):
        x = 0
        y = 0
        string_ = False
        current_string = ""
        while x < len(parsed):
            if parsed[x][0] == '"':
                current_string = parsed[x]
                string_ = True
                y = x
            elif parsed[x][-1] == '"':
                current_string = current_string + " " + parsed[x]
                string_ = False
                while not y == x:
                    parsed.pop(x)
                    x -= 1
                parsed.pop(x)
                parsed.insert(x,current_string)
            elif string_:
                current_string = current_string + " " + parsed[x]
            x += 1
        x = 0
        while x < len(parsed):
            if parsed[x][0] == '"' and parsed[x][-1] == '"':
                parsed[x] = parsed[x]
            x += 1
        return parsed

    def get_var_address(self,parsed):
        variables = []
        variable_addresses = []
        for i in parsed[:]:
            if i[0] == 'var':
                variables.append(i[1])
                parsed.remove(i)
                self.ints.append(i[1])
            if i[0] == 'list':
                variables.append(i[1])
                self.lists.append(i[1])
        for i in variables:
            variable_addresses.append(-self.hidden_memory)
            self.hidden_memory += 1
        #for i in range(len(parsed)):
        #    for e in range(len(parsed[i])):
        #        if parsed[i][e] in variables and not (parsed[i][e-1] == 'int' or parsed[i][e-1] == 'str'):
        #            parsed[i][e] = variable_addresses[variables.index(parsed[i][e])]
        self.variables = variables
        self.variable_addresses = variable_addresses
        return parsed

    def check_writes(self,parsed):
        parsed_temp = []
        for idx,i in enumerate(parsed[:]):
            temp = []
            if i[0] == 'list_write_basic':
                x = 0
                for e in i[2]:
                    temp.append(["list_set",i[1],x,"str",e])
                    x += 1
                parsed_temp.append(temp)
        for temp in parsed_temp:
            for idx,e in enumerate(parsed):
                if e[0] == "list_write_basic":
                    break
            parsed.remove(e)
            for i in temp:
                parsed.insert(idx,i)
        return parsed

    def set_hidden_memory(self,parsed):
        for i in parsed[:]:
            if i[0] == 'set_hidden_memory':
                if int(i[1]) > self.hidden_memory:
                    self.hidden_memory = int(i[1])
                parsed.remove(i)
        return parsed

    def has_func(self,parsed):
        has_func = False
        for i in parsed:
            for e in self.functions:
                if i[0] in e[0]:
                    has_func = True
        return has_func

    def has_import(self,parsed):
        has_import = False
        for i in parsed:
            if i == 'import':
                has_import = True
        return has_import

    def read (self,file,is_file = True):
        raw = []
        if is_file:
            with open(file,'r') as f:
                for line in f:
                    for word in line.split():
                        raw.append(word)
        else:
            for line in file:
                for word in line.split():
                    raw.append(word)
        return raw

    def imports (self,raw_file):
        raw = raw_file
        x = 0
        while x < (len(raw)-1):
            if raw[x] == 'import':
                raw.pop(x)
                file = raw.pop(x)
                if not file in self.imported:
                    new_raw = self.read(file)
                    raw = new_raw + raw
                    self.imported.append(file)
                x -= 1
            x += 1
        return raw


    def get_functions (self,raw_file):
        raw = raw_file
        x = 0
        functions = []
        while x < (len(raw)-1):
            if raw[x] == 'fnc':
                new_func = []
                raw.pop(x)
                no_args = -1
                while not raw[x] == '{':
                    no_args += 1
                    new_func.append(raw.pop(x))
                raw.pop(x)
                while not raw[x] == '}':
                    new_func.append(raw.pop(x))
                raw.remove('}')
                self.possible_commands.append([new_func[0],no_args])
                functions.append(self.parse(new_func))
                x = -1
            x += 1
        return [raw,functions]

    def parse (self,raw_file):
        raw = raw_file
        parsed = []
        while len(raw) > 0:
            parsed_command = []
            command = raw.pop(0)
            parsed_command.append(command)
            for idx,i in enumerate(self.possible_commands):
                args = i[1]
                if i[0] == command:
                    break
            for i in range(args):
                try:
                    parsed_command.append(raw.pop(0))
                except:
                    print("")
                    print("Syntax error:")
                    print("")
                    function_exists = False
                    real_arguments = len(parsed_command)-1
                    req_arguments = 0
                    for func in self.functions:
                        if func[0][0] == command:
                            function_exists = True
                            req_arguments = len(func[0])-1
                            break
                    if not function_exists:
                        for func in possible_commands:
                            if func[0] == command:
                                function_exists = True
                                req_arguments = func[1]
                                break
                    if function_exists:
                        print("Function",command,"takes",req_arguments,"arguments but",real_arguments,"were given:")
                        incorrect_line = ""
                        for cmd in parsed_command:
                            incorrect_line = incorrect_line + cmd + " "
                        print("")
                        print("    " + incorrect_line)
                    else:
                        print("Function",command,"doesn't exist")
                        print("")
                        print("    Maybe an error in command",parsed[-1][0])
                        incorrect_line = ""
                        for cmd in parsed[-1]:
                            incorrect_line = incorrect_line + cmd + " "
                        print("")
                        print("        " + incorrect_line)
                    print("")
                    sys.exit("Compiler Stopped")
            parsed.append(parsed_command)
        return parsed

    def replace_func (self,raw_file):
        raw = copy.deepcopy(raw_file)

        all_functions = []

        i = 0
        while i < (len(raw)):
            command = raw[i]
            is_function = False
            functions = copy.deepcopy(self.functions)
            for e,function in enumerate(functions):
                if command[0] in function[0]:
                    is_function = True
                    break
            if is_function:
                command_sub = command
                command_sub.pop(0)
                function_sub = function[:]
                function_sub = function_sub[0]
                function_sub.pop(0)
                sub = dict(zip(function_sub,command_sub))
                new_function = []
                for e in function:
                    new_function.append(list(map(sub.get, e, e)))
                new_function.pop(0)
                index = i
                raw.pop(index)
                for e in new_function:
                    raw.insert(index,e)
                    index += 1
            i += 1
        return raw



class compiler:
    def __init__(self,possible_commands,parser):
        self.bf_out = ''
        self.untils = []
        self.hidden_memory = parser.hidden_memory
        self.possible_commands = possible_commands
        self.variables,self.variable_addresses = parser.variables,parser.variable_addresses
        self.ints,self.lists = parser.ints,parser.lists

    def replace_func (self,args):
        x = 0
        while x < len(args):
            if args[x] in self.variables:
                if x > 0:
                    if not args[x-1] == "int" and not args[x-1] == "str":
                        args[x] = self.variable_addresses[self.variables.index(args[x])]
                else:
                    args[x] = self.variable_addresses[self.variables.index(args[x])]
            x += 1
        return args

    def bf (self,args):
        args = self.replace_func(args)
        self.bf_out = self.bf_out + args[0]

    def jmp (self,args):
        args = self.replace_func(args)
        try:
            address_type,location = args[0],(int(args[1])+self.hidden_memory)
        except:
            print("")
            print("Compiler Error:")
            print("")
            print("Variable",args[1],"doesn't exist")
            print("")
            sys.exit("Compiler Stopped")
        self.bf_out = self.bf_out + 'rc'
        for i in range(location):
            self.bf_out = self.bf_out + '+'
        self.bf_out = self.bf_out + 'p'
        if address_type == '!dir':
            self.bf_out = self.bf_out + 'p'
            for i in range(self.hidden_memory):
                self.bf_out = self.bf_out + '>'

    def inp (self,args):
        args = self.replace_func(args)
        address_type,location = args[0],args[1]
        self.jmp([address_type,location])
        self.bf_out = self.bf_out + ','

    def set (self,args):
        args = self.replace_func(args)
        address_type,location = args[0],args[1]
        data_type,value = args[2],args[3]
        self.jmp([address_type,location])
        self.bf_out = self.bf_out + 'c'
        if data_type == 'str':
            value = ord(value)
        elif data_type == 'int':
            value = int(value)
        for i in range(value):
            self.bf_out = self.bf_out + '+'

    def out (self,args):
        args = self.replace_func(args)
        address_type,location,data_type = args[0],args[1],args[2]
        self.jmp([address_type,location])
        if data_type == 'int':
            self.bf_out = self.bf_out + 'o'
        elif data_type == 'str':
            self.bf_out = self.bf_out + '.'

    def unt (self,args):
        args = self.replace_func(args)
        self.jmp(args)
        self.untils.append(args)
        self.bf_out = self.bf_out + '['

    def end_unt (self):
        args = self.untils.pop(len(self.untils)-1)
        self.jmp(args)
        self.bf_out = self.bf_out + ']'

    def inc (self,args):
        args = self.replace_func(args)
        address_type,location,data_type,value = args[0],args[1],args[2],args[3]
        self.jmp([address_type,location])
        if data_type == 'str':
            value = ord(value)
        elif data_type == 'int':
            value = int(value)
        char = '-'
        if value > 0:
            char = '+'
        for i in range(abs(value)):
            self.bf_out = self.bf_out + char
        #self.bf_out = self.bf_out + 'a' + str(value) + 'b'

    def cpy (self,args):
        args = self.replace_func(args)
        address_type_1,location_1,address_type_2,location_2 = args[0],args[1],args[2],args[3]
        address_type_3,location_3 = 'dir','-1'
        self.set([address_type_3,location_3,'int',0])
        self.set([address_type_2,location_2,'int',0])
        self.unt([address_type_1,location_1])
        self.inc([address_type_1,location_1,'int',-1])
        self.inc([address_type_2,location_2,'int',1])
        self.inc([address_type_3,location_3,'int',1])
        self.end_unt()
        self.unt([address_type_3,location_3])
        self.inc([address_type_1,location_1,'int',1])
        self.inc([address_type_3,location_3,'int',-1])
        self.end_unt()

    def mve (self,args):
        args = self.replace_func(args)
        address_type_1,location_1,address_type_2,location_2 = args[0],args[1],args[2],args[3]
        address_type_3,location_3 = 'dir','-1'
        self.set([address_type_2,location_2,'int',0])
        self.unt([address_type_1,location_1])
        self.inc([address_type_1,location_1,'int',-1])
        self.inc([address_type_2,location_2,'int',1])
        self.end_unt()

    def fwd (self):
        self.bf_out = self.bf_out + '>'

    def bck (self):
        self.bf_out = self.bf_out + '<'

    def plu (self):
        self.bf_out = self.bf_out + '+'

    def min (self):
        self.bf_out = self.bf_out + '-'

    def loo (self):
        self.bf_out = self.bf_out + '['

    def end_loo (self):
        self.bf_out = self.bf_out + ']'

    def out_now (self,args):
        args = self.replace_func(args)
        data_type = args[0]
        self.bf_out = self.bf_out + '.'
        if data_type == 'int':
            self.bf_out = self.bf_out + 'o'
        elif data_type == 'str':
            self.bf_out = self.bf_out + '.'

    def add (self,args):
        args = self.replace_func(args)
        address_type_1,location_1,address_type_2,location_2 = args[0],args[1],args[2],args[3]
        output_address_type,output_location = args[4],args[5]
        self.cpy([address_type_1,location_1,'dir','-2'])
        self.cpy([address_type_2,location_2,output_address_type,output_location])
        self.unt(['dir','-2'])
        self.inc(['dir','-2','int','-1'])
        self.inc([output_address_type,output_location,'int','1'])
        self.end_unt()

    def sub (self,args):
        args = self.replace_func(args)
        address_type_1,location_1,address_type_2,location_2 = args[0],args[1],args[2],args[3]
        output_address_type,output_location = args[4],args[5]
        self.cpy([address_type_1,location_1,output_address_type,output_location])
        self.cpy([address_type_2,location_2,'dir','-2'])
        self.unt(['dir','-2'])
        self.inc(['dir','-2','int','-1'])
        self.inc([output_address_type,output_location,'int','-1'])
        self.end_unt()

    def mul (self,args):
        args = self.replace_func(args)
        address_type_1,location_1,address_type_2,location_2 = args[0],args[1],args[2],args[3]
        output_address_type,output_location = args[4],args[5]
        self.set([output_address_type,output_location,'int',0])
        self.cpy([address_type_1,location_1,'dir','-2'])
        self.unt(['dir','-2'])
        self.cpy([address_type_2,location_2,'dir','-3'])
        self.unt(['dir','-3'])
        self.inc([output_address_type,output_location,'int','1'])
        self.inc(['dir','-3','int','-1'])
        self.end_unt()
        self.inc(['dir','-2','int','-1'])
        self.end_unt()

    def if_not_zero(self,args):
        args = self.replace_func(args)
        address_type,location = args[0],args[1]
        self.cpy([address_type,location,'dir','-2'])
        self.unt(['dir','-2'])
        self.set(['dir','-2','int','0'])

    def end_if(self):
        self.end_unt()

    def if_zero(self,args):
        args = self.replace_func(args)
        address_type,location = args[0],args[1]
        self.set(['dir','-3','int','1'])
        self.if_not_zero([address_type,location])
        self.set(['dir','-3','int','0'])
        self.end_if()
        self.if_not_zero(['dir','-3'])
        self.set(['dir','-3','int','0'])

    def if_true(self,args):
        args = self.replace_func(args)
        address_type_1,location_1,address_type_2,location_2 = args[0],args[1],args[3],args[4]
        operator = args[2]
        if operator == "==":
            self.sub([address_type_1,location_1,address_type_2,location_2,'dir','-4'])
            self.sub([address_type_2,location_2,address_type_1,location_1,'dir','-5'])
            self.add(['dir','-4','dir','-5','dir','-6'])
            self.if_zero(['dir','-6'])
        elif operator == "!=":
            self.sub([address_type_1,location_1,address_type_2,location_2,'dir','-4'])
            self.sub([address_type_2,location_2,address_type_1,location_1,'dir','-5'])
            self.add(['dir','-4','dir','-5','dir','-6'])
            self.if_not_zero(['dir','-6'])
        elif operator == ">":
            self.sub([address_type_1,location_1,address_type_2,location_2,'dir','-4'])
            self.sub([address_type_2,location_2,address_type_1,location_1,'dir','-5'])
            self.sub(['dir','-4','dir','-5','dir','-6'])
            self.if_not_zero(['dir','-6'])
        elif operator == "<":
            self.sub([address_type_1,location_1,address_type_2,location_2,'dir','-5'])
            self.sub([address_type_2,location_2,address_type_1,location_1,'dir','-4'])
            self.sub(['dir','-4','dir','-5','dir','-6'])
            self.if_not_zero(['dir','-6'])
        elif operator == ">=":
            self.sub([address_type_1,location_1,address_type_2,location_2,'dir','-4'])
            self.sub([address_type_2,location_2,address_type_1,location_1,'dir','-5'])
            self.sub(['dir','-4','dir','-5','dir','-6'])
            self.add(['dir','-4','dir','-5','dir','-7'])
            self.if_zero(['dir','-7'])
            self.set(['dir','-6','int','1'])
            self.end_unt()
            self.if_not_zero(['dir','-6'])
        elif operator == "<=":
            self.sub([address_type_1,location_1,address_type_2,location_2,'dir','-5'])
            self.sub([address_type_2,location_2,address_type_1,location_1,'dir','-4'])
            self.sub(['dir','-4','dir','-5','dir','-6'])
            self.add(['dir','-4','dir','-5','dir','-7'])
            self.if_zero(['dir','-7'])
            self.set(['dir','-6','int','1'])
            self.end_unt()
            self.if_not_zero(['dir','-6'])
        else:
            print("Operator",operator,"not valid")
            sys.exit()

    def if_special(self,args):
        var_1,operator,var_2 = args[0],args[1],args[2]
        address_type_1 = 'dir'
        location_1 = '-8'
        address_type_2 = 'dir'
        location_2 = '-9'
        if self.get_type(var_1) == 'var':
            address_type_1 = 'dir'
            location_1 = self.replace_func([var_1])[0]
        elif self.get_type(var_1) == 'str':
            self.set(['dir','-8','str',var_1[1:-1]])
        else:
            self.set(['dir','-8','int',var_1])

        if self.get_type(var_2) == 'var':
            address_type_2 = 'dir'
            location_2 = self.replace_func([var_2])[0]
        elif self.get_type(var_2) == 'str':
            self.set(['dir','-9','str',var_2[1:-1]])
        else:
            self.set(['dir','-9','int',var_2])
        self.if_true([address_type_1,location_1,operator,address_type_2,location_2])

    def asg(self,args):
        #-11 == temp
        #-12 == _list_index
        #-13 == temp
        #-14 == input_var
        var_1,value = str(args[0]),str(args[2])
        print(value)
        output_type = 'dir'
        output_var = var_1
        input_type = 'dir'
        input_var = '-14'
        if self.get_type(var_1.split('[')[0]) == "list":
            if len(var_1.split('[')) == 2:
                var_1_index = var_1.split('[')[1][:-1]
                var_1 = var_1.split('[')[0]
                if var_1_index in self.variables:
                    self.cpy(['dir',self.variable_addresses[self.variables.index(var_1_index)],'dir','-11'])
                else:
                    self.set(['dir','-11','int',var_1_index])
                self.add(['dir',self.variable_addresses[self.variables.index(var_1)],'dir','-11','dir','-12'])
                self.inc(['dir','-12','int','1'])
                output_type = '!dir'
                output_var = '-12'
            else:
                output_var = self.replace_func([var_1])[0]
        if self.get_type(value.split('[')[0]) == 'var':
            self.cpy(['dir',self.replace_func([value])[0],'dir','-14'])
        elif self.get_type(value.split('[')[0]) == 'math':
            #ADD PARSER FOR MATH EXPRESSIONS
            pass
        elif self.get_type(value.split('[')[0]) == 'str':
            value_ = value[1:-1]
            self.set(['dir','-14','str',value_])
        elif self.get_type(value.split('[')[0]) == 'list':
            if len(value.split('[')) == 2:
                value_index = value.split('[')[1][:-1]
                value = value.split('[')[0]
                if value_index in self.variables:
                    self.cpy(['dir',self.variable_addresses[self.variables.index(value_index)],'dir','-11'])
                else:
                    self.set(['dir','-11','int',value_index])
                self.add(['dir',self.variable_addresses[self.variables.index(value)],'dir','-11','dir','-13'])
                self.inc(['dir','-13','int','1'])
                self.cpy(['!dir','-13','dir','-14'])
            else:
                self.cpy(['dir',self.replace_func([value])[0],'dir','-14'])
        elif self.get_type(value.split('[')[0]) == 'list_':
            list_ = value.split('[')[1]
            list_ = list_[:-1].split(",")
            print("LIST",var_1.split('[')[0])
            for idx,h in enumerate(list_):
                self.asg([var_1.split('[')[0]+'[' + str(idx) + ']','=',h])
            return
        else:
            self.set(['dir','-14','int',value])
        self.cpy([input_type,input_var,output_type,output_var])

    def list(self,args):
        #-10 == _list_start
        name,length = args[0],args[1]
        self.cpy(['dir','-10','dir',name])
        self.set(['!dir','-10','int',length])
        self.inc(['dir','-10','int',length])
        self.inc(['dir','-10','int','1'])

    def get_type(self,variable):
        if variable in self.ints:
            return "var"
        elif variable in self.lists:
            return "list"
        elif variable == '':
            return "list_"
        elif variable[0] == '"' and len(variable) == 3:
            return "str"
        elif variable[0] == '"' and len(variable) > 3:
            return "string"
        else:
            return None

    def compile_code (self,code):
        self.set(['dir','-10','int','0'])
        local_code = code
        for i in local_code:
            no_args = 0
            for e in self.possible_commands:
                if i[0] in e:
                    no_args = e[1]
                    func = e[0]
                    break
            if func == "if":
                self.if_special(i[-no_args:])
            else:
                func_to_call = getattr(self,func)
                if not no_args == 0:
                    func_to_call(i[-no_args:])
                else:
                    func_to_call()

editor = True

if __name__ == "__main__":
    args = sys.argv[:]
    if len(args) > 1:
        if not editor:

            args.pop(0)
            file = args.pop(0)
            run = False
            out = False
            debug = False
            compiled_print = False
            optimize = True
            c_compile = False
            name = 'output.hl'
            for i in args:
                if i == '-r':
                    run = True
                elif i == '-o':
                    out = True
                elif i[1] == 'n':
                    name = i[3:]
                elif i == '-d':
                    debug = True
                elif i == '-c':
                    compiled_print = True
                elif i == '-f':
                    optimize = False
                elif i == '-compile':
                    c_compile = True
            with open(file,'r') as brain_file:
                brain = brain_file.read()

            print("Parsing...")
            file = parse(file,possible_commands,is_file = True)
            print("Initializing BF Compiler")
            compiler = compiler(possible_commands,file)
            print("Compiling to BF")
            compiler.compile_code(file.parsed)
            print("Compiled to BF")

            if out:
                file_object  = open(name, 'w')
                file_object.write(compiler.bf_out)
                file_object.close()

            if compiled_print:
                print(compiler.bf_out)

            brain = compiler.bf_out

            if c_compile:
                print("Compiling to executable")
                compiler_bf_exe(brain,name)
                print("Compiled to executable")

            if optimize:
                brain = BF.optimize_brain(brain)

            if run:
                try:
                    print("Running BF")
                    print("------------------------")
                    print("")
                    BF.run(brain,debug)
                    print("")
                    print("------------------------")
                    print("Finished")
                except:
                    raise ValueError('Run Error')
    elif editor:
        file = 'test.hl'

        file = parse(file,possible_commands)
        compiler = compiler(possible_commands,file)
        print(file.parsed)
        compiler.compile_code(file.parsed)

        optimize = True
        print(compiler.bf_out)
        brain = compiler.bf_out

        #compiler_bf_exe(brain,"test.exe")

        optimized =  BF.optimize_brain(brain)

        #file_object  = open("test.txt", 'w')
        #file_object.write(brain)
        #file_object.close()


        if optimize:
            brain_run = optimized
        else:
            brain_run = brain
        try:
            BF.run(brain_run,True)
        except:
            raise ValueError('Run Error')

    else:
        print("Interactive Enviornment")
        print("------------------------")
        print("")
        new_input = []
        whole_program = []
        while True:
            new_input_raw = input()
            if new_input_raw == "exit":
                break
            new_input.append(new_input_raw)
            if new_input_raw == "":
                old_program = whole_program
                whole_program = whole_program + new_input
                new_input = []
                try:
                    file = parse(whole_program,possible_commands,is_file = False)
                    compiler_interactive = compiler(possible_commands,file.hidden_memory)
                    compiler_interactive.compile_code(file.parsed)
                    brain = compiler_interactive.bf_out
                    brain = BF.optimize_brain(brain)
                    print(" ---- Executing")
                    BF.run(brain,False)
                    print(" ---- Done")
                    print("")
                    to_remove = []
                    has_print = False
                    for command in whole_program:
                        if len(command.split()) > 1:
                            if command.split()[0] == "print" or command.split()[0] == "out" or command.split()[0] == "out_list" or command.split()[0] == "printf_list" or command.split()[0] == "print_direct":
                                to_remove.append(command)
                                has_print = True
                    for command in to_remove:
                        whole_program.remove(command)
                    if has_print:
                        print("")
                except:
                    print("------------------------")
                    print("ERROR")
                    print("------------------------")
                    whole_program = old_program
