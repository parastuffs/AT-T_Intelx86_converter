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

def toATT(inputString):




#def toIntel(inputString):




if __name__ == '__main__':

    inputString = ""
    toATT = False
    toIntel = False

    args = docopt(__doc__)
    if args["-s"]:
        inputString = args["-s"]
    if args["--to-att"]:
        toATT = True
    if args["--to-intel"]:
        toIntel = True

    if toATT and toIntel:
        print "Make up your mind."
        exit()

    if toATT:
        toATT(inputString)
    elif toIntel:
        toIntel(inputString)