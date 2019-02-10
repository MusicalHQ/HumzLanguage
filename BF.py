#brainfuck interpreter
import sys



def run(brain,show_memory = False):
    memory = [0]
    
    counter = 0
    e = 0
    while e < len(brain):
        i = brain[e]
        if i == '+':
            memory[counter] += 1
        elif i == '-':
            if memory[counter] > 0:
                memory[counter] -= 1
        elif i == '>':
            counter += 1
            if counter > (len(memory)-1):
                memory.append(0)
        elif i == '<':
            if counter > 0:
                counter -= 1
        elif i == '.':
            print(chr(memory[counter]),end='')
        elif i == ',':
            try:
                memory[counter] = ord(str(input("")))
            except:
                memory[counter] = 10
        elif i == '[':
            if memory[counter] == 0:
                loop_counter = 1
                while not loop_counter == 0:
                    e += 1
                    if brain[e] == '[':
                        loop_counter += 1
                    elif brain[e] == ']':
                        loop_counter -= 1
        elif i == ']':
            if not memory[counter] == 0:
                loop_counter = 1
                while not loop_counter == 0:
                    e -= 1
                    if brain[e] == ']':
                        loop_counter += 1
                    elif brain[e] == '[':
                        loop_counter -= 1
        e += 1
    if show_memory:
        print("")
        print(memory)

if __name__ == "__main__":       
    try:
        file = sys.argv[1]
        with open(file,'r') as brain_file:
            brain = brain_file.read()    
    except:
        print("No args passed")
        brain = ''
    run(brain)