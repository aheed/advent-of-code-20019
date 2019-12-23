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

def _process(mem, pos, inputs, outputs, relbase):
    opcode = mem[pos]

    jump = False

    nof_params = get_nof_params(opcode)
    (op, opmodes) = get_op(mem, pos, nof_params)
    params = get_parameters(mem, pos + 1, opmodes, relbase)
    
    if op == 1:
        respos = get_addr_from_param(params[2])
        set_autoexpand(mem, respos, get_val_from_param(params[0]) + get_val_from_param(params[1]))
    if op == 2:
        respos = get_addr_from_param(params[2])
        set_autoexpand(mem, respos, get_val_from_param(params[0]) * get_val_from_param(params[1]))
    if op == 3:
        respos = get_addr_from_param(params[0])
        inputval = inputs.get_next()
        set_autoexpand(mem, respos, inputval)
    if op == 4:
        output = get_val_from_param(params[0])
        outputs.append(output)
    if op == 5:
        if get_val_from_param(params[0]) != 0:
            pos = get_val_from_param(params[1])
            jump = True
    if op == 6:
        if get_val_from_param(params[0]) == 0:
            pos = get_val_from_param(params[1])
            jump = True
    if op == 7:
        respos = get_addr_from_param(params[2])
        set_autoexpand(mem, respos, 1 if get_val_from_param(params[0]) < get_val_from_param(params[1]) else 0)
    if op == 8:
        respos = get_addr_from_param(params[2])
        p1 = get_val_from_param(params[0])
        p2 = get_val_from_param(params[1])
        set_autoexpand(mem, respos, 1 if p1 == p2 else 0)
    if op == 9:
        relbase += get_val_from_param(params[0])
    if op == 99:
        pos = -1
        jump = True

    if not jump:
        pos = pos + 1 + nof_params

    return (pos, relbase)


################################################
class IntcodeComputer():
    def __init__(self, prog=[], input_source=None):
        self.prog = prog.copy()
        self.input_source = input_source
        self.pc = 0
        self.relbase = 0
        self.outputs = []
    
    def process(self):
        assert self.is_running()
        (self.pc, self.relbase) = _process(self.prog, self.pc, self.input_source, self.outputs, self.relbase)

    def execute(self):
        self.pc = 0
        while self.is_running():
            self.process()

    def execute_until_output(self):
        while self.pc >=0 and len(self.outputs) == 0:
            self.process()

    def is_running(self):
        return self.pc >= 0

################################################################
################################################################

class QueueInputSource():
    def __init__(self, inputs, default_val):
        self.inputs = []
        self.add_inputs(inputs)
        self.default_val = default_val

    def add_inputs(self, inputs):
        self.inputs.extend(inputs)
    
    def get_next(self):
        if len(self.inputs):
            return self.inputs.pop(0)
        else:
            return self.default_val

class ConstInputSource():
    def __init__(self, val):
        self.val = val
    
    def get_next(self):
        return self.val


###############################

nof_nodes = 50
#nof_nodes = 1 #TEMP

computers = []
for index in range(nof_nodes):
    computers.append(IntcodeComputer(mem, QueueInputSource([index], -1)))

cmp_index = 0
while True:
    cmp = computers[cmp_index]
    cmp.process()

    if len(cmp.outputs) == 3:
        packet_dest = cmp.outputs.pop(0)
        packet_x = cmp.outputs.pop(0)
        packet_y = cmp.outputs.pop(0)
        if packet_dest == 255:
            result = packet_y
            break
        else:
            dest_cmp = computers[packet_dest]
            dest_cmp.input_source.add_inputs([packet_x, packet_y])

    cmp_index += 1
    if cmp_index >= nof_nodes:
        cmp_index = 0


print(result)
