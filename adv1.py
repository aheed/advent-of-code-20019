
import sys
import math

def calc_fuel(mass):
    return math.floor(mass / 3) - 2

def test_calc():
    print(str(calc_fuel(12)))
    print(str(calc_fuel(14)))
    print(str(calc_fuel(1969)))
    print(str(calc_fuel(100756)))
    print(str(calc_fuel(int("100756"))))

#test_calc()

total_fuel = 0

for line in sys.stdin:
    total_fuel += calc_fuel(int(line))

print("")
print(str(int(total_fuel)))
