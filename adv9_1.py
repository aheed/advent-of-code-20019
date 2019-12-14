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
        set_autoexpand(mem, respos, inputs.pop(0))
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
        set_autoexpand(mem, respos, 1 if get_val_from_param(params[0]) == get_val_from_param(params[1]) else 0)
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

def add_perm(perms, item):
    new_perms_list = []
    for perm in perms:
        #print(perm)
        for index in range(len(perm) + 1):
            new_perm = perm.copy()
            #print(new_perm)
            new_perm.insert(index, item)
            #print(new_perm)
            new_perms_list.append(new_perm)
    return new_perms_list

def get_permutations(items):
    ret = [[items.pop(0)]]
    for item in items:
        ret = add_perm(ret, item)
    return ret



def signals_to_amp(amp, signals):
    amp['inputs'].extend(signals)

def init_amps(prog, phase_settings):
    amps = []
    last_amp = None
    for item in phase_settings:
        amp = {'prog': prog.copy(), 'inputs': [], 'outputs': [], 'next_amp': None, 'pc': 0, 'relbase': 0}
        signals_to_amp(amp, [item])
        if last_amp:
            last_amp['next_amp'] = amp
        last_amp = amp
        amps.append(amp)
    last_amp['next_amp'] = amps[0] #feedback connection last to first amp
    return amps

def execute_amps(amps):
    last_amp = amps[len(amps) - 1]
    first_amp = amps[0]
    executing_amp = amps[0]
    signals_to_amp(executing_amp, [0])
    while last_amp['pc'] >= 0:
        if executing_amp['pc'] >= 0:
            #print("z {}".format(executing_amp['pc']))
            (executing_amp['pc'], executing_amp['relbase']) = execute_until_output(executing_amp['prog'], executing_amp['pc'], executing_amp['inputs'], executing_amp['outputs'], executing_amp['relbase'])
            signals_to_amp(executing_amp['next_amp'], executing_amp['outputs'])
            executing_amp['outputs'] = []
        else:
            print("not running anymore")
        executing_amp = executing_amp['next_amp']

    # get last output of last amp
    #output = last_amp['outputs'][len(last_amp['outputs']) - 1]
    output = first_amp['inputs'][len(first_amp['inputs']) - 1]
    return output



permuts = get_permutations(list(range(5, 10)))
#permuts = get_permutations(list(range(0, 5)))
max_output = -9999999999

for permut in permuts:
    #print(permut)
    amps = init_amps(mem, permut)
    output = execute_amps(amps)
    if output > max_output:
        max_output = output
        print("new top result: {}".format(max_output))


"""
To do:
Relative mode*
Relative mode outputs*
relative base member*
relative base offset instruction*
infinite memory*
large ints*
refactor
excute according to spec
"""
