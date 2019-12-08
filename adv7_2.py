import sys



for line in sys.stdin:
    #print(line)
    mem = [int(opcode) for opcode in line.split(',')]
    break

original_mem = [val for val in mem] #deep copy
#print(original_mem)

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
    if op == 99:
        return 0
    assert False

def get_parameters(mem, pos, opmodes):
    params = []
    for opmode in opmodes:
        immediate_val = mem[pos]
        if opmode == 0: # position mode
            param = mem[immediate_val]
        else: # immediate_mode
            param = immediate_val
        params.append(param)
        pos += 1
    return params

def process(mem, pos, inputs, outputs):
    opcode = mem[pos]

    jump = False

    nof_params = get_nof_params(opcode)
    (op, opmodes) = get_op(mem, pos, nof_params)
    params = get_parameters(mem, pos + 1, opmodes)
    
    if op == 1:
        respos = mem[pos + 3]
        mem[respos] = params[0] + params[1]
        #print('1 mem[respos]:{}'.format(mem[respos]))
    if op == 2:
        respos = mem[pos + 3]
        mem[respos] = params[0] * params[1]
        #print('2 mem[respos]:{}'.format(mem[respos]))
    if op == 3:
        respos = mem[pos + 1]
        mem[respos] = inputs.pop(0)
        #print("got signal {}".format(mem[respos]))
    if op == 4:
        output = params[0]
        #print('output: {}'.format(output))
        outputs.append(output)
    if op == 5:
        if params[0] != 0:
            pos = params[1]
            jump = True
    if op == 6:
        if params[0] == 0:
            pos = params[1]
            jump = True
    if op == 7:
        respos = mem[pos + 3]        
        mem[respos] = 1 if params[0] < params[1] else 0
    if op == 8:
        respos = mem[pos + 3]        
        mem[respos] = 1 if params[0] == params[1] else 0
    if op == 99:
        pos = -1
        jump = True

    if not jump:
        pos = pos + 1 + nof_params

    return pos

def execute(mem, inputs, outputs):
    pc = 0
    while True:
        #print('pc:{} mem[pc]:{}'.format(pc, mem[pc]))
        pc = process(mem, pc, inputs, outputs)
        if pc < 0:
            break

def execute_until_output(mem, pc, inputs, outputs):
    while pc >=0 and len(outputs) == 0:
        pc = process(mem, pc, inputs, outputs)
    return pc

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
        amp = {'prog': prog.copy(), 'inputs': [], 'outputs': [], 'next_amp': None, 'pc': 0}
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
            executing_amp['pc'] = execute_until_output(executing_amp['prog'], executing_amp['pc'], executing_amp['inputs'], executing_amp['outputs'])
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


