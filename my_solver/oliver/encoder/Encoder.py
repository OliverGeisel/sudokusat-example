import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput, PuzzleInfoEncode
from my_solver.oliver.encoder.EncoderList import EncoderList
from my_solver.oliver.encoder.Position import Position
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file


class Encoder(EncoderList):
    def distinct_column_clause(self, column: int) -> List[str]:
        """  Create the clauses, that describe, that one column has every value exactly once

        :param column: column that get the clauses.
        :return: clauses for the column
        """
        clauses = self.distinct_column_clause_list(column)
        return [f"-{clause[0]} -{clause[1]} 0\n" for clause in clauses]

    def distinct_row_clause(self, row: int) -> List[str]:
        """

        :param row: row that get clauses
        :return: clauses for the row
        """
        clauses = self.distinct_row_clause_list(row)
        return [f"-{clause[0]} -{clause[1]} 0\n" for clause in clauses]

    def one_value_per_cell_clause(self, row_count: int, cell_count: int, ) -> str:
        back = self.one_value_per_cell_clause_list(row_count, cell_count)
        back = list(map(lambda x: str(x), back))
        back.append("0\n")
        return " ".join(back)

    def exactly_one_value_per_cell(self, row: int, column: int) -> List[str]:
        clauses = self.exactly_one_value_per_cell_list(row, column)
        return [f"-{clause[0]} -{clause[1]} 0\n" for clause in clauses]

    def calc_clauses_for_cell_in_block(self, row_in_block, column_in_block, start_row, start_column) -> List[str]:
        """
        Get Clauses that encode that the cell(start_row,start_column) to be distinct from the other cells
        :param row_in_block:
        :param column_in_block:
        :param start_row:
        :param start_column:
        :return:
        """
        clauses = self.calc_clauses_for_cell_in_block(row_in_block, column_in_block, start_row, start_column)
        return [f"-{clause[0]} -{clause[1]} 0\n" for clause in clauses]

    def distinct_block_clauses(self, block_pos: List[int]) -> List[str]:
        """
        Calculate all clauses for one block in puzzle
        :param block_pos: position of the block in puzzle
        :return: clauses for the block as string
        """
        clauses = self.distinct_block_clauses_list(block_pos)
        return [f"-{clause[0]} -{clause[1]} 0\n" for clause in clauses]

    def calc_block_clauses(self, block_clauses) -> None:
        start = time.perf_counter()
        block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
        blocks_in_row = self.info.sqrt_of_length
        for block in range(self.info.length):
            block_pos[0] = int(block / blocks_in_row)
            block_pos[1] = block % blocks_in_row
            block_clauses.extend(self.distinct_block_clauses(block_pos))
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish block! Time: " + str(time_to_encode))

    def calc_column_clauses(self, column_clauses) -> None:
        start = time.perf_counter()
        for column in range(1, self.info.length + 1):
            column_clauses.extend(self.distinct_column_clause(column))
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish column! Time: " + str(time_to_encode))

    def calc_row_clauses(self, row_clauses) -> None:
        start = time.perf_counter()
        for row in range(1, self.info.length + 1):
            row_clauses.extend(self.distinct_row_clause(row))
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
                    unit_clauses.append("{} 0\n".format(u_clause))
                    for i in range(1, self.info.length + 1):
                        if i == cell:
                            continue
                        pos.set_value(i)
                        unit_clauses.append("-{var} 0\n".format(var=pos.var))
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
        info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)

        one_per_cell_clauses = list()
        unit_clauses = list()
        distinct_cell_clauses = list()

        row_clauses = list()
        column_clauses = list()
        block_clauses = list()
        # add clauses for at least one possible value in each cell
        self.calc_cell_clauses(distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field)
        # add clauses for row distinction
        self.calc_row_clauses(row_clauses)
        # add clauses for column  distinction
        self.calc_column_clauses(column_clauses)
        # add clauses for block distinction
        self.calc_block_clauses(block_clauses)

        clauses = dict()
        clauses["dist"] = distinct_cell_clauses
        clauses["one"] = one_per_cell_clauses
        clauses["unit"] = unit_clauses
        clauses["row"] = row_clauses
        clauses["column"] = column_clauses
        clauses["block"] = block_clauses

        num_clause = sum([len(x) for x in clauses.values()])
        num_var = info.length * info.square_of_length
        start_line = f"p cnf {num_var} {num_clause}\n"
        output_file = info.output_file_complete_absolute()

        start = time.perf_counter()
        write_cnf_file(clauses, output_file, start_line)
        end = time.perf_counter()
        time_to_encode = end - start
        print("Time to write CNF-File: {time}s".format(time=time_to_encode))
        return info
