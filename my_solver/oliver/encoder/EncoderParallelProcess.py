import multiprocessing
import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput, PuzzleInfoEncode
from my_solver.oliver.encoder.EncoderList import distinct_column_clause_list, distinct_block_clauses_list, \
    distinct_row_clause_list, one_value_per_cell_clause_list, exactly_one_value_per_cell_list
from my_solver.oliver.encoder.Position import Position
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file_list_join_interpolation_map


def encode(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
    info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
    length = info.length

    thread_list = list()
    clauses = dict()

    p_one, one_per_cell_clauses = multiprocessing.Pipe()
    p_unit, unit_clauses = multiprocessing.Pipe()
    p_dist, distinct_cell_clauses = multiprocessing.Pipe()

    p_row, row_clauses = multiprocessing.Pipe()
    p_column, column_clauses = multiprocessing.Pipe()
    p_block, block_clauses = multiprocessing.Pipe()

    # Todo name of thread
    arguments = [distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info]
    thread_cell = multiprocessing.Process(target=calc_cell_clauses_p, args=arguments)
    thread_list.append(thread_cell)

    arguments = [row_clauses, info]
    thread_row = multiprocessing.Process(target=calc_row_clauses_p, args=arguments)
    thread_list.append(thread_row)

    arguments = [column_clauses, info]
    thread_column = multiprocessing.Process(target=calc_column_clauses_p, args=arguments)
    thread_list.append(thread_column)

    arguments = [block_clauses, info]
    thread_block = multiprocessing.Process(target=calc_block_clauses_p, args=arguments)
    thread_list.append(thread_block)

    for i, thread in enumerate(thread_list):
        print("Thread " + str(i) + " started")
        thread.start()

    # add clauses in specific order (by length)
    clauses["dist"] = p_dist.recv()
    clauses["one"] = p_one.recv()
    clauses["unit"] = p_unit.recv()

    clauses["row"] = p_row.recv()
    clauses["column"] = p_column.recv()
    clauses["block"] = p_block.recv()

    num_clause = sum([len(x) for x in clauses.values()])
    num_var = info.length * info.square_of_length
    start_line = f"p cnf {num_var} {num_clause}\n"
    output_file = info.output_file_complete_absolute()
    start = time.perf_counter()
    write_cnf_file_list_join_interpolation_map(clauses, output_file, start_line)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to write CNF-File: {time}s".format(time=time_to_encode))
    return info


def calc_block_clauses_p(block_clauses, info) -> None:
    start = time.perf_counter()
    back = list()
    block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
    blocks_in_row = info.sqrt_of_length
    for block in range(info.length):
        block_pos[0] = int(block / blocks_in_row)
        block_pos[1] = block % blocks_in_row
        back.extend(distinct_block_clauses_list(block_pos, info))
    block_clauses.send(back)
    block_clauses.close()
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish block! Time: " + str(time_to_encode))


def calc_column_clauses_p(column_clauses, info) -> None:
    start = time.perf_counter()
    back = list()
    for column in range(1, info.length + 1):
        back.extend(distinct_column_clause_list(column, info))
    column_clauses.send(back)
    column_clauses.close()
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish column! Time: " + str(time_to_encode))


def calc_row_clauses_p(row_clauses, info) -> None:
    start = time.perf_counter()
    back = list()
    for row in range(1, info.length + 1):
        back.extend(distinct_row_clause_list(row, info))
    row_clauses.send(back)
    row_clauses.close()
    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish row! Time: " + str(time_to_encode))


def calc_cell_clauses_p(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field, info) -> None:
    start = time.perf_counter()
    unit_clauses_temp = list()
    one_per_cell_clauses_temp = list()
    distinct_cell_clauses_temp = list()

    for row_count, row in enumerate(field):
        row_count += 1
        for cell_count, cell in enumerate(row):
            cell_count += 1
            if cell != 0:
                # add known values to unit_clause
                pos = Position(info, row_count, cell_count, cell)
                u_clause = pos.var
                unit_clauses_temp.append("{} 0\n".format(u_clause))
                for i in range(1, info.length + 1):
                    if i == cell:
                        continue
                    pos.set_value(i)
                    unit_clauses_temp.append("-{var} 0\n".format(var=pos.var))
            else:
                # if not known add at least and exactly one value clauses to formula
                clause = one_value_per_cell_clause_list(row_count, cell_count, info)
                one_per_cell_clauses_temp.append(clause)
                cell_clauses = exactly_one_value_per_cell_list(row_count, cell_count, info)
                distinct_cell_clauses_temp.extend(cell_clauses)
    distinct_cell_clauses.send(distinct_cell_clauses_temp)
    one_per_cell_clauses.send(one_per_cell_clauses_temp)
    unit_clauses.send(unit_clauses_temp)
    distinct_cell_clauses.close()
    one_per_cell_clauses.close()
    unit_clauses.close()

    end = time.perf_counter()
    time_to_encode = end - start
    print("Finish cell! Time: " + str(time_to_encode))
