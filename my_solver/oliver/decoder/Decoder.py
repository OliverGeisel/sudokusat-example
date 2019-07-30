import math
import os
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoOutput, PuzzleInfo, PuzzleInfoEncode
from my_solver.oliver.encoder.Position import Position


class UnsatisfiableException(Exception):
    pass


def convert_var_into_pos(var: int, info: PuzzleInfo) -> Position:
    """

    :param var:
    :param info:
    :return:
    """
    length = info.length

    row = int(var / info.square_of_length) % length
    if row == 0:
        row = length if var > length else 1
    column = int(var / length) % length
    if column == 0:
        column = length if var > length else 1
    value = var % length
    if value == 0:
        value = length
    return Position(info, row, column, value)


def fill_output_field(output_field: List[str], variables: List[str], info: PuzzleInfoOutput) -> None:
    line_start = "| "
    width = math.ceil(math.log(info.length, 10))
    for count, var in enumerate(variables):
        count += 1
        pos = convert_var_into_pos(int(var), info)

        line_start += "{:>{width}}".format(str(pos.value), width=width) + " "  # get last number(value)
        if count % info.sqrt_of_length == 0:
            line_start += "| "
        if count % info.length == 0:
            line_start = line_start.strip()
            line_start += "\n"
            output_field.append(line_start)
            line_start = "| "


def create_sep_line(info: PuzzleInfo) -> str:
    cell_length = int(math.ceil(math.log(info.length, 10)))
    start_separator = 1
    separator_between_cells = 1
    num_of_minus = (start_separator + (info.sqrt_of_length * (cell_length + separator_between_cells)))
    return f'{("+" + "-" * num_of_minus) * info.sqrt_of_length}+\n'


def decode(encode_info: PuzzleInfoEncode) -> None:
    info = PuzzleInfoOutput(encode_info)
    path = os.path.join("tmp", info.task, info.input_file_name)
    try:
        filled_sudoku = read_source(path, info)
    except UnsatisfiableException:
        return
    except RuntimeError:
        return
    write_solution_file(info, filled_sudoku)
    print(info.text)
    for i in filled_sudoku:
        print(i, end="")


def read_source(source_path: str, info: PuzzleInfoOutput) -> List[str]:
    with open(source_path, "r") as solution:
        content = solution.readlines()

    satisfiable = [x for x in content if x[0] == "s"][0]
    if "UNSATISFIABLE".lower() in satisfiable.lower():
        write_solution_file(info, "NO Solution\n")
        raise UnsatisfiableException
    if "UNKNOWN" in satisfiable:
        raise RuntimeError
    #  remove 'v'
    var_lines = [x for x in content if x[0] == "v"]
    var_lines = list(map(lambda x: x.replace("v ", ""), var_lines))
    variables = list()
    for current_line in var_lines:
        # get only positive values
        current_vars = [x for x in current_line.split() if int(x) > 0]
        variables.extend(current_vars)
    # get concrete values from variables
    output_field = list()
    fill_output_field(output_field, variables, info)
    # insert horizontal separator_lines for block
    add_horizontal_lines(info, output_field)
    return output_field


def add_horizontal_lines(info, output_field):
    sep_line = create_sep_line(info)
    for i in range(info.sqrt_of_length + 1):
        output_field.insert((info.sqrt_of_length + 1) * i, sep_line)


def write_solution_file(info, main_output):
    output_file_path = os.path.join("tmp", info.task, info.output_file_name)
    with open(output_file_path, "w") as output:
        output.writelines(info.text)
        output.writelines(main_output)
