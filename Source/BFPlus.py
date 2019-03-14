#brainfuck extended
import sys

def optimize_brain(brain):
    brain = brain + ' '
    e = 0
    brain_new = ''
    while e < len(brain):
        i = brain[e]
        if i == '[' and brain[e+1] == '-' and brain[e+2] == ']':
            brain_new = brain_new + 'c'
            e += 2
        elif i == '+':
            f = e
            total = 0
            #print(e+f)
            while brain[f] == '+' and f < (len(brain)-1):
                f += 1
            brain_new = brain_new + 'a' + str(f-e) + 'b'
            e = f
            e -= 1
        elif i == '-':
            #print('negative')
            f = e
            total = 0
            #print(e+f)
            while brain[f] == '-' and f < (len(brain)-1):
                f += 1
            brain_new = brain_new + 'a' + str(-(f-e)) + 'b'
            e = f
            e -= 1
        else:
            brain_new = brain_new + i
        e += 1
    return brain_new


def run(brain,show_memory = False):
    memory = [0]
    brain = brain + " "
    counter = 0
    e = 0
    while e < len(brain):
        i = brain[e]
        if i == '+':
            f = 0
            total = 0
            while brain[e + f] == '+' and (e+f) < (len(brain)-1):
                f += 1
            memory[counter] += f
            e += f
            e -= 1
            #memory[counter] += 1
        elif i == 'a':
            f = e
            total = 0
            while not (brain[f] == 'b') and f < (len(brain)-1):
                f += 1
            number = int(brain[(e+1):f])
            memory[counter] += number
            if memory[counter] < 0:
                memory[counter] = 0
            e = f

        elif i == 'c':
            memory[counter] = 0

        elif i == 'p':
            counter = memory[counter]
            if counter > (len(memory)-1):
                for i in range(counter - (len(memory)-1)):
                    memory.append(0)
        elif i == 'r':
            counter = 0
        #elif i == 'l':
        #    counter = len(memory)-1
            #memory.append(0)
        elif i == '-':
            f = 0
            total = 0
            while brain[e + f] == '-' and (e+f) < (len(brain)-1):
                f += 1
            memory[counter] -= f
            if memory[counter] < 0:
                memory[counter] = 0
            e += f
            e -= 1
            #if memory[counter] > 0:
            #    memory[counter] -= 1
        elif i == '>':
            counter += 1
            if counter > (len(memory)-1):
                memory.append(0)
        elif i == '<':
            if counter > 0:
                counter -= 1
        elif i == '.':
            print(chr(memory[counter]),end='')
        elif i == 'o':
            print(memory[counter],end='')
        elif i == ',':
            memory[counter] = int(input(""))
        elif i == '[':
            if memory[counter] == 0:
                loop_counter = 1
                while not loop_counter == 0:
                    e += 1
                    #print(brain[e],loop_counter)
                    if brain[e] == '[':
                        loop_counter += 1
                    elif brain[e] == ']':
                        loop_counter -= 1
            elif brain[e+1] == '-' and brain[e+2] == ']':
                memory[counter] = 0
                e += 2

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
    #try:
    #    file = sys.argv[1]
    #    with open(file,'r') as brain_file:
    #        brain = brain_file.read()
    #except:
    #    print("No args passed")
    #    file = 'bf.bf'
    #    with open(file,'r') as brain_file:
    #        brain = brain_file.read()
    brain = '++[-]++'
    print(brain)
    brain = optimize_brain(brain)
    print(brain)
    run(brain,True)
