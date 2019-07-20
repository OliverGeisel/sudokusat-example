import threading
import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoEncode, PuzzleInfoInput
from my_solver.oliver.encoder.Encoder import calc_cell_clauses, calc_row_clauses, calc_column_clauses, \
    calc_block_clauses
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file


def encode(field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
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
