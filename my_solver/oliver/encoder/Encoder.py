from typing import List

import math

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput, PuzzleInfoEncode
from my_solver.oliver.encoder.Position import Position


def convert_pos_into_var(pos: Position, length: int) -> str:
    """
    Convert a position of the sudoku-field into a variable

    Example 5. row 4. column and value 9 in 9x9 Puzzle is in old 549
    New it is 5*9*9+4*9+9

    :param pos:
    :param length:
    :return:
    """
    var = pos.row * (length ** 2) \
          + pos.column * length \
          + pos.value
    return str(var)


def convert_var_into_pos(var: int, length: int) -> Position:
    row = int(var / (length ** 2)) % length
    if row == 0:
        row = length
    column = int(var / length) % length
    if column == 0:
        column = length
    value = var % length
    if value == 0:
        value = length
    return Position(row, column, value)


def distinct_column_clause(column: int, length: int) -> List[str]:
    """  Create the clauses, that describe, that one column has every value exactly once

    :param column: column that get the clauses.
    :param length: number of values from 1 to length
    :return: clauses for the column
    """
    back = list()
    for upper_row in range(1, length + 1):
        for lower_row in range(upper_row + 1, length + 1):
            for value in range(1, length + 1):
                current = "-{row}{column}{value} -{row2}{column}{value} 0\n". \
                    format(column=column, row=upper_row, value=value, row2=lower_row)
                back.append(current)
    return back


def distinct_row_clause(row: int, length: int) -> List[str]:
    """

    :param row: row that get clauses
    :param length: number of values from 1 to length
    :return: clauses fro the row
    """
    back = list()
    for left_column in range(1, length + 1):
        for right_column in range(left_column + 1, length + 1):
            for value in range(1, length + 1):
                current = "-{row}{column}{value} -{row}{column2}{value} 0\n". \
                    format(column=left_column, row=row, value=value, column2=right_column)
                back.append(current)
    return back


def one_value_per_cell_clause(row_count: int, cell_count: int, length: int) -> str:
    # TODO improve with format
    back = ""
    for i in range(length):
        back += str(row_count + 1) + str(cell_count + 1) + str(i + 1) + " "
    back += "0\n"
    return back


def calc_clauses_for_cell_in_block(row_in_block, column_in_block, sqrt_of_length, start_row, start_column) -> List[str]:
    result = list()
    pos_in_block = (row_in_block - 1) * int(sqrt_of_length ** 2) + column_in_block

    for current_row in range(start_row, start_row + sqrt_of_length):
        for current_column in range(start_column, start_column + sqrt_of_length):
            if (current_row - 1) * int(sqrt_of_length ** 2) + current_column <= pos_in_block:
                continue
            for value in range(1, int(sqrt_of_length ** 2) + 1):
                back = "-{row}{column}{value} -{row2}{column2}{value} 0\n" \
                    .format(column=column_in_block, row=row_in_block, value=value,
                            column2=current_column, row2=current_row)
                result.append(back)
    return result


def distinct_block_clauses(block_pos: List[int], length: int) -> List[str]:
    block_clauses = list()
    # for 1.1 1 will reached by     1.2 1.3 are not 1
    #                          2.1 2.2 2.3
    #                          3.1 3.2 3.3
    # same for 2 to 9
    # this continue with 1.2 2 by ...
    sqrt_of_length = int(math.sqrt(length))
    start_row = block_pos[0] * sqrt_of_length + 1
    start_column = block_pos[1] * sqrt_of_length + 1

    # for one pos in block
    for line in range(start_row, start_row + sqrt_of_length):
        for cell in range(start_column, start_column + sqrt_of_length):
            block_clauses.extend(calc_clauses_for_cell_in_block(line, cell, sqrt_of_length, start_row, start_column))
    return block_clauses


def write_cnf_file(clauses, output_file, start_line):
    with open(output_file, "w")as output_file:
        output_file.write(start_line)
        output_file.writelines(clauses)


def encode(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
    length = info.length

    clauses = list()

    # num_var = (10 ** (round(math.log(length, 10), 1))) ** 3
    num_var = int(str(length) * 3)  # TODO IMPROVE THE NUMBER

    # add clauses for at least one possible value in each cell
    one_per_cell_clauses = list()
    unit_clauses = list()
    for row_count, row in enumerate(field):
        for cell_count, cell in enumerate(row):
            one_per_cell_clauses.append(one_value_per_cell_clause(row_count, cell_count, length))
            # add known values to unit_clause
            if cell != 0:
                unit_clauses.append(
                    "{row_count}{cell_count}{value} 0\n".format(row_count=row_count + 1, cell_count=cell_count + 1,
                                                                value=cell))

    # add clauses for row distinction
    row_clauses = list()
    for row in range(1, length + 1):
        row_clauses.extend(distinct_row_clause(row, length))

    # add clauses for column  distinction
    column_clauses = list()
    for column in range(1, length + 1):
        column_clauses.extend(distinct_column_clause(column, length))

    # add clauses for block distinction
    block_clauses = list()
    block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
    cells_per_block = info_input.sqrt_of_length
    for block in range(length):
        block_pos[0] = int(block / cells_per_block)
        block_pos[1] = block % cells_per_block
        block_clauses.extend(distinct_block_clauses(block_pos, length))

    # add clauses for each cell has only one value
    distinct_cell_clauses = list()
    for row in range(1, length + 1):
        for column in range(1, length + 1):
            for value in range(1, length + 1):
                for other in range(value + 1, length + 1):
                    clause = "-{row}{column}{value} -{row}{column}{value2} 0\n". \
                        format(column=column, row=row, value=value, value2=other)
                    distinct_cell_clauses.append(clause)
    # add clauses in specific order (by length)
    clauses.extend(unit_clauses)
    clauses.extend(distinct_cell_clauses)
    clauses.extend(row_clauses)
    clauses.extend(column_clauses)
    clauses.extend(block_clauses)
    clauses.extend(one_per_cell_clauses)
    # only to mark clauses, that are double
    # for pos, clause in enumerate(clauses):
    #     if 1 < clauses.count(clause):
    #         clauses[pos] = "HIER IST WAS DOPPELT: " + clause
    num_clause = len(clauses)
    start_line = "p cnf {num_var} {num_clause}\n" \
        .format(num_var=num_var, num_clause=num_clause)

    output_file = info.output_file_complete_absolute()
    write_cnf_file(clauses, output_file, start_line)
    return info
