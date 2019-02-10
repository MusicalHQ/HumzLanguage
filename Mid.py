#Mid
import BF

parsed = []

with open('ml.txt','r') as f:
    for line in f:
        for word in line.split():
            parsed.append(word)

ml_input = []

possible_commands = [['jmp',2],['out',2],['set',4],['while',2],['until',2],['inc',4],['enduntil',0],['cpy',4],['add',6]]

while len(parsed) > 0:
    parsed_command = []
    command = parsed.pop(0)
    parsed_command.append(command)
    
    for i in possible_commands:
        args = i[1]
        if i[0] == command:
            break
    
    for i in range(args):
        parsed_command.append(parsed.pop(0))    
    ml_input.append(parsed_command)

print(ml_input)

class compiler:
    def __init__(self):
        self.bf_out = ''
        self.mem_counter = 0
        self.memory = []
        self.untils = []
    
    def check_memory(self):
        for i in range(len(self.memory)):
            if self.memory[i] < 0:
                self.memory[i] = 0
    
    def jmp (self,location,address_type='dir'):
        if address_type == 'dir':
            location = int(location)
            if location > len(self.memory)-1:
                for i in range(location-(len(self.memory)-1)):
                    self.memory.append(0)
            delta = location - self.mem_counter
            char = '<'
            if delta > 0:
                char = '>'
            for i in range(abs(delta)):
                self.bf_out = self.bf_out + char
            self.mem_counter = location
 
    def out (self,address_type,location):
        if address_type == 'dir':
            location = int(location)
            self.jmp(location)
            self.bf_out = self.bf_out + '.'
    
    def set_val (self,address_type,location,data_type,value):
        if address_type == 'dir':
            location = int(location)
            self.jmp(location)
            if data_type == "str":
                value = ord(value)
            if data_type == "int":
                value = int(value)
            delta = value - self.memory[self.mem_counter]
            char = '-'
            if delta > 0:
                char = '+'
            for i in range(abs(delta)):
                self.bf_out = self.bf_out + char
            self.memory[self.mem_counter] = value
    
    def inc (self,address_type,location,data_type,value):
        if address_type == 'dir':
            location = int(location)
            self.jmp(location)
            if data_type == "str":
                value = ord(value)
            if data_type == "int":
                value = int(value)
            char = '-'
            if value > 0:
                char = '+'
            for i in range(abs(value)):
                self.bf_out = self.bf_out + char
            self.memory[self.mem_counter] += value
    
    def until (self,address_type,location):
        if address_type == 'dir':
            location = int(location)
            self.untils.append(location)
            self.jmp(location)
            self.bf_out = self.bf_out + '['
    
    def end_until (self):
        location = self.untils.pop(len(self.untils)-1)
        self.jmp(location)
        self.bf_out = self.bf_out + ']'
    
    def cpy (self,address_type_1,location_1,address_type_2,location_2):
        if address_type_1 == 'dir':
            if address_type_2 == 'dir':
                location_1 = int(location_1)
                location_2 = int(location_2)
                self.set_val('dir',location_2,'int',0)
                self.jmp('dir',location_2)
                self.jmp('dir',location_1)                
                for i in range(10):
                    self.memory.append(0)
                location_3 = len(self.memory)
                self.set_val('dir',location_3,'int',0)
                self.until('dir',location_1)
                self.inc('dir',location_1,'int',-1)
                self.inc('dir',location_2,'int',1)
                self.inc('dir',location_3,'int',1)
                self.end_until()
                self.until('dir',location_3)
                self.inc('dir',location_1,'int',1)
                self.inc('dir',location_3,'int',-1)
                self.end_until()
    
    def add (self,address_type_1,location_1,address_type_2,location_2,address_type_3,location_3):
        if address_type_1 == 'dir':
            if address_type_2 == 'dir':
                if address_type_3 == 'dir':
                    location_1,location_2,location_3 = int(location_1),int(location_2),int(location_3)
                    original = len(self.memory)
                    self.cpy('dir',location_1,'dir',original)
                    first = len(self.memory)
                    self.cpy('dir',location_2,'dir',first)
                    self.until('dir',original)
                    self.inc('dir',original,'int',-1)
                    self.inc('dir',first,'int',1)
                    self.end_until()
                    self.cpy('dir',first,'dir',location_3)
                    #self.set_val('dir',first,'int',0)
                    
                    
        
compiler = compiler()

for i in ml_input:
    if i[0] == 'jmp':
        compiler.jmp(i[2],i[1])
    if i[0] == 'out':
        compiler.out(i[1],i[2])
    if i[0] == 'set':
        compiler.set_val(i[1],i[2],i[3],i[4])
    if i[0] == 'inc':
        compiler.inc(i[1],i[2],i[3],i[4])
    if i[0] == 'until':
        compiler.until(i[1],i[2])
    if i[0] == 'enduntil':
        compiler.end_until()
    if i[0] == 'cpy':
        compiler.cpy(i[1],i[2],i[3],i[4])
    if i[0] == 'add':
        compiler.add(i[1],i[2],i[3],i[4],i[5],i[6])
    compiler.check_memory(),

print(compiler.bf_out)
print(compiler.memory)
BF.run(compiler.bf_out,True)

            