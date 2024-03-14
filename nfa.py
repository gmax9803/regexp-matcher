#!/usr/bin/env python3

import sys

class NFA:
    def __init__(self):
        self.states:    list = []
        self.alphabet:  list = ['&'] 
        self.start:     str  = ''
        self.accepts:   list = []
        self.transitions: dict(dict(list(str))) = {}

    def read_nfa(self, name):
        f = open(name, 'r')
        lines = f.readlines()
        for line in lines:
            line = line.strip()
        for state in lines[0].split():
            self.states.append(state)
        for letter in lines[1].split():
            self.alphabet.append(letter)
        self.start = lines[2].strip()
        for state in lines[3].split():
            self.accepts.append(state)
        for state in self.states:
            self.transitions[state] = {}
            for letter in self.alphabet:
                self.transitions[state][letter] = []
        for t in lines[4:]:
            t = t.strip().split()
            origin      = t[0]
            char: str   = t[1]
            destination = t[2]
            self.transitions[origin][char].append(destination)
        '''
        print(f"States: {self.states}")
        print(f"Alpha:  {self.alphabet}")
        print(f"Start:  {self.start}")
        print(f"Accepts: {self.accepts}")
        '''
        #print(f"Transitions: {self.transitions}")

    def write_nfa(self, name):
        f = open(name, 'w')
        f.write((' ').join(self.states) + '\n')
        f.write((' ').join(self.alphabet) + '\n')
        f.write(self.start + '\n')
        f.write((' ').join(self.accepts) + '\n')
        for state in self.transitions:
            for char in self.transitions[state]:
                for dest in self.transitions[state][char]:
                    f.write(f"{state} {char} {dest}\n")
    

    def match_nfa(self, w: str):
       #frontier layout                         = [(depthNo&, totalPath, state, transitionsOutOfState, statePath, transitionPath)]
        frontier: list(tuple(int, str, str, list(str), list, list)) = [(0, '', self.start, self.transitions[self.start], [self.start], [])]
        #print('original')
        #print(frontier)
        while frontier:
            curr = frontier.pop()
            maxChar = False
            #print('this is curr')
            #print(curr)
            #print(type(curr))
            if curr[1] == w:
                if curr[2] in self.accepts: 
                    print('Success!')
                    print(w)
                    print(curr[1])
                    print(curr)
                    return True
            for transitions in self.alphabet:                   #look at each char in the alphabet as transitions
                #print(f'this is curr {curr}')
                #print(f'this is curr[1] {curr[1]}')
                #for i in curr:
                #    print(i)
                #fork = self.transitions[curr[2]][transitions]   #find where taking each transition could possibly lead, the forks in the road
                #if not fork: 
                #    print(f'{transitions} transition DNE')
                #    continue                                    #if the transition has no path, ignore it and move on to next transition
                for dest in self.transitions[curr[2]][transitions]:  #look at each transition's possible destinations
                    #print(f'{transitions} transition can lead to {dest} state')
                    charLimit = False
                    if curr[0] == len(w):                        #if the string is too long, DO NOT add to frontier
                        charLimit = True
                    if not charLimit and transitions == w[curr[0]]: #check if the transition should be taken by looking at string input
                        #print(f'printing valid paths for transition: {transitions}')
                        front = (curr[0]+1, curr[1]+transitions, dest, self.transitions[dest], curr[4]+[dest], curr[5]+[transitions])
                        print(front)
                        frontier.append(front)
                        #print(frontier[-1])
                        #print(f'{curr[1] + transitions} | {curr[4]+[dest]} | {curr[5] + [transitions]}')
                        #print('adding to frontier')
                        #print(frontier)
                    if transitions == '&':
                        statePath       = curr[4] + [dest]
                        transitionPath  = curr[5] + [transitions]
                        cycle = False   #innocent until proven guilty
                        backwardsCount  = 1
                        visited         = set()    #these are the states visited
                        #print('entering while loop')
                        while not cycle and len(transitionPath) > backwardsCount and transitionPath[-backwardsCount] == '&':
                            #print('looping')
                            if statePath[-backwardsCount] not in visited:
                                visited.add(statePath[-backwardsCount])
                                #print(visited)
                                backwardsCount += 1
                            else:
                                #print(visited)
                                #print(f'repeat {statePath[-backwardsCount]}')
                                cycle = True
                        if not cycle:
                            front = (curr[0], curr[1], dest, self.transitions[dest], curr[4]+[dest], curr[5]+[transitions])
                            print(front)
                            frontier.append(front)
                    '''
                # save: or w[curr[0]] != transitions:
                    else:
                        #implement backtracing
                        #backtrace passed: proceed
                        investigation = [([curr[0], curr[1], state, self.transitions[state]], curr[2] + [state[, curr[1] + [transitions])]
                        i = -1
                        visited = []
                        while investigation[5][i] == '&':
                             visited += 
                        #backtrace passed: proceed
                        #if fail: pop the back to undo mistake
                '''

        print('Failure')
        print(w)
        print(curr[1])
        return False

        #queue = [(depth, prev depth, [origin, transitions, curr])]
        #make an epsilon loop tracker that follows epsilon transitions
        #go backwards to find epsilon loops
        

def main(stream=sys.stdin):
    nfa = NFA()
    nfa.read_nfa(sys.argv[1])
    nfa.write_nfa(sys.argv[2])
    nfa.match_nfa(sys.argv[3])


if __name__ == '__main__':
    main()
    
