import sys



for line in sys.stdin:
    #print(line)
    mem = [int(opcode) for opcode in line.split(',')]
    break

original_mem = [val for val in mem] #deep copy
#print(original_mem)

def process(mem, pos):
    opcode = mem[pos]
    operand1 = mem[mem[pos + 1]]
    operand2 = mem[mem[pos + 2]]
    respos = mem[pos + 3]

    if opcode == 1:
        mem[respos] = operand1 + operand2
        return True
    if opcode == 2:
        mem[respos] = operand1 * operand2
        return True
    if opcode == 99:
        return False
    assert False

def execute(mem, noun, verb):

    mem[1] = noun
    mem[2] = verb

    for i in range(0, len(mem), 4):
        #print('i:{} mem[i]:{}'.format(i, mem[i]))
        if not process(mem, i):
            break

def find_input():
    for noun in range(99):
        for verb in range(99):
            mem = [val for val in original_mem] #deep copy
            execute(mem, noun, verb)
            if(mem[0] == 19690720):
                return 100 * noun + verb
    assert False

res = find_input()

print(res)


