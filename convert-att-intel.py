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

def toIntel(inputString):

    commentBlock = False
    tab = 0 # Number of tabulations at line beginning
    isLabel = False
    clobbersCount = 0
    clobberLine = 0
    variables = dict()
    label = ""
    index = ""

    # print inputString
    with open("testfile.att", "r") as f:
        inputString = f.read()

    # First, split the input string in lines
    lines = inputString.splitlines()


    # I first need to parse the clobbers to figure out the name of the variables.
    # The third clobber line can be dropped; it's simply the registers used.
    # For the first two clobber lines, we have to build a dictionary with the
    # index or label of the variable as key, and the name of the variable as value.
    i = 0
    while i < len(lines):
        line = lines[i]
        line = line.strip()

        # If clobber line.
        if re.search('^:', line):
            del lines[i]
            clobberLine += 1
            # If third clobber line, skip it.
            if clobberLine == 3:
                continue
            else:
                line = re.sub(r'((\/\/)|(\/\*)).*', '', line) # Remove comments at the end of the line
                tokens = line.split(',')
                for token in tokens:
                    label = ""
                    # Search for a label
                    match = re.search('\[(\w+)\]', token)
                    if match:
                        label = match.group(1)
                    index = str(clobbersCount)
                    # Search for the variable name
                    match = re.search('\((\w+)\)', token)
                    if match:
                        if label != "":
                            variables[label] = match.group(1)
                        variables[index] = match.group(1)
                    else:
                        print("Error, could not find variable name.")
                    clobbersCount += 1

        else:
            i += 1


    for i in range(len(lines)):
        line = lines[i]
        line = line.strip()
        isLabel = False

        # Comment block detection
        if line[0] + line[1] == "/*":
            commentBlock = True

        if not commentBlock:
            if "__asm__" in line:
                line = "__asm{"
                tab += 1
            if line == ");":
                line = "}"
                tab -= 1
            # Remove the '%'
            line = re.sub(r'%?%(?P<reg>[a-zA-Z]+)', '\g<reg>', line)
            # Remove quotes
            line = re.sub(r'"', '', line)
            # Remove explicit \n
            line = re.sub(r'\\n', '', line)

            # Those should only be applied on instructions parameters to void facking up any hypothetical comment.
            line = re.sub(r'\$(?P<imm>\d+)', '\g<imm>', line)
            line = re.sub(r'\(', '[', line)
            line = re.sub(r'\)', ']', line)

            # Change the aliases with the true variable name.
            for k in variables:
                pattern = '%\[?' + k + '\]?'
                if re.search(pattern, line):
                    line = re.sub(pattern, variables[k], line)

            tokens = line.split(' ')

            # Translate the offset
            for i in range(len(tokens)):
                token = tokens[i]
                token = re.sub(r'(?P<offset>\-\d+)\[(?P<var>\w+)\]', '[\g<var>\g<offset>]', token)
                token = re.sub(r'(?P<offset>\d+)\[(?P<var>\w+)\]', '[\g<var>+\g<offset>]', token)
                tokens[i] = token

            # If two parameters are glued together with a comma, split them.
            if len(tokens) > 1 and re.search(',.+', tokens[1]):
                subtokens = tokens[1].split(',')
                tokens[1] = subtokens[0]
                tokens.insert(2, subtokens[1])

            # If there are two arguments and the second one is not a comment, swap them.
            if len(tokens) > 2 and not re.search('^\/\/|^\/\*', tokens[2]):
                tmp = tokens[1]
                tokens[1] = tokens[2] + ","
                tokens[2] = re.sub(r'(?P<arg>.*),$', '\g<arg>', tmp) + ";"
            if re.search(':$', tokens[0]):
                isLabel = True

            # Merge tokens back
            line = ' '.join(tokens)

        # End of comment block detection
        if "*/" in line:
            commentBlock = False

        # Highlight the label by shifting them to the left.
        if isLabel:
            tab -= 1
        lines[i] = "\t"*tab + line
        if isLabel:
            tab += 1
        print lines[i]

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