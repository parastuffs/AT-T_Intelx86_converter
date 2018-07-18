"""
Usage:
    convert-att-intel.py [-s <input_code>] [-a|--to-att] [-i|--to-intel]
    convert-att-intel.py (--help|-h)

Options:
    -s <input_code>    Input string containing the full code to convert
    -a --to-att        Convert from Intelx86 to AT&T
    -i --to-intel      Convert from AT&T to Intelx86

    -h --help          Print this help
"""

from docopt import docopt
import re

def toATT(inputString):

    commentBlock = False

    # print inputString
    with open("testfile.att", "r") as f:
        inputString = f.read()

    # print inputString
    # First, split the input string in lines
    lines = inputString.splitlines()
    # print lines
    # Remove extra spaces and tabulations
    for i in range(len(lines)):
        line = lines[i]
        line = line.strip()

        # Comment block detection
        if line[0] + line[1] == "/*":
            commentBlock = True
            # print line
        if "*/" in line:
            commentBlock = False

        if not commentBlock:
            if "__asm__" in line:
                line = "__asm{"
            # Remove the '%'
            line = re.sub(r'%', '', line)
            # line = re.sub(r'%%?(?P<reg>\w{3,4})', '\g<reg>', line)
            line = re.sub(r'"', '', line)
            line = re.sub(r'\\n', '', line)

            # Those should only be applied on instructions parameters to void facking up any hypothetical comment.
            line = re.sub(r'\$(?P<imm>\d+)', '\g<imm>', line)
            line = re.sub(r'\(', '[', line)
            line = re.sub(r'\)', ']', line)

            tokens = line.split(' ')
            if len(tokens) > 1 and re.search(',.+', tokens[1]):
                print tokens[1]
                subtokens = tokens[1].split(',')
                tokens[1] = subtokens[0]
                tokens.insert(2, subtokens[1])
                print tokens
            # If there are two arguments and the second one is not a comment.
            if len(tokens) > 2 and not re.search('^\/\/|^\/\*', tokens[2]):
                tmp = tokens[1]
                tokens[1] = tokens[2]
                tokens[2] = tmp
                print tokens




        lines[i] = line



    # print lines



#def toIntel(inputString):




if __name__ == '__main__':

    inputString = ""
    isToATT = False
    isToIntel = False

    args = docopt(__doc__)
    if args["-s"]:
        inputString = args["-s"]
    if args["--to-att"]:
        isToATT = True
    if args["--to-intel"]:
        isToIntel = True

    if isToATT and isToIntel:
        print "Make up your mind."
        exit()

    if isToATT:
        toATT(inputString)
    elif isToIntel:
        toIntel(inputString)