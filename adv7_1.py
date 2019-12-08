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
    if op == 4:
        output = params[0]
        #print('output: {}'.format(output)) #just print output for now
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

"""
def find_input():
    for noun in range(99):
        for verb in range(99):
            mem = [val for val in original_mem] #deep copy
            mem[1] = noun
            mem[2] = verb
            execute(mem)
            if(mem[0] == 19690720):
                return 100 * noun + verb
    assert False

#res = find_input()
#print(res)
"""

def add_perm_number(perms):
    new_perms_list = []
    for perm in perms:
        #print(perm)
        new_perm_number = len(perm)
        for index in range(new_perm_number + 1):
            new_perm = perm.copy()
            #print(new_perm)
            new_perm.insert(index, new_perm_number)
            #print(new_perm)
            new_perms_list.append(new_perm)
    return new_perms_list

def get_permutations(max):
    ret = [[0]]
    for number in range(1, max):
        ret = add_perm_number(ret)
    return ret

"""
permuts = get_permutations(5)
print(permuts)
print(len(permuts))

execute(mem, [5])
"""

permuts = get_permutations(5)
max_output = -9999999999

for permut in permuts:
    output = 0
    for amp in range(len(permut)):
        mem = original_mem.copy()
        inputs = [permut[amp], output]
        #print("inputs=" + str(inputs))
        outputs = []
        result = execute(mem, inputs, outputs)
        output = outputs[0] #assume the program will yield exactly one output
        #print("output=" + str(output))
    if output > max_output:
        max_output = output
        print("new top result: {}".format(max_output))

"""
todo:
input queue per execution*
phase permutations*
daisy chain executions
"""
