#!/usr/bin/env python3
import nfa

if __name__ == "__main__":
    import argparse
    import fileinput
    import sys
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument('nfafile', metavar='nfafile', help='file containing NFA')
    argparser.add_argument('input', metavar='string', help='string to run NFA on')
    args = argparser.parse_args()

    m = nfa.read(open(args.nfafile))
    flag, path = nfa.match(m, args.input)
    if flag:
        print("accept")
        for t in path:
            print(t.q, t.a, t.r)
    else:
        print("reject")

