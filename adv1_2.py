
import sys
import math

def calc_fuel(mass):
    return math.floor(mass / 3) - 2

def calc_fuel_including_itself(mass):
    fuel = calc_fuel(mass)
    if fuel < 0:
        fuel = 0
        return fuel
    fuel = fuel + calc_fuel_including_itself(fuel)
    #print("*" + str(fuel))
    return fuel
    

def test_calc():
    print(str(calc_fuel_including_itself(12)))
    print(str(calc_fuel_including_itself(14)))
    print(str(calc_fuel_including_itself(1969)))
    print(str(calc_fuel_including_itself(100756)))
    print(str(calc_fuel_including_itself(int("100756"))))

#test_calc()

total_fuel = 0

for line in sys.stdin:
    total_fuel += calc_fuel_including_itself(int(line))

print("")
print(str(int(total_fuel)))
