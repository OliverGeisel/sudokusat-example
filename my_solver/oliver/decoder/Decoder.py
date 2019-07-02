from typing import List

import math

from my_solver.oliver.PuzzleInfo import PuzzleInfoOutput, PuzzleInfoEncode
from my_solver.oliver.encoder.Encoder import convert_var_into_pos


def fill_output_field(output_field: List[str], variables: List[str], length: int) -> None:
    line_start = "| "
    for count, var in enumerate(variables):
        count += 1
        pos = convert_var_into_pos(int(var), length)
        line_start += str(pos.value) + " "  # get last number(value)
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


def decode(encode_info: PuzzleInfoEncode) -> None:
    info = PuzzleInfoOutput(encode_info)
    path = info.input_file_complete_absolute()
    filled_sudoku = read_source(path)
    write_solution_file(info, filled_sudoku)
    pass


def read_source(source_path: str) -> List[str]:
    with open(source_path) as solution:
        content = solution.readlines()
    #  remove 'v' and split string into single strings
    variables = content[-1].replace("v ", "").split()
    # get only positive values
    # variables = [x for x in variables if int(x) > 0]
    variables = list(filter(lambda x: int(x) > 0, variables))
    length = 9  # TODO Info!!
    # get concrete values from variables
    output_field = list()
    fill_output_field(output_field, variables, length)
    # insert horizontal separator_lines for block
    add_horizontal_lines(length, output_field)
    return output_field


def add_horizontal_lines(length, output_field):
    for i in range(int(math.sqrt(length)) + 1):
        output_field.insert(int(math.sqrt(length) + 1) * i, create_sep_line(length))


def write_solution_file(info, output_field):
    with open(info.output_file_complete_absolute(), "w") as output:
        output.writelines(info.text)
        output.writelines(output_field)
