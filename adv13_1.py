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
        print('input: {}'.format(inputval))
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


"""
intcomputer = {'prog': mem.copy(), 'inputs': QueueInputSource([]), 'outputs': [], 'next_amp': None, 'pc': 0, 'relbase': 0}

signals_to_intcomputer(intcomputer, [2])

(intcomputer['pc'], intcomputer['relbase']) = execute_until_output(intcomputer['prog'], intcomputer['pc'], intcomputer['inputs'], intcomputer['outputs'], intcomputer['relbase'])
# get last output
output = intcomputer['outputs'][len(intcomputer['outputs']) - 1]
print(output)

"""



# constants
up=0
left=1
down=2
right=3
ccw = 0
cw = 1
black = 0
white = 1

tile_block = 2
    
class PanelGrid():
    def __init__(self):
        self.paneldict = {}
        self.robot_pos = (0, 0)
        self.orientation = up
        self.maxx = 0
        self.maxy = 0

    def rotate_robot(self, rot_direction):
        rotation = 1 if rot_direction == ccw else -1
        self.orientation += rotation
        if self.orientation < up:
            self.orientation = right
        if self.orientation > right:
            self.orientation = up

    def set_color_at(self, color, pos):
        print("painting {} {}".format(str(pos), color))
        self.paneldict[str(pos)] = color
        (x, y) = pos 
        if x > self.maxx:
            self.maxx = x
        if y > self.maxy:
            self.maxy = y

    def set_color_at_current_panel(self, color):
        #print("painting {} {}".format(str(self.robot_pos), color))
        self.set_color_at(color, self.robot_pos)

    def get_color_at(self, pos):
        if str(pos) in self.paneldict:
            return self.paneldict[str(pos)]
        return black

    def get_color_at_current_panel(self):
        return self.get_color_at(self.robot_pos)
        #if str(self.robot_pos) in self.paneldict:
        #    return self.paneldict[str(self.robot_pos)]
        #return black

    def move_robot(self, dx, dy):
        self.robot_pos = (self.robot_pos[0] + dx, self.robot_pos[1] + dy)

    def move_robot_forward(self):
        dx = 0
        dy = 0
        if self.orientation == up:
            dy = 1
        elif self.orientation == left:
            dx = -1
        elif self.orientation == down:
            dy = -1
        elif self.orientation == right:
            dx = 1
        self.move_robot(dx, dy)

    def paint_panel(self, color):
        self.set_color_at_current_panel(color)
    
    def make_move(self, rot_direction):
        self.rotate_robot(rot_direction)
        self.move_robot_forward()
    
    def get_nof_painted_panels(self):
        return len(self.paneldict)

    def get_maxx(self):
        return self.maxx

    def get_maxy(self):
        return self.maxy

    def get_nof_grids_of_type(self, tiletype):
        print(self.paneldict.values())
        tiles_of_type = [candidate_type for candidate_type in self.paneldict.values() if candidate_type == tiletype]
        return len(tiles_of_type)

thegrid = PanelGrid()
#thegrid.paint_panel(1)

intcomputer = {'prog': mem.copy(), 'outputs': [], 'next_amp': None, 'pc': 0, 'relbase': 0}
outputs_buffer = []

while intcomputer['pc'] >= 0:
    intcomputer['inputs'] = ConstInputSource(thegrid.get_color_at_current_panel())
    (intcomputer['pc'], intcomputer['relbase']) = execute_until_output(intcomputer['prog'], intcomputer['pc'], intcomputer['inputs'], intcomputer['outputs'], intcomputer['relbase'])
    outputs_buffer.extend(intcomputer['outputs'])
    del intcomputer['outputs'][:]
    if len(outputs_buffer) == 3:
        x = outputs_buffer.pop(0)
        y = outputs_buffer.pop(0)
        tiletype = outputs_buffer.pop(0)
        thegrid.set_color_at(tiletype, (x, y))
    """
    if len(intcomputer['outputs']) == 3:
        x = intcomputer['outputs'].pop()
        y = intcomputer['outputs'].pop()
        tiletype = intcomputer['outputs'].pop()
        thegrid.set_color_at(tiletype, (x, y))
    """

    """
    outputs_buffer.extend(intcomputer['outputs'])
    del intcomputer['outputs'][:]
    if len(outputs_buffer) == 2:
        new_color = outputs_buffer.pop()
        turn_direction = outputs_buffer.pop()
        thegrid.paint_panel(new_color, turn_direction)
    """

"""
thegrid.paint_panel(1, 0)
thegrid.paint_panel(0, 0)
thegrid.paint_panel(1, 0)
thegrid.paint_panel(1, 0)
thegrid.paint_panel(0, 1)
thegrid.paint_panel(1, 0)
thegrid.paint_panel(1, 0)
"""


#print(thegrid.get_nof_painted_panels())

print(thegrid.get_maxy())
print(thegrid.get_maxx())

for y in range(0, thegrid.get_maxy()):
    line = ""
    for x in range(0, thegrid.get_maxx()):
        colchar = "¤" if thegrid.get_color_at((x, y)) == white else " "
        line += colchar
    print(line)

nof_block_tiles = thegrid.get_nof_grids_of_type(tile_block)
print(nof_block_tiles)


"""
Problem:
The second program instruction (1008,2751,248387,381) does not seems to be right. It writes 0 at address 381. Should probably be 1.
Changing that instruction to 1108 (as in 1108,2751,248387,381) makes the program run.


"""
