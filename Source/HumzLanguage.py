#mid_level_language to BFExtended


import BFPlus as BF
import copy
import sys

possible_commands = [['jmp',2],['out',3],['set',4],['unt',2],['inc',4],['end_unt',0],['cpy',4],['mve',4],['fwd',0],['bck',0],['plu',0],['loo',0],['end_loo',0],['out_now',1],['inp',2],['set_hidden_memory',1],['var',1]]

class parse:
    def __init__(self,file,possible_commands,recursion_limit = 1000,import_limit = 100):
        self.recursion_limit = recursion_limit
        self.possible_commands = possible_commands
        self.raw = self.read(file)
        self.variables = None
        self.variable_addresses = None
        self.import_limit = import_limit
        self.imported = []
        counter = 0
        self.hidden_memory = 0
        while self.has_import(self.raw) and counter < self.import_limit:
            counter += 1
            self.raw = self.imports(self.raw)

        self.functions = self.get_functions(self.raw)
        self.raw = self.functions[0]
        self.functions = self.functions[1]
        self.parsed = self.parse(self.raw)
        counter = 0
        while self.has_func(self.parsed) and counter < self.recursion_limit:
            counter += 1
            self.parsed = self.replace_func(self.parsed)

        if self.has_func(self.parsed):
            print("Reached function limit")
            raise ValueError('Reached function in function limit')

        self.parsed = self.set_hidden_memory(self.parsed)
        self.parsed = self.get_var_address(self.parsed)

    def get_var_address(self,parsed):
        variables = []
        variable_addresses = []
        for i in parsed[:]:
            if i[0] == 'var':
                variables.append(i[1])
                parsed.remove(i)
        for i in variables:
            variable_addresses.append(-self.hidden_memory)
            self.hidden_memory += 1
        for i in range(len(parsed)):
            for e in range(len(parsed[i])):
                if parsed[i][e] in variables and not (parsed[i][e-1] == 'int' or parsed[i][e-1] == 'str'):
                    parsed[i][e] = variable_addresses[variables.index(parsed[i][e])]
        self.variables = variables
        self.variable_addresses = variable_addresses
        print(self.variable_addresses)
        print(self.variables)
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

    def read (self,file):
        raw = []
        with open(file,'r') as f:
            for line in f:
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
            for i in self.possible_commands:
                args = i[1]
                if i[0] == command:
                    break
            for i in range(args):
                parsed_command.append(raw.pop(0))
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
    def __init__(self,possible_commands,hidden_memory = 20):
        self.bf_out = ''
        self.untils = []
        self.hidden_memory = 20
        if hidden_memory > self.hidden_memory:
            self.hidden_memory = hidden_memory
        self.possible_commands = possible_commands

    def jmp (self,args):
        address_type,location = args[0],(int(args[1])+self.hidden_memory)
        self.bf_out = self.bf_out + 'r[-]'
        for i in range(location):
            self.bf_out = self.bf_out + '+'
        self.bf_out = self.bf_out + 'p'
        if address_type == '!dir':
            self.bf_out = self.bf_out + 'p'
            for i in range(self.hidden_memory):
                self.bf_out = self.bf_out + '>'

    def inp (self,args):
        address_type,location = args[0],args[1]
        self.jmp([address_type,location])
        self.bf_out = self.bf_out + ','

    def set (self,args):
        address_type,location = args[0],args[1]
        data_type,value = args[2],args[3]
        self.jmp([address_type,location])
        self.bf_out = self.bf_out + '[-]'
        if data_type == 'str':
            value = ord(value)
        elif data_type == 'int':
            value = int(value)
        for i in range(value):
            self.bf_out = self.bf_out + '+'

    def out (self,args):
        address_type,location,data_type = args[0],args[1],args[2]
        self.jmp([address_type,location])
        if data_type == 'int':
            self.bf_out = self.bf_out + 'o'
        elif data_type == 'str':
            self.bf_out = self.bf_out + '.'

    def unt (self,args):
        self.jmp(args)
        self.untils.append(args)
        self.bf_out = self.bf_out + '['

    def end_unt (self):
        args = self.untils.pop(len(self.untils)-1)
        self.jmp(args)
        self.bf_out = self.bf_out + ']'

    def inc (self,args):
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
        data_type = args[0]
        self.bf_out = self.bf_out + '.'
        if data_type == 'int':
            self.bf_out = self.bf_out + 'o'
        elif data_type == 'str':
            self.bf_out = self.bf_out + '.'

    def compile_code (self,code):
        local_code = code
        for i in local_code:
            no_args = 0
            for e in self.possible_commands:
                if i[0] in e:
                    no_args = e[1]
                    func = e[0]
                    break
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
            with open(file,'r') as brain_file:
                brain = brain_file.read()

            try:
                file = parse(file,possible_commands)
            except:
                raise ValueError('Parsing error')

            compiler = compiler(possible_commands,file.hidden_memory)
            try:
                compiler.compile_code(file.parsed)
            except:
                raise ValueError('Compiler Error')

            if out:
                file_object  = open(name, 'w')
                file_object.write(compiler.bf_out)
                file_object.close()

            if compiled_print:
                print(compiler.bf_out)

            brain = compiler.bf_out

            if optimize:
                brain = BF.optimize_brain(brain)

            if run:
                try:
                    BF.run(brain,debug)
                except:
                    raise ValueError('Run Error')
    elif editor:
        file = 'test.hl'

        file = parse(file,possible_commands)
        compiler = compiler(possible_commands,file.hidden_memory)
        compiler.compile_code(file.parsed)

        optimize = True
        print(compiler.bf_out)
        brain = compiler.bf_out
        optimized =  BF.optimize_brain(brain)

        file_object  = open("test.txt", 'w')
        file_object.write(brain)
        file_object.close()


        if optimize:
            brain_run = optimized
        else:
            brain_run = brain
        try:
            BF.run(brain_run,True)
        except:
            raise ValueError('Run Error')

    else:
        print("No args passed - see docs for help")
