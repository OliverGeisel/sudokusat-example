import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput, PuzzleInfoEncode
from my_solver.oliver.encoder.EncoderList import EncoderList
from my_solver.oliver.encoder.Position import Position
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file, one_template_function_delete, \
    binary_template_function_delete


class Encoder(EncoderList):

    def one_value_per_cell_clause(self, row_count: int, cell_count: int, ) -> str:
        back = self.one_value_per_cell_clause_list(row_count, cell_count)
        return " ".join(str(x) for x in back) + " 0\n"

    def exactly_one_value_per_cell(self, row: int, column: int) -> List[str]:
        return binary_template_function_delete(self.exactly_one_value_per_cell_list(row, column))

    def distinct_row_clause(self, row: int) -> List[str]:
        """

        :param row: row that get clauses
        :return: clauses for the row
        """
        return binary_template_function_delete(self.distinct_row_clause_list(row))

    def only_one_solution_per_row_clause(self, row) -> List[str]:
        return one_template_function_delete(self.only_one_solution_per_row_clause_list(row))

    def only_one_solution_per_column_clause(self, column) -> List[str]:
        return one_template_function_delete(self.only_one_solution_per_column_clause_list(column))

    def distinct_block_clauses(self, block_pos: List[int]) -> List[str]:
        """
        Calculate all clauses for one block in puzzle
        :param block_pos: position of the block in puzzle
        :return: clauses for the block as string
        """
        return binary_template_function_delete(self.distinct_block_clauses_list(block_pos))

    def only_one_solution_per_block_clause(self, block_pos: List[int]) -> List[str]:
        return one_template_function_delete(self.only_one_solution_per_block_clause_list(block_pos))

    def calc_block_clauses(self, block_clauses, block_one_clauses) -> None:
        start = time.perf_counter()
        block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
        blocks_in_row = self.info.sqrt_of_length
        for block in range(self.info.length):
            block_pos[0] = int(block / blocks_in_row)
            block_pos[1] = block % blocks_in_row
            block_clauses.extend(self.distinct_block_clauses(block_pos))
            block_one_clauses.extend(self.only_one_solution_per_block_clause(block_pos))
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

    def calc_row_clauses(self, row_clauses, row_one_clauses) -> None:
        start = time.perf_counter()
        for row in range(1, self.info.length + 1):
            row_clauses.extend(self.distinct_row_clause(row))
            row_one_clauses.extend(self.only_one_solution_per_row_clause(row))
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish row! Time: " + str(time_to_encode))

    def calc_cell_clauses(self, distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field) -> None:
        start = time.perf_counter()
        pos = Position(self.info)
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
                    unit_clauses.append(f"{u_clause} 0\n")
                    for i in range(1, self.info.length + 1):
                        if i == cell:
                            continue
                        pos.set_value(i)
                        unit_clauses.append(f"-{pos.var} 0\n")
                else:
                    # if not known add at least and exactly one value clauses to formula
                    clause = self.one_value_per_cell_clause(row_count, cell_count)
                    one_per_cell_clauses.append(clause)
                    cell_clauses = self.exactly_one_value_per_cell(row_count, cell_count)
                    distinct_cell_clauses.extend(cell_clauses)
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish cell! Time: " + str(time_to_encode))

    def encode(self, field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
        self.info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)

        # add clauses for at least one possible value in each cell
        self.calc_cell_clauses(self.clauses["dist"], self.clauses["one"], self.clauses["unit"], field)
        # add clauses for row distinction
        self.calc_row_clauses(self.clauses["row"], self.clauses["row_one"])
        # add clauses for column  distinction
        self.calc_column_clauses()
        # add clauses for block distinction
        self.calc_block_clauses(self.clauses["block"], self.clauses["block_one"])

        num_clause = sum([len(sub_clause_list) for sub_clause_list in self.clauses.values()])
        num_var = self.info.length * self.info.square_of_length
        start_line = f"p cnf {num_var} {num_clause}\n"
        output_file = self.info.output_file_complete_absolute()

        start = time.perf_counter()
        write_cnf_file(self.clauses, output_file, start_line)
        end = time.perf_counter()
        time_to_encode = end - start
        print("Time to write CNF-File: {time}s".format(time=time_to_encode))
        return self.info
