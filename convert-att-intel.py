"""
Usage:
    convert-att-intel.py [-s <input_code>] [-a|--to-att] [-i|--to-intel]
    convert-att-intel.py (--help|-h)

Options:
    -s <input_code>    Input string containing the full code to convert
    -a --to-att        Convert from Intelx86 to AT&T
    -i --to-intel      Convert from AT&T to Intelx86

    -h --help          Print this help

If neither -a nor -i are provided, the script starts a GUI.
"""

from docopt import docopt
import re
from sets import Set
try:
    # Python 2
    import Tkinter as tk
except ImportError:
    # Python 3
    import tkinter as tk
import webbrowser
import pyperclip

# Register names pattern
registers = ["xmm\d", "[re][abcds][ix]"]


##########    #####            ########   ##      ##  ##########  #########  ##         
    ##      ##     ##             ##      ###     ##      ##      ##         ##         
    ##      ##     ##             ##      ## ##   ##      ##      ##         ##         
    ##      ##     ##             ##      ##  ##  ##      ##      ######     ##         
    ##      ##     ##             ##      ##   ## ##      ##      ##         ##         
    ##      ##     ##             ##      ##     ###      ##      ##         ##         
    ##        #####    ####### ########   ##      ##      ##      #########  ######### 

def toIntel(inputString):

    commentBlock = False
    tab = 0 # Number of tabulations at line beginning
    isLabel = False
    clobbersCount = 0
    clobberLine = 0
    variables = dict()
    label = ""
    index = ""
    outputString = ""

    # print inputString
    # with open("testfile.att", "r") as f:
    #     inputString = f.read()

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

            tokens = re.split('\s', line)

            # Translate the offset
            for j in range(len(tokens)):
                token = tokens[j]
                token = re.sub(r'(?P<offset>\-\d+)\[(?P<var>\w+)\]', '[\g<var>\g<offset>]', token)
                token = re.sub(r'(?P<offset>\d+)\[(?P<var>\w+)\]', '[\g<var>+\g<offset>]', token)
                tokens[j] = token

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
        outputString += lines[i] + "\n"

    return outputString





##########    #####               ###     ##########  ##########  
    ##      ##     ##            ## ##        ##          ##      
    ##      ##     ##           ##   ##       ##          ##      
    ##      ##     ##          ##     ##      ##          ##      
    ##      ##     ##          #########      ##          ##      
    ##      ##     ##          ##     ##      ##          ##      
    ##        #####    ####### ##     ##      ##          ##   

def toATT(inputString):

    commentBlock = False
    tab = 0 # Number of tabulations at line beginning
    isLabel = False
    clobbersCount = 0
    clobberLine = 0
    variables = dict()
    label = ""
    index = ""
    regUsed = Set() # Set of registers used.
    varUsed = Set() # Set of variables used.
    labelUsed = Set() # Set of labels.
    outputString = ""

    # print inputString
    # with open("testfile.x86", "r") as f:
    #     inputString = f.read()

    # First, split the input string in lines
    lines = inputString.splitlines()


    for i in range(len(lines)):
        line = lines[i]
        line = line.strip()
        isLabel = False

        # Comment block detection
        if len(line) > 1 and line[0] + line[1] == "/*":
            commentBlock = True

        if not commentBlock:

            if "emms;" in line:
                line = "\n"

            line = re.sub(r';', '\\\\n"', line)

            line = re.sub(r'__asm', '__asm__', line)
            if re.match('\{', line):
                tab += 1
                line = re.sub(r'\{', '(', line)
            if re.match('\}', line):
                tab -= 1
                line = re.sub(r'\}', ');', line)


            # Those should only be applied on instructions parameters to void facking up any hypothetical comment.
            # line = re.sub(r'\$(?P<imm>\d+)', '\g<imm>', line)
            line = re.sub(r'\[(?P<var>[\w+\-]+)\]', '(\g<var>)', line)

            tokens = re.split('\s+', line)

            # Translate the offset
            for j in range(len(tokens)):
                token = tokens[j]
                token = re.sub(r'\((?P<var>[\w]+)(?P<offset>\-\d+)\)', '\g<offset>(\g<var>)', token)
                token = re.sub(r'\((?P<var>[\w]+)\+(?P<offset>\d+)\)', '\g<offset>(\g<var>)', token)
                tokens[j] = token

            # If two parameters are glued together with a comma, split them.
            if len(tokens) > 1 and re.search(',.+', tokens[1]):
                subtokens = tokens[1].split(',')
                tokens[1] = subtokens[0]
                tokens.insert(2, subtokens[1])

            # If a comment is glued to the argument, space it.
            for j in range(len(tokens)):
                token = tokens[j]
                match = re.search('^.+((\/\/)|(\/\*))', token)
                if match:
                    # I assume there are only one match, hence two subtokens.
                    subtokens = token.split(match.group(1))
                    tokens[j] = subtokens[0]
                    tokens[j+1] = match.group(1) + subtokens[1]


            # If there are two arguments and the second one is not a comment, swap them.
            # Plus, register any variable of used register.
            if len(tokens) > 2 and not re.search('^\/\/|^\/\*', tokens[2]):
                tmp = tokens[1]
                tokens[1] = re.sub(r'\\n"', ',', tokens[2])
                tokens[2] = re.sub(r'(?P<arg>.*),$', '\g<arg>', tmp) + '\\n"'
                # Detect registers
                for pattern in registers:
                    for j, token in enumerate(tokens[1:3]):
                        match = re.search(pattern, token)
                        if match:
                            regUsed.add(match.group(0))
                        # Prepend '%%' to registers
                        superpattern = '(?P<reg>' + pattern + ')'
                        tokens[1+j] = re.sub(superpattern, '%%\g<reg>', token)
                # Detect variables
                for j, token in enumerate(tokens[1:3]):
                    match = re.search('([a-zA-Z]\w*)((\\\\n")|,)$', token)
                    if match:
                        varUsed.add(match.group(1))
                    match = re.search('\(([a-zA-Z]\w*)\)', token)
                    if match:
                        varUsed.add(match.group(1))
                    # 'var' becomes '%[var]'
                    if "%%" not in token:
                        tokens[1+j] = re.sub(r'(?P<var>[a-zA-Z]\w*)', '%[\g<var>]', token)
                # Convert constants
                for j, token in enumerate(tokens[1:3]):
                    tokens[1+j] = re.sub(r'^(?P<const>\d+)(?P<n>,|\\)', '$\g<const>\g<n>', token)


            # Detect label
            if re.search(':$', tokens[0]):
                isLabel = True
                match = re.search('(?P<label>\w+):$', tokens[0])
                if match:
                    labelUsed.add(match.group(1))
                tokens[0] += "\\n\""

            # Merge tokens back
            line = ' '.join(tokens)

            # If normal instruction line, prepend a double quote.
            if not re.search('^((__asm__)|(\()|(\)))', line) and line.strip() != "":
                line = '"' + line

        # End of comment block detection
        if "*/" in line:
            commentBlock = False

        # Highlight the label by shifting them to the left.
        if isLabel:
            tab -= 1
        lines[i] = "\t"*tab + line
        if isLabel:
            tab += 1

        


    # Second pass: create the clobbers.
    # Find the index of the line with ");" and do everything right before it.
    for i in range(len(lines)):
        line = lines[i]
        if ");" in line:
            varUsed = varUsed.difference(regUsed)
            varUsed = varUsed.difference(labelUsed)

            # Third clobber line
            clobLine = ":"
            for reg in regUsed:
                clobLine += '"%%' + reg + '", '
            clobLine = re.sub(r', $', '', clobLine)
            lines.insert(i-1, clobLine)

            # Second clobber line
            clobLine = ":"
            for var in varUsed:
                clobLine += '[' + var + ']"m" (' + var + '), '
            clobLine = re.sub(r', $', '', clobLine)
            lines.insert(i-1, clobLine)

            # First clobber line
            clobLine = ": // Outputs, please populate."
            lines.insert(i-1, clobLine)

    for line in lines:
        outputString += line + "\n"



    return outputString





 #######   ##     ##  ########   
##         ##     ##     ##      
##         ##     ##     ##      
##   ####  ##     ##     ##      
##     ##  ##     ##     ##      
##     ##  ##     ##     ##      
########    #######   ########

def callback(event):
    webbrowser.open_new(r"https://github.com/parastuffs/AT-T_Intelx86_converter/issues")

class Gui(tk.Frame):

    def __init__(self, top, **kwargs):
        tk.Frame.__init__(self, top, **kwargs)
        self.pack()

        # Paned window
        self.p = tk.PanedWindow(self, orient=tk.VERTICAL)

        # Radio buttons
        self.fRadioButtons = tk.LabelFrame(self.p, width=500, text="Choose the conversion")
        self.fRadioButtons.pack(fill=tk.X)

        self.prb = tk.PanedWindow(self.fRadioButtons, orient=tk.HORIZONTAL)

        self.convChoice = tk.StringVar()
        self.rbToATT = tk.Radiobutton(self.prb, text="Intel x86 -> AT&T", variable=self.convChoice, value="toATT")
        self.rbToIntel = tk.Radiobutton(self.prb, text="AT&T -> Intel x86", variable=self.convChoice, value="toIntel")
        self.rbToATT.pack()
        self.rbToIntel.pack()

        self.prb.add(self.rbToATT)
        self.prb.add(self.rbToIntel)
        self.prb.pack()

        self.p.add(self.fRadioButtons)

        # Input text frame
        self.fInput = tk.Frame(self.p)
        self.p.add(self.fInput)

        # Scrollbar
        self.scrollbarIn = tk.Scrollbar(self.fInput)
        self.scrollbarIn.pack(side=tk.RIGHT, fill=tk.Y)

        # Input text box
        self.tInput = tk.Text(self.fInput, yscrollcommand=self.scrollbarIn.set)
        self.tInput.pack()

        # Output text frame
        self.fOutput = tk.Frame(self.p)
        self.p.add(self.fOutput)

        # Scrollbar
        self.scrollbarOut = tk.Scrollbar(self.fOutput)
        self.scrollbarOut.pack(side=tk.RIGHT, fill=tk.Y)

        # Input text box
        self.tOutput = tk.Text(self.fOutput, yscrollcommand=self.scrollbarOut.set)
        self.tOutput.pack()

        # # Buttons panel
        # self.pb = tk.PanedWindow(self.p, orient=tk.HORIZONTAL)
        # # Conversion button
        # self.bConvert = tk.Button(self.pb, text="Convert", command=self.convert)
        # self.pb.add(self.bConvert)
        # self.bCopy = tk.Button(self.pb, text="Copy to clipboard", command=self.copyCB)
        # self.pb.add(self.bCopy)
        # self.p.add(self.pb)

        # Conversion button
        self.bConvert = tk.Button(self.p, text="Convert", command=self.convert)
        self.p.add(self.bConvert)


        # Issue hyperlink
        self.link = tk.Label(self.p, text="Not what you expected? File an issue on Github.", fg="blue", cursor="hand2")
        self.link.pack()
        self.link.bind("<Button-1>", callback)
        self.p.add(self.link)


        self.p.pack(fill=tk.X)


    def convert(self):
        inputString = self.tInput.get("1.0",'end-1c')
        outputString = ""
        # print inputString
        convType = self.convChoice.get()
        if convType == "":
            # Raise an alert
            pass
        elif convType == "toATT":
            outputString = toATT(inputString)
        elif convType == "toIntel":
            outputString = toIntel(inputString)

        self.tOutput.delete("1.0", tk.END)
        # print outputString
        self.tOutput.insert("1.0", outputString)

    def copyCB(self):
        outputStr = self.tInput.get("1.0",'end-1c')
        pyperclip.copy(outputStr)









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
    else:
        window = tk.Tk()
        window.title("Assembly converter")
        imgicon = tk.PhotoImage(file='app.gif')
        window.tk.call('wm', 'iconphoto', window._w, imgicon)  
        gui = Gui(window)

        gui.mainloop()