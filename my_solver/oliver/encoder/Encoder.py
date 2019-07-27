import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput, PuzzleInfoEncode
from my_solver.oliver.encoder.EncoderList import EncoderList
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file, one_template_function_delete, \
    binary_template_function_delete, unit_template_function_delete


class Encoder(EncoderList):

    def calc_block_clauses(self) -> None:
        start = time.perf_counter()
        self.calc_block_clauses_list()
        self.clauses["block"] = binary_template_function_delete(self.clauses["block"])
        self.clauses["block_one"] = one_template_function_delete(self.clauses["block_one"])
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish block! Time: " + str(time_to_encode))

    def calc_column_clauses(self) -> None:
        start = time.perf_counter()
        self.calc_column_clauses_list()
        self.clauses["column"] = binary_template_function_delete(self.clauses["column"])
        self.clauses["column_one"] = one_template_function_delete(self.clauses["column_one"])
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish column! Time: " + str(time_to_encode))

    def calc_row_clauses(self) -> None:
        start = time.perf_counter()
        self.calc_row_clauses_list()
        self.clauses["row"] = binary_template_function_delete(self.clauses["row"])
        self.clauses["row_one"] = one_template_function_delete(self.clauses["row_one"])
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish row! Time: " + str(time_to_encode))

    def calc_cell_clauses(self, field) -> None:
        start = time.perf_counter()
        self.calc_cell_clauses_list(field)
        self.clauses["unit"] = unit_template_function_delete(self.clauses["unit"])
        self.clauses["one"] = one_template_function_delete(self.clauses["one"])
        self.clauses["dist"] = binary_template_function_delete(self.clauses["dist"])

        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish cell! Time: " + str(time_to_encode))

    def encode(self, field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
        self.info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)

        # add clauses for at least one possible value in each cell
        self.calc_cell_clauses(field)
        # add clauses for row distinction
        self.calc_row_clauses()
        # add clauses for column  distinction
        self.calc_column_clauses()
        # add clauses for block distinction
        self.calc_block_clauses()

        num_clause = sum([len(sub_clause_list) for sub_clause_list in self.clauses.values()])
        num_var = self.info.length * self.info.square_of_length
        start_line = f"p cnf {num_var} {num_clause}\n"
        output_file = self.info.output_file_name

        start = time.perf_counter()
        write_cnf_file(self.clauses, output_file, start_line)
        end = time.perf_counter()
        time_to_encode = end - start
        print("Time to write CNF-File: {time}s".format(time=time_to_encode))
        return self.info
