from typing import List

import math


def fill_output_field(output_field: List[str], variables: List[str], length: int) -> None:
    line_start = "| "
    for count, var in enumerate(variables):
        count += 1
        line_start += var[-1] + " "  # get last number(value)
        if count % math.sqrt(length) == 0:
            line_start += "| "
        if count % length == 0:
            line_start = line_start.strip()
            line_start += "\n"
            output_field.append(line_start)
            line_start = "| "


def create_sep_line(length) -> str:
    cell_length = int(math.ceil(math.log(length, 10)))
    start_separator = 1
    sqrt_of_length = int(math.sqrt(length))
    separator_between_cells = 1
    return ("+"
            + "-"
            * (start_separator
               + (sqrt_of_length
                  * (cell_length
                     + separator_between_cells)))) \
           * sqrt_of_length \
           + "+\n"


def read_source(source_path: str) -> None:
    with open(source_path) as solution:
        content = solution.readlines()
    #  remove 'v' and split string into single strings
    variables = content[-1].replace("v ", "").split()
    # get only positive values
    variables = list(filter(lambda x: int(x) > 0, variables))
    length = 9
    # get concrete values from variables
    output_field = list()
    fill_output_field(output_field, variables, length)

    # insert horizontal separator_lines for block
    for i in range(int(math.sqrt(length)) + 1):
        output_field.insert(int(math.sqrt(length) + 1) * i, create_sep_line(length))

    # write output_file
    with open("../../../examples/bsp-sudoku-output2.txt", "w") as output:
        output.writelines(info)
        output.writelines(output_field)


read_source("../../../examples/bsp-sudoku-SAT-sol.txt")
