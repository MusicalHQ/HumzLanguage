# Welcome to the HumzLanguage docs

### Getting Started

To download the compiler, download the lastest release from https://github.com/humz2k/HumzLanguage/releases. Contained in the zip are a few example programs, and the standard libraries.

All Humzlanguage Programs have the file extension `.hl`. To run a program, navigate to the directory containing the compiler in command prompt, and point it to the file you want to run.

For example:

`humzlanguage hello_world.hl`

#### Running the program

The above command will not actually output anything - you must specify this as an argument.

Possible run arguments are:


* `-r` - this will run the program. With this flag, the compiler behaves like python would

* `-o` - this outputs the Brainfuck output to a file, specified in the next flag

* `-n:` - this specifies the file to output to - e.g. `-n:brain_fuck_out.hlbf`

* `-compile` - this compiles the program to a binary to the file specified in the `-n:` flag

* `-c` - this prints the Brainfuck output

* `-d` - this turns on debug mode - the memory at the end of the program is printed

So, to run the hello world program contained in the zip, navigate to the directory and then type:

`HumzLanguage hello_world.hl -r`
