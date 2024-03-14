import collections
from dataclasses import dataclass
from collections    import deque
from typing         import Union

EPSILON = '&'

# Begin Solution from Prof. Chiang
class Transition(object):
    def __init__(self, q, a, r):
        self.q = q
        self.a = a
        self.r = r

class NFA(object):
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.start = None
        self.accept = set()
        self.transitions = {}

    def add_state(self, q):
        self.states.add(q)

    def add_symbol(self, a):
        self.alphabet.add(a)
        
    def set_start(self, q):
        self.add_state(q)
        self.start = q

    def add_accept(self, q): 
        self.add_state(q)
        self.accept.add(q)

    def add_transition(self, t):
        self.add_state(t.q)
        if t.a != EPSILON:
            self.add_symbol(t.a)
        self.add_state(t.r)
        self.transitions.setdefault(t.q, {}).setdefault(t.a, []).append(t)

def read(file):
    """Read a NFA from a file."""
    m = NFA()
    for q in next(file).split():
        m.add_state(q)
    for a in next(file).split():
        m.add_symbol(a)
    m.set_start(next(file).rstrip())
    for q in next(file).split():
        m.add_accept(q)
    for line in file:
        q, a, r = line.split()
        m.add_transition(Transition(q, a, r))
    return m

def write(m, file):
    """Write a NFA to a file."""
    file.write(' '.join(map(str, m.states)) + '\n')
    file.write(' '.join(map(str, m.alphabet)) + '\n')
    file.write(str(m.start) + '\n')
    file.write(' '.join(map(str, m.accept)) + '\n')
    for q in m.transitions:
        for a in m.transitions[q]:
            for t in m.transitions[q][a]:
                file.write("{} {} {}\n".format(t.q, t.a, t.r))

def _transitions(m, w, q, i):
    """Helper function for match_dfs and match_bfs.

    If NFA m is in state q and reading string w at position i,
    iterates over possible transitions and new positions."""
    
    for t in m.transitions.get(q, {}).get(EPSILON, []):
        yield t, i
    if i < len(w):
        for t in m.transitions.get(q, {}).get(w[i], []):
            yield t, i+1

def match(m, w):
    """Test whether a NFA accepts a string, using a breadth-first search.

    m: NFA
    w: list of symbols
    Returns: 
      - if m accepts w, then (True, path), where path is a list of Transitions
      - otherwise, (False, None)
    """

    if m.start in m.accept and len(w) == 0:
        return True, []
    start = (m.start, 0)
    frontier = collections.deque([start]) # Queue of configurations to explore
    visited = {} # Mapping from each visited configuration to one of its incoming transitions

    while len(frontier) > 0:
        q, i = frontier.popleft()
        for t, j in _transitions(m, w, q, i):
            # Don't allow duplicates in frontier.
            # If we do this later, it will be exponential.
            if (t.r, j) in visited: continue
            visited[t.r, j] = t
            if t.r in m.accept and j == len(w):
                # Reconstruct the path in reverse
                path = []
                r = t.r
                while (r, j) != start:
                    t = visited[r, j]
                    path.append(t)
                    r = t.q
                    if t.a != EPSILON: j -= 1
                path.reverse()
                return True, path
            frontier.append((t.r, j))
    return False, None

# End solution from Prof. Chiang

def uniq(oldNFA, shift) -> NFA:
    #shift is how much each state should be moved by so that there is no state overlap
    newNFA = NFA()
    for dictState in oldNFA.transitions.values():
        for listT in dictState.values():
            for t in listT:
                newNFA.add_transition(Transition(t.q+shift, t.a, shift + t.r))
    for a in oldNFA.accept:
        newNFA.add_accept(shift + a)
    newNFA.set_start(shift + oldNFA.start)
    return newNFA

def convert(oldNFA) -> NFA:
    newNFA = NFA()
    flip = {}
    for index, state in enumerate(sorted(oldNFA.states), 1):
        flip[state] = index
        newNFA.states.add(index)
    for dictState in oldNFA.transitions.values():
        for listT in dictState.values():
            for t in listT:
                newNFA.add_transition(Transition(flip[t.q], t.a, flip[t.r]))
    newNFA.start = flip[oldNFA.start]
    for a in oldNFA.accept:
        newNFA.add_accept(flip[a])

    return newNFA

def concat_nfa(one, two) -> NFA:
    '''
    Concatinates two NFA's
    '''
    one = convert(one)
    two = convert(two)
    three = NFA()
    three.alphabet = one.alphabet.copy()
    three.alphabet.update(two.alphabet)
    one = uniq(one, -1)
    two = uniq(two, len(one.states) - 1)
    three.set_start(0)
    total = len(one.states) + len(two.states)
    for i in range(total):
        three.add_state(i)

    #three.add_transition(nfa.Transition(three.start, '&', one.start))
    three.transitions = one.transitions
    for a in one.accept:
        three.add_transition(Transition(a, '&', two.start))
    three.transitions.update(two.transitions)
    for a in two.accept:
        three.add_accept(a)
    return three


###############################
###### parse re->NFA ##########
###############################
@dataclass
class symbol:
    '''symbol() referenced in docs'''
    symbol: str

    def __str__(self) -> str:
        return f'symbol("{self.symbol}")'

@dataclass
class concat:
    '''concat(a,b) referenced in docs'''

    left:    Union[symbol, 'concat']
    right:   Union[symbol, 'concat']
    def __str__(self) -> str:
        return f'concat({self.left},{self.right})'

@dataclass
class epsilon:
    '''epsilon() referenced in docs'''
    def __str__(self):
        return 'epsilon()'

@dataclass
class union:
    '''The union(a,b) function implemented as node with left, right children'''
    left:   Union['union', symbol, concat, epsilon]
    right:  Union['union', symbol, concat, epsilon]

    def __str__(self) -> str:
        return f'union({self.left},{self.right})' # Used to correctly output the parsed regex


@dataclass
class star:
    child:  Union['union', symbol, concat, epsilon]

    def __str__(self) -> str:
        return f'star({self.child})'


@dataclass
class nt: 
    '''
    Non-Terminal
    '''
    value:  str
    tree:   Union[NFA, union, symbol, concat, epsilon ]
    def __str__(self) -> str:
        '''Makes it easy to compare values'''
        return self.value

    def __eq__(self, other: object) -> bool:
        '''Makes it easy to compare values'''
        if (type(other) is str):
            return self.value == other 
        else:
            return self == other


def nexti(input: deque, vals: set, i=0):
    '''Check if next `input` is in `vals` referenced in docs.'''
    return (input[i] in vals) if len(input) >= i+1 else False 

def below(stack: list[str|nt], vals:set, i: int=2):
    '''Check "below" referenced in docs. Ultimately a poor patchjob, should fix'''
    return (str(stack[-i]) in vals) if len(stack) >= i else True

def stack_is(stack, str):
    '''Get current stack item in question'''
    return stack[-1] == str

def curr(input: deque, string: str):
    '''Check if current consumable input == string'''
    return input[0] == string

def flattenc(stack: deque, st: str):
    '''Checks multiple next stack items against string for string length'''
    if len(stack) >= len(st):
        return ''.join([str(s) for s in stack[-len(st):]]) == st
    else:
        return False

def re_to_nfa(regex: str, stack: list[str|nt]=['$']) -> NFA:
    '''Builds an NFA from a regular expression
    regex: Regular Expression
    stack: A multi-type list that can contain different dataclasses or strings in order to implement the PDA. Default value is ['$']

    Output: an NFA

    This is overall a lengthy and poor implementation of the PDA in code, although it works now that I fully understand it I would do it differently in the future.
    '''

    input: deque = deque([c for c in regex])
    below_a: set = {'$', '(', '|', 'T'}

    input.append('⊣')
    flag = False    

    while(not flag):
        if (not (str(input[0]) if len(input) > 0 else '|') in {'|', '(', ')', '*', '⊣', '\\'} and below(stack, below_a, 1)): # case a
            stack.append(input[0])
            input.popleft()

        elif (curr(input, '(') and below(stack, below_a, 1)):
            stack.append('(')
            input.popleft()
            
        elif (curr(input, ')') and below(stack, {'E'}, 1)):
            stack.append(')')
            input.popleft()
            
        elif (curr(input, '|') and below(stack, {'E'}, 1)):
            stack.append('|')
            input.popleft()
            
        elif (curr(input, '*') and below(stack, {'P'}, 1)):
            stack.append('*')
            input.popleft()

        elif (flattenc(stack, 'E|M')):
            m: nt = stack.pop() 
            stack.pop()
            e: nt = stack.pop()

            push: nt = nt('E', union_nfa(e.tree, m.tree))
            stack.append(push)

        elif (flattenc(stack, 'M') and below(stack, {'$', '('})):
            m: nt = stack.pop()

            push: nt = nt('E', m.tree)
            stack.append(push)

        elif (below(stack, {'$', '(', '|'}, 1) and nexti(input, {'|', ')', '⊣'})):
            push: nt = nt('M', string_nfa(''))
            stack.append(push)

        elif (stack_is(stack, 'T') and nexti(input, {'|', ')', '⊣'})):
            t: nt = stack.pop()

            push: nt = nt('M', t.tree)
            stack.append(push)

        elif (flattenc(stack, 'TF')):
            f: nt = stack.pop()
            t: nt = stack.pop()

            push: nt = nt('T', concat_nfa(t.tree, f.tree))
            stack.append(push)

        elif (stack_is(stack, 'F') and below(stack, {'$', '(', '|'})):
            f: nt = stack.pop()
            
            push: nt = nt('T', f.tree)
            stack.append(push)
            
        elif (flattenc(stack, 'P*')):
            stack.pop()
            p: nt = stack.pop()
            
            push: nt = nt('F', star_nfa(p.tree))
            stack.append(push)
        
        elif (stack_is(stack, 'P') and not nexti(input, {'*'}, 0)):
            p: nt = stack.pop()

            push: nt = nt('F', p.tree)
            stack.append(push)

        elif (not str(stack[-1]) in {'|', '(', ')', '*', '⊣', '\\'} and not type(stack[-1]) is nt):
            a: str = stack.pop()

            push: nt = nt('P', string_nfa(a))
            stack.append(push)

        elif (flattenc(stack, '(E)')):
            stack.pop()
            e: nt = stack.pop()
            stack.pop()
            
            push: nt = nt('P', e.tree)
            stack.append(push)
        else:
            try:
                if stack[1].value == 'E':
                    flag = True
            except:
                continue
    
    sNFA: NFA = stack[1].tree
    return sNFA

def string_nfa(w) -> NFA:
    '''Creates an NFA that accepts exactly one string, w

    w: a string (possibly empty)
    Output: an NFA recognizing the language {w}
    '''
    word_nfa = NFA()
    length = len(w)
    for i in range(length):
        word_nfa.add_state(i)
        word_nfa.add_symbol(w[i])
        transition = Transition(i, w[i], i+1)
        word_nfa.add_transition(transition)
    word_nfa.set_start(0)
    word_nfa.add_accept(length)
    
    word_nfa.states = sorted(word_nfa.states)
    word_nfa.alphabet = sorted(word_nfa.alphabet)
    
    return word_nfa

def union_nfa(one: NFA, two: NFA) -> NFA:
    '''
    one: NFA
    two: NFA

    Output: NFA recognizing the language of union of one and two
    '''
    one = convert(one)
    two = convert(two)
    #new union NFA call it three
    three = NFA()
    #find new alphabet
    three.alphabet = one.alphabet.copy()
    three.alphabet.update(two.alphabet)
    #find new number of states
    total = 1 + len(one.states) + len(two.states)
    for i in range(total):
        three.add_state(i)
    #shift all the states and transitions of one and two based on position
    one = uniq(one, 0)
    two = uniq(two, len(one.states))
    #put a start state to the old start states
    three.set_start(0)
    three.add_transition(Transition(three.start, '&', one.start))
    three.add_transition(Transition(three.start, '&', two.start))
    three.transitions = three.transitions | one.transitions | two.transitions
    #keep the accept states
    for a in one.accept:
        three.add_accept(a)
    for a in two.accept:
        three.add_accept(a)
    return three

def star_nfa(one) -> NFA:
    '''
    one: NFA
    Output: NFA recognizing L(one)*
    '''
    one = convert(one)
    one.add_transition(Transition(0, '&', one.start))

    for a in one.accept:
        one.add_transition(Transition(a, '&', one.start))
    one.add_accept(0)
    one.set_start(0)

    return one