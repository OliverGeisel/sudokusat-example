import threading
import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput, PuzzleInfoEncode
from my_solver.oliver.encoder.Position import Position


def convert_pos_into_var(pos: Position) -> int:
    """
    Convert a position of the sudoku-field into a variable

    Example 5. row 4. column and value 9 in 9x9 Puzzle is in old 549
    New it is 4*9*9+3*9+9

    :param pos:
    :return:
    """
    var = (pos.row - 1) * pos.info.square_of_length \
          + (pos.column - 1) * pos.info.length \
          + pos.value
    return var


def convert_pos_int_var_as_str(pos: Position) -> str:
    return str(convert_pos_into_var(pos))


def convert_var_into_pos(var: int, info: PuzzleInfoEncode) -> Position:
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


def positions_to_str(first_pos: Position, second_pos: Position, first_positive: bool = False,
                     second_positive: bool = False) -> str:
    if not first_positive and not second_positive:
        positions_to_str_negative(first_pos, second_pos)
    sign1 = "" if first_positive else "-"
    sign2 = "" if second_positive else "-"
    return "{sign1}{var1} {sign2}{var2} 0\n".format(sign1=sign1, var1=first_pos.var,
                                                    sign2=sign2, var2=second_pos.var)


def positions_to_str_negative(first_pos: Position, second_pos: Position) -> str:
    return "-{var1} -{var2} 0\n".format(var1=first_pos.var,
                                        var2=second_pos.var)


def distinct_column_clause(column: int, info: PuzzleInfoEncode) -> List[str]:
    """  Create the clauses, that describe, that one column has every value exactly once

    :param column: column that get the clauses.
    :param info: number of values from 1 to length
    :return: clauses for the column
    """
    # TODO MAP()
    back = list()
    clauses = distinct_column_clause_list(column, info)
    for clause in clauses:
        back.append("-%s -%s 0\n" % (clause[0], clause[1]))
    return back


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


def distinct_row_clause(row: int, info: PuzzleInfoEncode) -> List[str]:
    """

    :param row: row that get clauses
    :param info: number of values from 1 to length
    :return: clauses for the row
    """
    back = list()
    clauses = distinct_row_clause_list(row, info)
    # TODO MAP()
    for clause in clauses:
        back.append("-%s -%s 0\n" % (clause[0], clause[1]))
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


def one_value_per_cell_clause(row_count: int, cell_count: int, info: PuzzleInfoEncode) -> str:
    back = one_value_per_cell_clause_list(row_count, cell_count, info)
    back.append("0\n")
    return " ".join(str(back))


def one_value_per_cell_clause_list(row_count: int, cell_count: int, info: PuzzleInfoEncode) -> List[int]:
    literals = list()
    pos = Position(info, row_count, cell_count)
    for i in range(1, info.length + 1):
        pos.set_value(i)
        literals.append(pos.var)
    return literals


def exactly_one_value_per_cell(row: int, column: int, info: PuzzleInfoEncode) -> List[str]:
    back = list()
    clauses = exactly_one_value_per_cell_list(row, column, info)
    # TODO MAP()
    for clause in clauses:
        back.append("-%s -%s 0\n" % (clause[0], clause[1]))
    return back


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


def calc_clauses_for_cell_in_block(row_in_block, column_in_block, info: PuzzleInfoEncode, start_row, start_column) -> \
        List[str]:
    """
    Get Clauses that encode that the cell(start_row,start_column) to be distinct from the other cells
    :param row_in_block:
    :param column_in_block:
    :param info:
    :param start_row:
    :param start_column:
    :return:
    """
    back = list()
    clauses = calc_clauses_for_cell_in_block(row_in_block, column_in_block, info, start_row, start_column)
    # TODO MAP()
    for clause in clauses:
        back.append("-%s -%s 0\n" % (clause[0], clause[1]))
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


def distinct_block_clauses(block_pos: List[int], info: PuzzleInfoEncode) -> List[str]:
    """
    Calculate all clauses for one block in puzzle
    :param block_pos: position of the block in puzzle
    :param info: Information about the puzzle
    :return: clauses for the block as string
    """
    back = list()
    clauses = distinct_block_clauses_list(block_pos, info)
    # TODO MAP()
    for clause in clauses:
        back.append("-%s -%s 0\n" % (clause[0], clause[1]))
    return back


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


def encode(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
    length = info.length

    one_per_cell_clauses = list()
    unit_clauses = list()
    distinct_cell_clauses = list()

    row_clauses = list()
    column_clauses = list()
    block_clauses = list()
    # add clauses for at least one possible value in each cell
    calc_cell_clauses(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info)
    # add clauses for row distinction
    calc_row_clauses(row_clauses, info)
    # add clauses for column  distinction
    calc_column_clauses(column_clauses, info)
    # add clauses for block distinction
    calc_block_clauses(block_clauses, info)

    clauses = dict()
    clauses["dist"] = distinct_cell_clauses
    clauses["one"] = one_per_cell_clauses
    clauses["unit"] = unit_clauses
    clauses["row"] = row_clauses
    clauses["column"] = column_clauses
    clauses["block"] = block_clauses

    num_clause = sum(map(lambda x: len(x), clauses.values()))
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


def encode_list(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)

    one_per_cell_clauses = list()
    unit_clauses = list()
    distinct_cell_clauses = list()

    row_clauses = list()
    column_clauses = list()
    block_clauses = list()
    # add clauses for at least one possible value in each cell
    calc_cell_clauses_list(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info)
    # add clauses for row distinction
    calc_row_clauses_list(row_clauses, info)
    # add clauses for column  distinction
    calc_column_clauses_list(column_clauses, info)
    # add clauses for block distinction
    calc_block_clauses_list(block_clauses, info)

    clauses = dict()
    clauses["dist"] = distinct_cell_clauses
    clauses["one"] = one_per_cell_clauses
    clauses["unit"] = unit_clauses
    clauses["row"] = row_clauses
    clauses["column"] = column_clauses
    clauses["block"] = block_clauses

    num_clause = sum(map(lambda x: len(x), clauses.values()))
    num_var = info.length * info.square_of_length
    start_line = "p cnf {num_var} {num_clause}\n" \
        .format(num_var=num_var, num_clause=num_clause)
    output_file = info.output_file_complete_absolute()

    start = time.perf_counter()
    write_cnf_file_list(clauses, output_file, start_line)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to write CNF-File: {time}s".format(time=time_to_encode))
    return info


def encode_parallel(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
    length = info.length

    one_per_cell_clauses = list()
    unit_clauses = list()
    distinct_cell_clauses = list()

    row_clauses = list()
    column_clauses = list()
    block_clauses = list()

    thread_list = list()

    # Todo name of thread
    arguments = [distinct_cell_clauses, field, info, length, one_per_cell_clauses, unit_clauses]
    thread_cell = threading.Thread(target=calc_cell_clauses, args=arguments)
    thread_list.append(thread_cell)

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

    clauses = dict()
    thread_cell.join()
    clauses["dist"] = distinct_cell_clauses
    clauses["one"] = one_per_cell_clauses
    clauses["unit"] = unit_clauses

    thread_row.join()
    clauses["row"] = row_clauses
    thread_column.join()
    clauses["column"] = column_clauses
    thread_block.join()
    clauses["block"] = block_clauses

    num_clause = sum(map(lambda x: len(x), clauses.values()))
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


def write_cnf_file(clauses, output_file_name, start_line):
    with open(output_file_name, "w")as output_file:
        output_file.write(start_line)
        output_file.writelines(clauses["unit"])
        output_file.writelines(clauses["dist"])

        output_file.writelines(clauses["row"])
        output_file.writelines(clauses["column"])
        output_file.writelines(clauses["block"])

        output_file.writelines(clauses["one"])


def write_cnf_file_list(clauses, output_file_name, start_line):
    with open(output_file_name, "w")as output_file:
        output_file.write(start_line)
        lines_to_write = list()
        for clause in clauses["unit"]:
            lines_to_write.append("%s%s 0\n" % (("" if clause[1] else "-"), clause[0]))
        output_file.writelines(lines_to_write)
        lines_to_write.clear()
        for clause in clauses["dist"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        output_file.writelines(lines_to_write)
        lines_to_write.clear()
        for clause in clauses["row"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        output_file.writelines(lines_to_write)
        lines_to_write.clear()
        for clause in clauses["column"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        output_file.writelines(lines_to_write)
        lines_to_write.clear()
        for clause in clauses["block"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        output_file.writelines(lines_to_write)

        lines_to_write.clear()
        for clause in clauses["one"]:
            clause.append("0\n")
            clause = list(map(lambda x: str(x), clause))
            lines_to_write.append(" ".join(clause))
        output_file.writelines(lines_to_write)


def calc_block_clauses(block_clauses, info) -> None:
    start = time.perf_counter()
    block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
    blocks_in_row = info.sqrt_of_length
    for block in range(info.length):
        block_pos[0] = int(block / blocks_in_row)
        block_pos[1] = block % blocks_in_row
        block_clauses.extend(distinct_block_clauses(block_pos, info))
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish block! Time: " + str(time_to_encode))


def calc_block_clauses_list(block_clauses, info) -> None:
    start = time.perf_counter()
    block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
    blocks_in_row = info.sqrt_of_length
    for block in range(info.length):
        block_pos[0] = int(block / blocks_in_row)
        block_pos[1] = block % blocks_in_row
        block_clauses.extend(distinct_block_clauses_list(block_pos, info))
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


def calc_column_clauses_list(column_clauses, info) -> None:
    start = time.perf_counter()
    for column in range(1, info.length + 1):
        column_clauses.extend(distinct_column_clause_list(column, info))
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


def calc_row_clauses_list(row_clauses, info) -> None:
    start = time.perf_counter()
    for row in range(1, info.length + 1):
        row_clauses.extend(distinct_row_clause_list(row, info))
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish row! Time: " + str(time_to_encode))




def calc_cell_clauses(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info) -> None:
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
                u_clause = convert_pos_into_var(pos)
                unit_clauses.append("{} 0\n".format(u_clause))
                for i in range(1, info.length + 1):
                    if i == cell:
                        continue
                    pos.set_value(i)
                    unit_clauses.append("-{var} 0\n".format(var=convert_pos_into_var(pos)))
            else:
                # if not known add at least and exactly one value clauses to formula
                clause = one_value_per_cell_clause(row_count, cell_count, info)
                one_per_cell_clauses.append(clause)
                cell_clauses = exactly_one_value_per_cell(row_count, cell_count, info)
                distinct_cell_clauses.extend(cell_clauses)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish cell! Time: " + str(time_to_encode))


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


