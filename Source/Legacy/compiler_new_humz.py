'''
This program converts a BF+ code given as a command line argument into a valid C program which is then compiled by this same program
The other command line argument that must be given is the name of the executable file that will be created

'''


import sys
import os

def compiler_bf_exe(instructions,outfile):
    preamble = '''
    #include <stdio.h>

    char array[30000] = {0};
    char *start = array;
    char *ptr = array;

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

    translation = {">": "++ptr;\n",
                   "<": "--ptr;\n",
                   "+": "++*ptr;\n",
                   "-": "--*ptr;\n",
                   ".": "putchar(*ptr);\n",
                   ",": "*ptr=getchar();\n",
                   "[": "while(*ptr){\n",
                   "]": "}\n",
                   "c": "*ptr=0;\n",
                   "r": "ptr = start;\n",
                   "p": "ptr = start + *ptr;\n",
                   "o": "printf(\"%d\", *ptr);\n"}

    transpiled = ""

    for instruction in instructions:
        if instruction in translation.keys():
            transpiled += translation[instruction]

    with open(outfile + ".c", "w") as f:
        f.write(preamble + transpiled + end)

    os.system("gcc -Wall -g " + outfile + ".c " + "-o " + outfile)
    #os.system("del " + outfile + ".c")
