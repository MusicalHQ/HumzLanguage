#mid_level_language to BFExtended


import BFExtendedHumza as BF
import copy

possible_commands = [['jmp',2],['out',3],['set',4],['unt',2],['inc',4],['end_unt',0],['cpy',4],['mve',4],['fwd',0],['bck',0],['plu',0],['bck',0],['loo',0],['end_loo',0],['out_now',1],['inp',2]]

class parse:
    def __init__(self,file,possible_commands):
        self.possible_commands = possible_commands
        self.raw = self.read(file)
        self.raw = self.imports(self.raw)
        #print(self.raw)
        self.functions = self.get_functions(self.raw)
        self.raw = self.functions[0]
        self.functions = self.functions[1]
        
        #print(self.raw)
        self.parsed = self.parse(self.raw)
        #print(self.functions)
        #print(self.parsed)
        self.parsed = self.replace_func(self.parsed)
        #print(self.parsed)
        
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
                new_raw = self.read(file)
                raw = new_raw + raw
            x += 1
        return raw
                
    
    def get_functions (self,raw_file):
        raw = raw_file
        x = 0
        functions = []
        while x < (len(raw)-1):
            #print(raw)
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
                #print(raw)
                raw.remove('}')
                #print(raw)
                self.possible_commands.append([new_func[0],no_args])
                functions.append(self.parse(new_func))
                x = -1
            x += 1
        #print(functions)
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
        #print(parsed)
        return parsed
    
    def replace_func (self,raw_file):
        raw = copy.deepcopy(raw_file)
        
        all_functions = []
        
        i = 0
        while i < (len(raw)):
            command = raw[i]
            #print(command)
            is_function = False
            functions = copy.deepcopy(self.functions)
            for e,function in enumerate(functions):
                if command[0] in function[0]:
                    is_function = True
                    break
            
            #print(self.functions)
            if is_function:
                command_sub = command
                command_sub.pop(0)
                
                function_sub = function[:]
                function_sub = function_sub[0]
                function_sub.pop(0)
                
                
                sub = dict(zip(function_sub,command_sub))
                
                #print(sub)
                new_function = []
                for e in function:
                    new_function.append(list(map(sub.get, e, e)))
                #print(new_function[1])
                new_function.pop(0)
                #print(new_function[1])
                index = i
                raw.pop(index)
                for e in new_function:
                    raw.insert(index,e)
                    index += 1
            #print(command)
            i += 1
            
        
        #for i in all_functions:
        #    index = i[0]
        #    raw.pop(index)
        #    for e in i[1]:
        #        raw.insert(index,e)
        #        index += 1
        
        return raw
        
        

class compiler:
    def __init__(self,possible_commands):
        self.bf_out = ''
        self.untils = []
        self.possible_commands = possible_commands
    
    def jmp (self,args,compiler=False):
        if not compiler:
            address_type,location = args[0],(int(args[1])+10)
        else:
            address_type,location = args[0],(int(args[1]))
        self.bf_out = self.bf_out + 'r[-]'
        for i in range(location):
            self.bf_out = self.bf_out + '+'
        self.bf_out = self.bf_out + 'p'
        if address_type == '!dir':
            if not compiler:
                self.bf_out = self.bf_out + 'p>>>>>>>>>>'
            else:
                self.bf_out = self.bf_out + 'p'
    
    def inp (self,args):
        address_type,location = args[0],args[1]
        self.jmp([address_type,location])
        self.bf_out = self.bf_out + ','
            
    def set (self,args,compiler=False):
        address_type,location = args[0],args[1]
        data_type,value = args[2],args[3]
        self.jmp([address_type,location],compiler)
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
    
    def unt (self,args,compiler = False):
        self.jmp(args,compiler)
        self.untils.append([args,compiler])
        self.bf_out = self.bf_out + '['
    
    def end_unt (self):
        args = self.untils.pop(len(self.untils)-1)
        self.jmp(args[0],args[1])
        self.bf_out = self.bf_out + ']'
    
    def inc (self,args,compiler = False):
        address_type,location,data_type,value = args[0],args[1],args[2],args[3]
        self.jmp([address_type,location],compiler)
        if data_type == 'str':
            value = ord(value)
        elif data_type == 'int':
            value = int(value)
        char = '-'
        if value > 0:
            char = '+'
        for i in range(abs(value)):
            self.bf_out = self.bf_out + char
    
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
        self.set([address_type_3,location_3,'int',0])
        self.unt([address_type_1,location_1])
        self.inc([address_type_1,location_1,'int',-1])
        self.inc([address_type_2,location_2,'int',1])
        self.inc([address_type_3,location_3,'int',1])
        self.end_unt()
        self.jmp([address_type_3,location_3])
        self.bf_out = self.bf_out + '[-]'
    
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

file = parse('test.hl',possible_commands)
compiler = compiler(possible_commands)
compiler.compile_code(file.parsed)
#print(len(compiler.bf_out))
BF.run(compiler.bf_out,True)