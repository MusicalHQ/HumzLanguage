'''
Potential future optimizations:
- Repetitions of o
- Removing statements that cancel out
- Dynamically allocating array size to fit the maximum index of the program



'''
import sys
import os

preamble = '''
#include <stdio.h>

unsigned int array[30000] = {0};
unsigned int *start = array;
unsigned int *ptr = array;
unsigned int input;

int main()
{
'''

end = '''
printf("Memory: ");
for (int i = 0; i < 50; i++)
{
    printf("%d, ", array[i]);
}
return 0;
}
'''

def compiler_bf_exe(instructions,outfile):
    # Optional debugging code
    debug = "for (int i = 0; i < 50; i++){printf(\"%d, \", array[i]);}\nprintf(\"\\n\");"

    transpiled = ""

    i = 0;
    instruction_length = len(instructions)

    translation = {">": "ptr += ",
                   "<": "ptr -= ",
                   "+": "*ptr += ",
                   "-": "if(*ptr != 0) {*ptr -= ",
                   ".": "putchar(*ptr);\n",
                   ",": "*ptr=getchar();\n",
                   "[": "while(*ptr){\n",
                   "]": "}\n",
                   "c": "*ptr=0;\n",
                   "r": "ptr = start;\n",
                   "p": "ptr = start + *ptr;\n",
                   "o": "printf(\"%d\", *ptr);\n"}


    while i != instruction_length:
        instruction = instructions[i]
        if instruction in [">", "<", "+", "-"]: # Only instructions that can be compressed if repeated
            remaining_instructions = instructions[i+1:]

            
            # Work the number of consecutive instances of the instruction that directly follow the instruction itself
            n_repetitions = 0
            for remaining_instruction in remaining_instructions:
                if remaining_instruction != instruction:
                    break
                n_repetitions += 1

            n_repetitions += 1 # Include first occurence 

            if instruction in [">", "<", "+"]: # Same line ending
                transpiled += translation[instruction] + str(n_repetitions) + ";\n"
            elif instruction == "-":
                transpiled += translation[instruction] + str(n_repetitions) + ";}\n"

            i += n_repetitions # Skip forward by the number of symbols we have already parsed 
        else:
            transpiled += translation[instruction]
            i += 1

    with open(outfile + ".c", "w") as f:
        f.write(preamble + transpiled + end)

    os.system("gcc -Wall -g " + outfile + ".c " + "-o " + outfile)
    os.system("del " + outfile + ".c")
