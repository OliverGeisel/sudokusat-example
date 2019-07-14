import multiprocessing
import threading
import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput, PuzzleInfoEncode
from my_solver.oliver.encoder.Position import Position


def convert_pos_into_var(pos: Position, info: PuzzleInfoEncode) -> str:
    """
    Convert a position of the sudoku-field into a variable

    Example 5. row 4. column and value 9 in 9x9 Puzzle is in old 549
    New it is 4*9*9+3*9+9

    :param pos:
    :param info:
    :return:
    """
    var = (pos.row - 1) * info.square_of_length \
          + (pos.column - 1) * info.length \
          + pos.value
    return str(var)


def convert_var_into_pos(var: int, length: int) -> Position:
    """

    :param var:
    :param length:
    :return:
    """
    row = int(var / (length ** 2)) % length
    if row == 0:
        row = length if var > length else 1
    column = int(var / length) % length
    if column == 0:
        column = length if var > length else 1
    value = var % length
    if value == 0:
        value = length
    return Position(row, column, value)


def positions_to_str(first_pos: Position, second_pos: Position, info: PuzzleInfoEncode, first_positive: bool = False,
                     second_positive: bool = False) -> str:
    # row1, column1, value1 = first_pos.get_tuple()
    # row2, column2, value2 = second_pos.get_tuple()
    sign1 = "" if first_positive else "-"
    sign2 = "" if second_positive else "-"
    # Todo join() better?
    return "{sign1}{var1} {sign2}{var2} 0\n".format(sign1=sign1, var1=convert_pos_into_var(first_pos, info),
                                                    sign2=sign2, var2=convert_pos_into_var(second_pos, info))


def distinct_column_clause(column: int, info: PuzzleInfoEncode) -> List[str]:
    """  Create the clauses, that describe, that one column has every value exactly once

    :param column: column that get the clauses.
    :param info: number of values from 1 to length
    :return: clauses for the column
    """

    length = info.length
    back = list()
    for upper_row in range(1, length + 1):
        for lower_row in range(upper_row + 1, length + 1):
            for value in range(1, length + 1):
                first_pos = Position(upper_row, column, value)
                second_pos = Position(lower_row, column, value)
                back.append(positions_to_str(first_pos, second_pos, info))
    return back


def distinct_row_clause(row: int, info: PuzzleInfoEncode) -> List[str]:
    """

    :param row: row that get clauses
    :param info: number of values from 1 to length
    :return: clauses fro the row
    """
    length = info.length
    back = list()
    for left_column in range(1, length + 1):
        for right_column in range(left_column + 1, length + 1):
            for value in range(1, length + 1):
                first_pos = Position(row, left_column, value)
                second_pos = Position(row, right_column, value)
                back.append(positions_to_str(first_pos, second_pos, info))
    return back


def one_value_per_cell_clause(row_count: int, cell_count: int, info: PuzzleInfoEncode) -> str:
    literals = list()
    for i in range(1, info.length + 1):
        pos = Position(row_count, cell_count, i)
        literals.append(convert_pos_into_var(pos, info))
    literals.append("0\n")
    back = " ".join(literals)
    return back


def exactly_one_value_per_cell(row: int, column: int, info: PuzzleInfoEncode) -> List[str]:
    exactly_one_value_per_cell_clause = list()
    for value in range(1, info.length + 1):
        for other in range(value + 1, info.length + 1):
            first_pos = Position(row, column, value)
            second_pos = Position(row, column, other)
            clause = positions_to_str(first_pos, second_pos, info)
            exactly_one_value_per_cell_clause.append(clause)
    return exactly_one_value_per_cell_clause


def calc_clauses_for_cell_in_block(row_in_block, column_in_block, info: PuzzleInfoEncode, start_row, start_column) -> \
        List[str]:
    result = list()
    sqrt_of_length = info.sqrt_of_length
    pos_in_block = (row_in_block - 1) * int(sqrt_of_length ** 2) + column_in_block

    for current_row in range(start_row, start_row + sqrt_of_length):
        for current_column in range(start_column, start_column + sqrt_of_length):
            if (current_row - 1) * int(sqrt_of_length ** 2) + current_column <= pos_in_block:
                continue
            for value in range(1, int(sqrt_of_length ** 2) + 1):
                first_pos = Position(row_in_block, column_in_block, value)
                second_pos = Position(current_row, current_column, value)
                result.append(positions_to_str(first_pos, second_pos, info))
    return result


def distinct_block_clauses(block_pos: List[int], info: PuzzleInfoEncode) -> List[str]:
    block_clauses = list()
    # for 1.1 1 will reached by    1.2 1.3 are not 1
    #                          2.1 2.2 2.3
    #                          3.1 3.2 3.3
    # same for 2 to 9
    # this continue with 1.2 2 by ...
    sqrt_of_length = info.sqrt_of_length
    start_row = block_pos[0] * sqrt_of_length + 1
    start_column = block_pos[1] * sqrt_of_length + 1
    # Todo parallel?
    # for one pos in block
    for line in range(start_row, start_row + sqrt_of_length):
        for cell in range(start_column, start_column + sqrt_of_length):
            block_clauses.extend(calc_clauses_for_cell_in_block(line, cell, info, start_row, start_column))
    return block_clauses


def write_cnf_file(clauses, output_file, start_line):
    with open(output_file, "w")as output_file:
        output_file.write(start_line)
        output_file.writelines(clauses)


def encode(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
    length = info.length

    # add clauses for at least one possible value in each cell
    one_per_cell_clauses = list()
    unit_clauses = list()
    distinct_cell_clauses = list()

    row_clauses = list()
    column_clauses = list()

    block_clauses = list()
    calc_cell_clauses(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info)

    # add clauses for row distinction
    calc_row_clauses(row_clauses, info)

    # add clauses for column  distinction
    calc_column_clauses(column_clauses, info)

    # add clauses for block distinction
    calc_block_clauses(block_clauses, info)

    # add clauses in specific order (by length)
    clauses = list()
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
    num_var = length ** 3

    start_line = "p cnf {num_var} {num_clause}\n" \
        .format(num_var=num_var, num_clause=num_clause)

    output_file = info.output_file_complete_absolute()
    start = time.perf_counter()
    write_cnf_file(clauses, output_file, start_line)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to write CNF-File: {time}s".format(time=time_to_encode))
    return info


def encode_parallel(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
    length = info.length

    # add clauses for at least one possible value in each cell
    one_per_cell_clauses = list()
    unit_clauses = list()
    distinct_cell_clauses = list()

    row_clauses = list()
    column_clauses = list()

    block_clauses = list()

    thread_list = list()

    # Todo name of thread
    # arguments = [distinct_cell_clauses, field, info, length, one_per_cell_clauses, unit_clauses]
    # thread_cell = threading.Thread(target=calc_cell_clauses, args=arguments)
    # thread_list.append(thread_cell)
    calc_cell_clauses(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info)

    arguments = [row_clauses, info]
    thread_row = threading.Thread(target=calc_row_clauses, args=arguments)
    thread_list.append(thread_row)

    arguments = [column_clauses, info]
    thread_column = threading.Thread(target=calc_column_clauses, args=arguments)
    thread_list.append(thread_column)

    arguments = [block_clauses, info]
    thread_block = threading.Thread(target=calc_block_clauses, args=arguments)
    thread_list.append(thread_block)

    for i, thread in enumerate(thread_list):
        print("Thread " + str(i) + " started")
        thread.start()

    for i, thread in enumerate(thread_list):
        thread.join()
        print("Thread " + str(i) + " finish")

    # add clauses in specific order (by length)
    clauses = list()
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
    num_var = length ** 3

    start_line = "p cnf {num_var} {num_clause}\n" \
        .format(num_var=num_var, num_clause=num_clause)

    output_file = info.output_file_complete_absolute()
    start = time.perf_counter()
    write_cnf_file(clauses, output_file, start_line)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to write CNF-File: {time}s".format(time=time_to_encode))
    return info


def encode_parallel_p(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
    length = info.length

    # add clauses for at least one possible value in each cell
    one_per_cell_clauses = list()
    unit_clauses = list()
    distinct_cell_clauses = list()

    row_clauses = list()
    column_clauses = list()

    block_clauses = list()

    thread_list = list()

    # Todo name of thread
    # arguments = [distinct_cell_clauses, field, info, length, one_per_cell_clauses, unit_clauses]
    # thread_cell = threading.Thread(target=calc_cell_clauses, args=arguments)
    # thread_list.append(thread_cell)
    calc_cell_clauses(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info)

    arguments = [row_clauses, info]
    thread_row = multiprocessing.Process(target=calc_row_clauses, args=arguments)
    thread_list.append(thread_row)

    arguments = [column_clauses, info]
    thread_column = multiprocessing.Process(target=calc_column_clauses, args=arguments)
    thread_list.append(thread_column)

    arguments = [block_clauses, info]
    thread_block = multiprocessing.Process(target=calc_block_clauses, args=arguments)
    thread_list.append(thread_block)

    for i, thread in enumerate(thread_list):
        print("Thread " + str(i) + " started")
        thread.start()

    for i, thread in enumerate(thread_list):
        thread.join()
        print("Thread " + str(i) + " finish")

    # add clauses in specific order (by length)
    clauses = list()
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
    num_var = length ** 3

    start_line = "p cnf {num_var} {num_clause}\n" \
        .format(num_var=num_var, num_clause=num_clause)

    output_file = info.output_file_complete_absolute()
    start = time.perf_counter()
    write_cnf_file(clauses, output_file, start_line)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to write CNF-File: {time}s".format(time=time_to_encode))
    return info


def calc_block_clauses(block_clauses, info) -> None:
    start = time.perf_counter()

    block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
    cells_per_block = info.sqrt_of_length
    for block in range(info.length):
        block_pos[0] = int(block / cells_per_block)
        block_pos[1] = block % cells_per_block
        block_clauses.extend(distinct_block_clauses(block_pos, info))

    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish block! Time: " + str(time_to_encode))


def calc_column_clauses(column_clauses, info) -> None:
    start = time.perf_counter()

    for column in range(1, info.length + 1):
        column_clauses.extend(distinct_column_clause(column, info))

    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish column! Time: " + str(time_to_encode))


def calc_row_clauses(row_clauses, info) -> None:
    start = time.perf_counter()

    for row in range(1, info.length + 1):
        row_clauses.extend(distinct_row_clause(row, info))

    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish row! Time: " + str(time_to_encode))


def calc_row_clauses_parallel(row_clauses, info) -> None:
    start = time.perf_counter()

    thread_list = [None] * info.length
    for i in range(1, info.length + 1):
        thread_list[i - 1](threading.Thread(target=distinct_row_clause, args=[i, info]).start())
        row_clauses.extend(distinct_row_clause(i, info))

    for row in range(1, info.length + 1):
        row_clauses.extend(distinct_row_clause(row, info))

    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish row! Time: " + str(time_to_encode))


def calc_cell_clauses(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info) -> None:
    start = time.perf_counter()
    for row_count, row in enumerate(field):
        row_count += 1
        for cell_count, cell in enumerate(row):
            cell_count += 1
            if cell != 0:
                # add known values to unit_clause
                pos = Position(row_count, cell_count, cell)
                u_clause = convert_pos_into_var(pos, info)
                unit_clauses.append(u_clause + " 0\n")
            else:
                # if not known add at least and exactly one value clauses to formula
                clause = one_value_per_cell_clause(row_count, cell_count, info)
                one_per_cell_clauses.append(clause)
                cell_clauses = exactly_one_value_per_cell(row_count, cell_count, info)
                distinct_cell_clauses.extend(cell_clauses)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish cell! Time: " + str(time_to_encode))
