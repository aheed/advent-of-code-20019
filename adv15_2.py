import sys

if len(sys.argv) <= 1:
    print("opening stdin")
    inputfile = sys.stdin
else:
    print("opening input file {}".format(sys.argv[1]))
    inputfile = open(sys.argv[1], "r")

for line in inputfile:
    #print(line)
    mem = [int(opcode) for opcode in line.split(',')]
    break

original_mem = [val for val in mem] #deep copy
#print(original_mem)

def expand_if_needed(l, index):
    if(len(l) <= index):
        for n in range(len(l), index + 1): 
            l.append(0) #pad new indexes with zeroes

def set_autoexpand(l, index, value):
    expand_if_needed(l, index)
    #print("setting {} to {}".format(index, value))
    l[index] = value

def get_autoexpand(l, index):
    expand_if_needed(l, index)
    return l[index]

def get_op(mem, pos, nof_params):
    opmodes = []
    opcode = mem[pos]
    op = opcode % 100
    opcode //= 100

    for paramindex in range(nof_params):
        opmodes.append(opcode % 10)
        opcode //= 10

    return (op, opmodes)

def get_nof_params(op):
    op = op % 100
    #print("opcode: {}".format(op))
    if op == 1:
        return 3
    if op == 2:
        return 3
    if op == 3:
        return 1
    if op == 4:
        return 1
    if op == 5:
        return 2
    if op == 6:
        return 2
    if op == 7:
        return 3
    if op == 8:
        return 3
    if op == 9:
        return 1
    if op == 99:
        return 0
    assert False

def get_parameters(mem, pos, opmodes, relbase):
    params = []
    for opmode in opmodes:
        immediate_val = get_autoexpand(mem, pos)
        if opmode == 0: # position mode
            outpos = immediate_val
            param = (outpos, get_autoexpand(mem, outpos))
        elif opmode == 1: # immediate_mode
            param = (immediate_val, immediate_val)
        elif opmode == 2: # relative mode
            outpos = relbase + immediate_val
            param = (outpos, get_autoexpand(mem, outpos))
        else:
            assert(False)
        params.append(param)
        pos += 1
    return params

def get_addr_from_param(param):
    return param[0]

def get_val_from_param(param):
    return param[1]

def process(mem, pos, inputs, outputs, relbase):
    opcode = mem[pos]

    jump = False

    nof_params = get_nof_params(opcode)
    (op, opmodes) = get_op(mem, pos, nof_params)
    params = get_parameters(mem, pos + 1, opmodes, relbase)
    
    if op == 1:
        #respos = mem[pos + 3]
        respos = get_addr_from_param(params[2])
        set_autoexpand(mem, respos, get_val_from_param(params[0]) + get_val_from_param(params[1]))
        #mem[respos] = params[0] + params[1]
        #print('1 mem[respos]:{}'.format(mem[respos]))
    if op == 2:
        #respos = mem[pos + 3]
        respos = get_addr_from_param(params[2])
        set_autoexpand(mem, respos, get_val_from_param(params[0]) * get_val_from_param(params[1]))
        #mem[respos] = params[0] * params[1]
        #print('2 mem[respos]:{}'.format(mem[respos]))
    if op == 3:
        #respos = mem[pos + 1]
        respos = get_addr_from_param(params[0])
        #set_autoexpand(mem, respos, inputs.pop(0))
        inputval = inputs.get_next()
        #print('input: {}'.format(inputval))
        set_autoexpand(mem, respos, inputval)
        #mem[respos] = inputs.pop(0)
        #print("got signal {}".format(mem[respos]))
    if op == 4:
        output = get_val_from_param(params[0])
        #output = params[0]
        #print('output: {}'.format(output))
        outputs.append(output)
    if op == 5:
        if get_val_from_param(params[0]) != 0:
            pos = get_val_from_param(params[1])
            #print(get_val_from_param(params[1]))
            #print(params)
            jump = True
            #print("jumping to: {}".format(pos))
        #if params[0] != 0:
        #    pos = params[1]
        #    jump = True
    if op == 6:
        if get_val_from_param(params[0]) == 0:
            pos = get_val_from_param(params[1])
            jump = True

        #if params[0] == 0:
        #    pos = params[1]
        #    jump = True
    if op == 7:
        respos = get_addr_from_param(params[2])
        #respos = mem[pos + 3]        
        set_autoexpand(mem, respos, 1 if get_val_from_param(params[0]) < get_val_from_param(params[1]) else 0)
        #mem[respos] = 1 if params[0] < params[1] else 0
    if op == 8:
        respos = get_addr_from_param(params[2])
        #respos = mem[pos + 3]
        p1 = get_val_from_param(params[0])
        p2 = get_val_from_param(params[1])
        set_autoexpand(mem, respos, 1 if p1 == p2 else 0)
        #set_autoexpand(mem, respos, 1 if get_val_from_param(params[0]) == get_val_from_param(params[1]) else 0)
        #mem[respos] = 1 if params[0] == params[1] else 0
    if op == 9:
        relbase += get_val_from_param(params[0])
    if op == 99:
        pos = -1
        jump = True

    if not jump:
        pos = pos + 1 + nof_params

    return (pos, relbase)

def execute(mem, inputs, outputs, relbase):
    pc = 0
    while True:
        #print('pc:{} mem[pc]:{}'.format(pc, mem[pc]))
        (pc, relbase) = process(mem, pc, inputs, outputs, relbase)
        if pc < 0:
            break

def execute_until_output(mem, pc, inputs, outputs, relbase):
    while pc >=0 and len(outputs) == 0:
        (pc, relbase) = process(mem, pc, inputs, outputs, relbase)
    return (pc, relbase)


def signals_to_intcomputer(cmp, signals):
    #cmp['inputs'].extend(signals)
    cmp['inputs'].add_inputs(signals)



################################################################
################################################################

class QueueInputSource():
    def __init__(self, inputs):
        self.inputs = []
        self.add_inputs(inputs)

    def add_inputs(self, inputs):
        self.inputs.extend(inputs)
    
    def get_next(self):
        return self.inputs.pop(0)

class ConstInputSource():
    def __init__(self, val):
        self.val = val
    
    def get_next(self):
        return self.val


##################################################

# constants
direction_to_deltas = {1: (0, 1), 2: (0, -1), 3: (-1, 0), 4: (1, 0)}
reverse_directions = {1: 2, 2: 1, 3: 4, 4: 3}
wall_tile = 0
empty_tile = 1
goal_tile = 2
max_distance = 10000

# globals
visited_tiles = {}
intcomputer = {'prog': mem.copy(), 'outputs': [], 'pc': 0, 'relbase': 0}

empty_tiles = {}
goal_tile_pos = None


def move_droid(direction):
    intcomputer['inputs'] = QueueInputSource([direction])
    (intcomputer['pc'], intcomputer['relbase']) = execute_until_output(intcomputer['prog'], intcomputer['pc'], intcomputer['inputs'], intcomputer['outputs'], intcomputer['relbase'])
    return intcomputer['outputs'].pop(0)

def move_droid_backward(direction):
    return move_droid(reverse_directions[direction])

def get_new_position(pos, deltas):
    return (pos[0] + deltas[0], pos[1] + deltas[1])

# Recursive tree search
def tree_search(distance_so_far, position):

    #print(position)
    #print(distance_so_far)

    if position in visited_tiles:
        return max_distance

    min_distance = max_distance
    visited_tiles[position] = True
    empty_tiles[position] = True

    for (direction, deltas) in direction_to_deltas.items():
        distance = max_distance

        move_result = move_droid(direction)

        if move_result == wall_tile:
            pass
        elif move_result == goal_tile:
            distance = distance_so_far + 1
            move_droid_backward(direction)
            print("found it!")
            print(distance)
            global goal_tile_pos
            goal_tile_pos = get_new_position(position, deltas)
            print("goal tile position: {}".format(goal_tile_pos))
        else:
            assert move_result == empty_tile
            distance = tree_search(distance_so_far + 1, get_new_position(position, deltas))
            move_droid_backward(direction)

        min_distance = min(min_distance, distance)

    visited_tiles.pop(position)
    return min_distance




result = tree_search(0, (0,0))
print(result)

############### Part 2 ############
unvisited_empty = empty_tiles.copy()
frontier = {goal_tile_pos: True}
tile_distances = {}
distance = 0

while len(frontier) != 0:
    new_frontier = {}
    for front_pos in frontier.keys():
        tile_distances[front_pos] = distance
        for (direction, deltas) in direction_to_deltas.items():
            new_pos = get_new_position(front_pos, deltas)
            if new_pos in unvisited_empty:
                new_frontier[new_pos] = True
                unvisited_empty.pop(new_pos)

    frontier = new_frontier
    distance += 1

distance -= 1

#print(len(empty_tiles))
#print(len(tile_distances))
print(distance)


