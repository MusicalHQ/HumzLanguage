'''
This program converts a BF+ code given as a command line argument into a valid C program which is then compiled by this same program
The other command line argument that must be given is the name of the executable file that will be created

'''


import sys
import os

preamble = '''
#include <stdio.h>

char array[30000] = {0};
char *start = array;
char *ptr = array;

int main()
{
'''

end = '''
return 0;
}
'''

outfile = sys.argv[1]
instructions = sys.argv[2]

transpiled = ""

for instruction in instructions:
    if instruction == ">":
        transpiled += "++ptr;\n"
    elif instruction == "<":
        transpiled += "--ptr;\n"
    elif instruction == "+":
        transpiled += "++*ptr;\n"
    elif instruction == "-":
        transpiled += "--*ptr;\n"
    elif instruction == ".":
        transpiled += "putchar(*ptr);\n"
    elif instruction == ",":
        transpiled += "*ptr=getchar();\n"
    elif instruction == "[":
        transpiled += "while(*ptr){\n"
    elif instruction == "]":
        transpiled += "}\n"
    elif instruction == "c":
        transpiled += "*ptr = 0;\n"
    elif instruction == "r":
        transpiled += "ptr = start;\n"
    elif instruction == "p":
        transpiled += "ptr = start + *ptr;\n"

with open(outfile + ".c", "w") as f:
    f.write(preamble + transpiled + end)

os.system("gcc -Wall -g " + outfile + ".c " + "-o " + outfile)
os.system("del " + outfile + ".c")
