#cleaned Mid

import BF

possible_commands = [['jmp',2],['out',2],['set',4],['unt',2],['inc',4],['end_unt',0],['cpy',4],['clr',2],['fwd',0],['bck',0],['out_now',0],['plu',0],['min',0],['loo',0],['end_loo',0],['cpy_nxt',0]]

class parse:
    def __init__(self,file,possible_commands):
        self.possible_commands = possible_commands
        self.raw = self.read(file)
        self.parsed = self.parse(self.raw)
        
    def read (self,file):
        raw = []
        with open(file,'r') as f:
            for line in f:
                for word in line.split():
                    raw.append(word)
        return raw
    
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
 
class compiler:
    def __init__(self,possible_commands):
        self.bf_out = ''
        self.mem_counter = 0
        self.memory_length = 0
        self.untils = []
        self.possible_commands = possible_commands
    
    def jmp (self,args):
        address_type,location = args[0],args[1]
        if address_type == 'dir':
            location = int(location)
            if location > self.memory_length:
                self.memory_length = location
            delta = location - self.mem_counter
            char = '<'
            if delta > 0:
                char = '>'
            for i in range(abs(delta)):
                self.bf_out = self.bf_out + char
            self.mem_counter = location
            
    def clr (self,args):
        self.jmp(args)
        self.bf_out = self.bf_out + '[-]'
    
    def set (self,args):
        address_type,location,data_type,value = args[0],args[1],args[2],args[3]
        self.clr([address_type,location])
        if data_type == 'str':
            value = ord(value)
        elif data_type == 'int':
            value = int(value)
        for i in range(value):
            self.bf_out = self.bf_out + '+'
    
    def out (self,args):
        self.jmp(args)
        self.bf_out = self.bf_out + '.'
        
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
    
    def unt (self,args):
        self.jmp(args)
        self.untils.append(args)
        self.bf_out = self.bf_out + '['
    
    def end_unt (self):
        args = self.untils.pop(len(self.untils)-1)
        self.jmp(args)
        self.bf_out = self.bf_out + ']'
        
    def cpy (self,args):
        #DOESN'T DO INDIRECT ADDRESSING!!!!!!!!!!!
        address_type_1,location_1,address_type_2,location_2 = args[0],args[1],args[2],args[3]
        location_1 = int(location_1)
        location_2 = int(location_2)
        self.set([address_type_2,location_2,'int',0])
        self.jmp([address_type_1,location_1])                
        location_3 = self.memory_length+1
        self.set(['dir',location_3,'int',0])
        self.unt([address_type_1,location_1])
        self.inc([address_type_1,location_1,'int',-1])
        self.inc([address_type_2,location_2,'int',1])
        self.inc(['dir',location_3,'int',1])
        self.end_unt()
        self.unt(['dir',location_3])
        self.inc([address_type_1,location_1,'int',1])
        self.inc(['dir',location_3,'int',-1])
        self.end_unt()        
    
    def fwd (self):
        self.bf_out = self.bf_out + '>'
        self.mem_counter += 1
        
    def bck (self):
        self.bf_out = self.bf_out + '<'
        self.mem_counter -= 1
        if self.mem_counter < 0:
            self.mem_counter = 0
    
    def plu (self):
        self.bf_out = self.bf_out + '+'

    def min (self):
        self.bf_out = self.bf_out + '-'  
    
    def loo (self):
        self.bf_out = self.bf_out + '['

    def end_loo (self):
        self.bf_out = self.bf_out + ']'       
    
    def out_now (self):
        self.bf_out = self.bf_out + '.'
    
    def cpy_nxt (self):
        pass
        
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
 
file = parse('ml.txt',possible_commands)
compiler = compiler(possible_commands)
compiler.compile_code(file.parsed)
print(compiler.bf_out)
BF.run(compiler.bf_out,True)
