import os
import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoEncode, PuzzleInfoInput
from my_solver.oliver.encoder.Position import Position
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file_list_join_interpolation_map


def distinct_column_clause_list(column: int, info: PuzzleInfoEncode) -> List[List[int]]:
    """  Create the clauses, that describe, that one column has every value exactly once

    :param column: column that get the clauses.
    :param info: number of values from 1 to length
    :return: clauses for the column as list
    """
    length = info.length
    back = list()
    first_pos = Position(info, 0, column)
    second_pos = Position(info, 0, column)
    for upper_row in range(1, length + 1):
        first_pos.set_row(upper_row)
        for lower_row in range(upper_row + 1, length + 1):
            second_pos.set_row(lower_row)
            for value in range(1, length + 1):
                first_pos.set_value(value)
                second_pos.set_value(value)
                back.append([first_pos.var, second_pos.var])
    return back


def distinct_row_clause_list(row: int, info: PuzzleInfoEncode) -> List[List[int]]:
    """

    :param row: row that get clauses
    :param info: number of values from 1 to length
    :return: clauses for the row
    """
    length = info.length
    back = list()
    first_pos = Position(info, row, 0)
    second_pos = Position(info, row, 0)
    for left_column in range(1, length + 1):
        first_pos.set_column(left_column)
        for right_column in range(left_column + 1, length + 1):
            second_pos.set_column(right_column)
            for value in range(1, length + 1):
                first_pos.set_value(value)
                second_pos.set_value(value)
                back.append([first_pos.var, second_pos.var])
    return back


def one_value_per_cell_clause_list(row_count: int, cell_count: int, info: PuzzleInfoEncode) -> List[int]:
    literals = list()
    pos = Position(info, row_count, cell_count)
    for i in range(1, info.length + 1):
        pos.set_value(i)
        literals.append(pos.var)
    return literals


def exactly_one_value_per_cell_list(row: int, column: int, info: PuzzleInfoEncode) -> List[List[int]]:
    exactly_one_value_per_cell_clause = list()
    first_pos = Position(info, row, column)
    second_pos = Position(info, row, column)
    for value in range(1, info.length + 1):
        first_pos.set_value(value)
        for other in range(value + 1, info.length + 1):
            second_pos.set_value(other)
            clause = [first_pos.var, second_pos.var]
            exactly_one_value_per_cell_clause.append(clause)
    return exactly_one_value_per_cell_clause


def only_one_solution_per_row_clause_list(row: int, info: PuzzleInfoEncode) -> List[List[int]]:
    back = list()
    pos = Position(info, row)
    for value in range(1, info.length + 1):
        pos.set_value(value)
        clause = list()
        for column in range(1, info.length + 1):
            pos.set_column(column)
            clause.append(pos.var)
        back.append(clause)
    return back


def only_one_solution_per_column_clause_list(column: int, info: PuzzleInfoEncode) -> List[List[int]]:
    back = list()
    pos = Position(info, column=column)
    for value in info.values:
        pos.set_value(value)
        clause = list()
        for row in info.values:
            pos.set_row(row)
            clause.append(pos.var)
        back.append(clause)
    return back


def only_one_solution_per_block_clause_list(block_pos: List[int], info: PuzzleInfoEncode) -> List[List[int]]:
    back = list()
    sqrt_of_length = info.sqrt_of_length
    start_row = block_pos[0] * sqrt_of_length + 1
    start_column = block_pos[1] * sqrt_of_length + 1
    pos = Position(info, start_row, start_column)
    for value in info.values:
        pos.set_value(value)
        clause = list()
        for row_in_block in range(start_row, start_row + sqrt_of_length):
            pos.set_row(row_in_block)
            for column_in_block in range(start_column, start_column + sqrt_of_length):
                pos.set_column(column_in_block)
                clause.append(pos.var)
        back.append(clause)
    return back


def calc_clauses_for_cell_in_block_list(row_in_block, column_in_block, info: PuzzleInfoEncode, start_row,
                                        start_column) -> \
        List[List[int]]:
    """
    Get Clauses that encode that the cell(start_row,start_column) to be distinct from the other cells
    :param row_in_block:
    :param column_in_block:
    :param info:
    :param start_row:
    :param start_column:
    :return:
    """
    result = list()
    sqrt_of_length = info.sqrt_of_length
    first_cell_pos_in_block = (row_in_block - 1) * info.sqrt_of_length + column_in_block
    first_pos = Position(info, start_row - 1 + row_in_block, start_column - 1 + column_in_block)
    second_pos = Position(info)
    # absolute row in puzzle
    for current_row in range(start_row, start_row + sqrt_of_length):
        # absolute column in puzzle
        if current_row <= start_row - 1 + row_in_block:
            continue
        second_pos.set_row(current_row)
        for current_column in range(start_column, start_column + sqrt_of_length):
            # skip if cell is behind the start_cell
            second_cell_pos = ((current_row - 1) % sqrt_of_length) * sqrt_of_length \
                              + (current_column - 1) % sqrt_of_length + 1
            if second_cell_pos <= first_cell_pos_in_block:
                continue
            # skipp if cell is in same row OR column
            if current_column == start_column - 1 + column_in_block:
                continue
            second_pos.set_column(current_column)
            for value in range(1, info.length + 1):
                first_pos.set_value(value)
                second_pos.set_value(value)
                result.append([first_pos.var, second_pos.var])
    return result


def distinct_block_clauses_list(block_pos: List[int], info: PuzzleInfoEncode) -> List[List[int]]:
    """
    Calculate all clauses for one block in puzzle
    :param block_pos: position of the block in puzzle
    :param info: Information about the puzzle
    :return: clauses for the block as string
    """
    block_clauses = list()
    # for 1.1 1 will reached by    1.2 1.3 are not 1
    #                          2.1 2.2 2.3
    #                          3.1 3.2 3.3
    # same for 2 to 9
    # this continue with 1.2 2 by ...
    sqrt_of_length = info.sqrt_of_length
    start_row = block_pos[0] * sqrt_of_length + 1
    start_column = block_pos[1] * sqrt_of_length + 1
    # for one pos in block
    for line in range(start_row, start_row + sqrt_of_length - 1):
        for cell in range(start_column, start_column + sqrt_of_length):
            row_in_block = (line - 1) % sqrt_of_length + 1
            column_in_block = (cell - 1) % sqrt_of_length + 1
            block_clauses.extend(
                calc_clauses_for_cell_in_block_list(row_in_block, column_in_block, info, start_row, start_column))
    return block_clauses


def calc_block_clauses_list(block_clauses, block_one_clauses, info) -> None:
    start = time.perf_counter()
    block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
    blocks_in_row = info.sqrt_of_length
    for block in range(info.length):
        block_pos[0] = int(block / blocks_in_row)
        block_pos[1] = block % blocks_in_row
        block_clauses.extend(distinct_block_clauses_list(block_pos, info))
        block_one_clauses.extend(only_one_solution_per_block_clause_list(block_pos, info))
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish block! Time: " + str(time_to_encode))


def calc_column_clauses_list(column_clauses, column_one_clauses, info) -> None:
    start = time.perf_counter()
    for column in range(1, info.length + 1):
        column_clauses.extend(distinct_column_clause_list(column, info))
        column_one_clauses.extend(only_one_solution_per_column_clause_list(column, info))
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish column! Time: " + str(time_to_encode))


def calc_row_clauses_list(row_clauses, row_one_clauses, info) -> None:
    start = time.perf_counter()
    for row in range(1, info.length + 1):
        row_clauses.extend(distinct_row_clause_list(row, info))
        row_one_clauses.extend(only_one_solution_per_row_clause_list(row, info))
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish row! Time: " + str(time_to_encode))


def calc_cell_clauses_list(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info) -> None:
    start = time.perf_counter()
    pos = Position(info)
    for row_count, row in enumerate(field):
        row_count += 1
        pos.set_row(row_count)
        for cell_count, cell in enumerate(row):
            cell_count += 1
            pos.set_column(cell_count)
            if cell != 0:
                # add known values to unit_clause
                pos.set_value(cell)
                u_clause = pos.var
                unit_clauses.append([u_clause, 1])
                for i in range(1, info.length + 1):
                    if i == cell:
                        continue
                    pos.set_value(i)
                    unit_clauses.append([pos.var, 0])
            else:
                # if not known add at least and exactly one value clauses to formula
                clause = one_value_per_cell_clause_list(row_count, cell_count, info)
                one_per_cell_clauses.append(clause)
                cell_clauses = exactly_one_value_per_cell_list(row_count, cell_count, info)
                distinct_cell_clauses.extend(cell_clauses)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish cell! Time: " + str(time_to_encode))


def write_temp_file(clauses, info: PuzzleInfoEncode, name: str, template):
    path = os.path.join(info.input_file_path, name)
    info.temp_files.append(path)
    lines_to_write = list()
    with open(path, "w") as temp_file:
        lines_to_write.extend(template(clauses))
        temp_file.write("".join(lines_to_write))


def write_cnf_from_parts(temp_files, output_file_name, start_line):
    with open(output_file_name, "w")as output_file:
        lines_to_write = list()
        lines_to_write.append(start_line)
        for file in temp_files:
            with open(file) as temp_file:
                lines_to_write.append(temp_file.read())
        output_file.write("".join(lines_to_write))


def encode(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)

    def unit_template_function(temp_clauses):
        return [f"{'' if x[1] else '-'}{x[0]} 0\n" for x in temp_clauses]

    def binary_template_function(temp_clauses):
        return [f"-{x[0]} -{x[1]} 0\n" for x in temp_clauses]

    def one_template_function(temp_clauses):
        back = list()
        for clause in temp_clauses:
            back.append(f"{' '.join([str(x) for x in clause])} 0\n")
        return back

    one_per_cell_clauses = list()
    unit_clauses = list()
    distinct_cell_clauses = list()

    row_clauses = list()
    row_one_clauses = list()

    column_clauses = list()
    column_one_clause = list()

    block_clauses = list()
    block_one_clauses = list()

    # add clauses for at least one possible value in each cell
    calc_cell_clauses_list(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info)
    if info.length >= 64:
        write_temp_file(distinct_cell_clauses, info, "dist_cell.txt", binary_template_function)
        distinct_cell_clauses.clear()
        write_temp_file(one_per_cell_clauses, info, "one_cell.txt", one_template_function)
        one_per_cell_clauses.clear()
        write_temp_file(unit_clauses, info, "unit_cell.txt", unit_template_function)
        unit_clauses.clear()

    # add clauses for row distinction
    calc_row_clauses_list(row_clauses, row_one_clauses, info)
    if info.length >= 64:
        write_temp_file(row_clauses, info, "row.txt", binary_template_function)
        row_clauses.clear()
        write_temp_file(row_one_clauses, info, "one_row.txt", one_template_function)
        row_one_clauses.clear()
    # add clauses for column  distinction
    calc_column_clauses_list(column_clauses, column_one_clause, info)
    if info.length >= 64:
        write_temp_file(column_clauses, info, "column.txt", binary_template_function)
        column_clauses.clear()
        write_temp_file(column_one_clause, info, "one_column.txt", one_template_function)
        column_one_clause.clear()
    # add clauses for block distinction
    calc_block_clauses_list(block_clauses, block_one_clauses, info)
    if info.length >= 64:
        write_temp_file(block_clauses, info, "block.txt", binary_template_function)
        block_clauses.clear()
        write_temp_file(block_one_clauses, info, "one_block.txt", one_template_function)
        block_one_clauses.clear()
    if info.length >= 64:
        # clean lists
        pass
    else:
        clauses = dict()
        clauses["dist"] = distinct_cell_clauses
        clauses["one"] = one_per_cell_clauses
        clauses["unit"] = unit_clauses

        clauses["row"] = row_clauses
        clauses["row_one"] = row_one_clauses

        clauses["column"] = column_clauses
        clauses["column_one"] = column_one_clause

        clauses["block"] = block_clauses
        clauses["block_one"] = block_one_clauses

    num_clause = sum([len(x) for x in clauses.values()]) if info.length < 64 else (64 ** 3) * 2
    num_var = info.length * info.square_of_length
    start_line = f"p cnf {num_var} {num_clause}\n"
    output_file = info.output_file_complete_absolute()

    start = time.perf_counter()
    if info.length >= 64:
        write_cnf_from_parts(info.temp_files, output_file, start_line)
    else:
        write_cnf_file_list_join_interpolation_map(clauses, output_file, start_line)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to write CNF-File: {time}s".format(time=time_to_encode))
    return info
