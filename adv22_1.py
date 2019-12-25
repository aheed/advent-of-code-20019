import sys
from enum import Enum

if len(sys.argv) <= 1:
    print("opening stdin")
    inputfile = sys.stdin
else:
    print("opening input file {}".format(sys.argv[1]))
    inputfile = open(sys.argv[1], "r")


class ShuffleEnum(Enum):
    DEAL_WITH = 1
    CUT = 2
    DEAL_INTO_NEW = 3

class ShuffleOp():
    def __init__(self, shuffle_enum, arg):
        self.shuffle_enum = shuffle_enum
        self.arg = arg
    def dump(self):
        print("op:{} arg:{}".format(self.shuffle_enum, self.arg))

def get_number(candidate):
    res = None
    try:
        res = int(candidate)
    except ValueError:
        pass
    return res

def get_index(line):
    cand_word = line.split()[-1]
    return get_number(cand_word)

def create_shuffle_op(line):
    if "deal with increment" in line:
        sh_enum = ShuffleEnum.DEAL_WITH
        arg = get_index(line)
    elif "cut" in line:
        sh_enum = ShuffleEnum.CUT
        arg = get_index(line)
    else:
        assert "deal into new stack" in line
        sh_enum = ShuffleEnum.DEAL_INTO_NEW
        arg = None
    return ShuffleOp(sh_enum, arg)

shuffle_ops = [create_shuffle_op(line) for line in inputfile]

#for op in shuffle_ops:
#    op.dump()

############################################
nof_cards = 10007

############################################
def deal_with(deck, increment):
    assert len(deck) == nof_cards
    index = 0
    new_stack = [None] * nof_cards
    assert len(deck) == len(new_stack)
    for card in deck:
        new_stack[index] = card
        index = (index + increment) % nof_cards
    return new_stack

#def deal_with2(deck, increment):
#    return [deck[(i * increment) % nof_cards] for i in range(nof_cards)]

def deal_into_new(deck):
    deck.reverse()
    return deck

def cut(deck, index):
    return deck[index:] + deck[:index]

############################################

deck = list(range(nof_cards))

#print(deck)
#deck = deal_with(deck, 3)
#print(deck)
#deck = deal_into_new(deck)
#print(deck)
#deck = cut(deck, -4)
#print(deck)
#####

for op in shuffle_ops:
    #op.dump()
    if op.shuffle_enum == ShuffleEnum.CUT:
        deck = cut(deck, op.arg)
    elif op.shuffle_enum == ShuffleEnum.DEAL_INTO_NEW:
        deck = deal_into_new(deck)
    else:
        deck = deal_with(deck, op.arg)

#print(deck)
result = deck.index(2019)
print(result)
#print(deck[result])