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
            assert False #TEMP
        params.append(param)
        pos += 1
    return params

def process(mem, pos):
    opcode = mem[pos]

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
        mem[respos] = 1 # hard coded input for now
    if op == 4:
        output = params[0]
        print('output: {}'.format(output)) #just print output for now
    if op == 99:
        pass
    return nof_params + 1

    """
    operand1 = mem[mem[pos + 1]]
    operand2 = mem[mem[pos + 2]]
    respos = mem[pos + 3]

    if opcode == 1:
        mem[respos] = operand1 + operand2
        print('1 mem[respos]:{}'.format(mem[respos]))
        return 4
    if opcode == 2:
        mem[respos] = operand1 * operand2
        print('2 mem[respos]:{}'.format(mem[respos]))
        return 4
    if opcode == 99:
        return 0
    assert False
    """

def execute(mem, noun, verb):

    

    pc = 0
    while True:
        #print('pc:{} mem[pc]:{}'.format(pc, mem[pc]))
        increment = process(mem, pc)
        if increment <= 1:
            break
        pc += increment

def find_input():
    for noun in range(99):
        for verb in range(99):
            mem = [val for val in original_mem] #deep copy
            mem[1] = noun
            mem[2] = verb
            execute(mem, noun, verb)
            if(mem[0] == 19690720):
                return 100 * noun + verb
    assert False

res = find_input()

print(res)


