import re

import math


def create_sep_line(length) -> str:
    return ("+" + "-" * (int(math.sqrt(length)) * 2 + 1)) * int(math.sqrt(length)) + "+\n"


def read_source(source_path: str) -> None:
    with open(source_path) as solution:
        content = solution.readlines()
    variables = content[-1]
    variables = variables.replace("v ", "")
    variables = re.sub(r"-\d+ ", "", variables).split()
    length = 9
    # variables = list(map(lambda x: int(x), variables))
    for count, i in enumerate(variables):
        if count % 9 == 0:
            print()
        print(str(i) + "|", end="")
    # get concrete values from variables
    output_field = list()
    line = "| "
    for count, var in enumerate(variables):
        count += 1
        line += var[-1] + " "
        if count % math.sqrt(length) == 0:
            line += "| "
        if count % length == 0:
            line = line.strip()
            line += "\n"
            output_field.append(line)
            line = "| "
    for i in range(int(math.sqrt(length)) + 1):
        output_field.insert(int(math.sqrt(length)+1) * i, create_sep_line(length), )
    info = ["3","7\n"]

    with open("../../../examples/bsp-sudoku-output2.txt", "w") as output:
        output.writelines(info)
        output.writelines(output_field)

read_source("../../../examples/bsp-sudoku-SAT-sol.txt")
