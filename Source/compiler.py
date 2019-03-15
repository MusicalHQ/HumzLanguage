import sys
import os

preamble = '''
#include <stdio.h>

unsigned int array[30000] = {0};
unsigned int *start = array;
unsigned int *ptr = array;

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

outfile = sys.argv[1]
instructions = sys.argv[2]

with open(instructions, "r") as f:
    instructions = f.readline()

# Optional debugging code
debug = "for (int i = 0; i < 50; i++){printf(\"%d, \", array[i]);}\nprintf(\"\\n\");"

translation = {">": "++ptr;\n",
               "<": "--ptr;\n",
               "+": "++*ptr;\n",
               "-": "if(*ptr != 0) {--*ptr;}\n",
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
#        transpiled += debug

with open(outfile + ".c", "w") as f:
    f.write(preamble + transpiled + end)

os.system("gcc -Wall -g " + outfile + ".c " + "-o " + outfile)
os.system("del " + outfile + ".c")
