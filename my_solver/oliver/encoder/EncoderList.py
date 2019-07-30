import itertools as it
import os
import sys
import time
from collections import defaultdict
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoEncode, PuzzleInfoInput, PuzzleInfo
from my_solver.oliver.encoder.Position import Position
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file_from_parts, \
    binary_template_function_delete as binary_template_function, \
    unit_template_function_delete as unit_template_function, \
    one_template_function_delete as one_template_function, write_temp_cnf_file_multiple


class EncoderList:
    large_size = 101

    def __init__(self, info: PuzzleInfo):
        self.info = info
        self.clauses = defaultdict(lambda: list())

    def one_value_per_cell_clause_list(self, row_count: int, cell_count: int) -> None:
        pos = Position(self.info, row_count, cell_count)
        run = pos.var
        self.clauses["one"].append([run + value for value in self.info.values_zero])

    def only_one_value_per_cell_list(self, row: int, column: int) -> None:
        first_pos = Position(self.info, row, column)
        run1 = first_pos.var
        vars_for_cell = range(run1, run1 + self.info.length)
        self.clauses["dist"].extend(it.combinations(vars_for_cell, 2))

    def distinct_row_clause_list(self, row: int) -> None:
        """

        :param row: row that get clauses
        :return: clauses for the row
        """
        length = self.info.length
        to_append = self.clauses["row"]
        first_pos = Position(self.info, row)
        run1 = first_pos.var
        for value in self.info.values_zero:
            vars_in_row = range(run1 + value, run1 + self.info.square_of_length + value, length)
            to_append.extend(it.combinations(vars_in_row, 2))

    def distinct_column_clause_list(self, column: int) -> None:
        """  Create the clauses, that describe, that one column has every value exactly once

        :param column: column that get the clauses.
        :return: clauses for the column as list
        """
        length = self.info.length
        to_append = self.clauses["column"]
        first_pos = Position(self.info, column=column)
        run1 = first_pos.var
        for value in self.info.values_zero:
            vars_in_row = range(run1 + value, run1 + self.info.square_of_length * length + value,
                                self.info.square_of_length)
            to_append.extend(it.combinations(vars_in_row, 2))

    def only_one_solution_per_row_clause_list(self, row: int) -> None:
        step = self.info.length
        pos = Position(self.info, row)
        to_append = self.clauses["row_one"]
        clause = list()
        run = pos.var
        for column in self.info.values:
            clause.append(run)
            run += step
        for value in self.info.values_zero:
            to_append.append([variable + value for variable in clause])

    def only_one_solution_per_column_clause_list(self, column: int) -> None:
        pos = Position(self.info, column=column)
        step = self.info.square_of_length
        to_append = self.clauses["column_one"]
        clause = list()
        run = pos.var
        for row in self.info.values:
            clause.append(run)
            run += step
        for value in self.info.values_zero:
            to_append.append([variable + value for variable in clause])

    def calc_clauses_for_cell_in_block_list(self, row_in_block, column_in_block, start_row_of_block,
                                            start_column_of_block) -> None:
        """
        Get Clauses that encode that the cell(start_row,start_column) to be distinct from the other cells
        :param row_in_block:
        :param column_in_block:
        :param start_row_of_block:
        :param start_column_of_block:
        :return:
        """
        sqrt_of_length = self.info.sqrt_of_length
        first_cell_pos_in_block = (row_in_block - 1) * self.info.sqrt_of_length + column_in_block
        first_pos = Position(self.info, start_row_of_block - 1 + row_in_block,
                             start_column_of_block - 1 + column_in_block).var
        to_append = self.clauses["block"]
        vars_in_block = list()
        step_row = self.info.square_of_length
        step_column = self.info.length
        run = (start_row_of_block - 1) * step_row + step_column * (start_column_of_block - 1) + 1
        current_cell_pos_in_block = 1
        # start with second row and got to last row of block
        for current_row in range(start_row_of_block, start_row_of_block + sqrt_of_length):
            if current_row > start_row_of_block + row_in_block - 1:
                # from first column to last column in block
                for current_column in range(start_column_of_block, start_column_of_block + sqrt_of_length):
                    # skip if cell is behind the start_cell or cell is in same column
                    if current_cell_pos_in_block <= first_cell_pos_in_block or \
                            current_column == start_column_of_block - 1 + column_in_block:
                        pass
                    else:
                        vars_in_block.append(run)
                    # next column
                    run += step_column
                    current_cell_pos_in_block += 1
                # next row
                run += step_row - step_column * sqrt_of_length
            else:
                run += step_row
                current_cell_pos_in_block += sqrt_of_length
        # after get all vars
        clauses = [[first_pos, variable] for variable in vars_in_block]
        for value in self.info.values_zero:
            to_append.extend([[clause[0] + value, clause[1] + value] for clause in clauses])

    def distinct_and_only_one_for_block_clauses_list(self, start_row, start_column) -> None:
        """
        Calculate all clauses for one block in puzzle
        :param start_column:
        :param start_row:
        :return: clauses for the block as string
        """
        # for 1.1 1 will reached by    1.2 1.3 are not 1
        #                          2.1 2.2 2.3
        #                          3.1 3.2 3.3
        # same for 2 to 9
        # this continue with 1.2 2 by ...
        sqrt_of_length = self.info.sqrt_of_length
        step_row = self.info.square_of_length
        step_column = self.info.length
        run = Position(self.info, start_row, start_column).var
        clause = list()
        to_append = self.clauses["block_one"]
        # for one pos in block
        for line in range(start_row, start_row + sqrt_of_length):
            row_in_block = (line - 1) % sqrt_of_length + 1
            for cell in range(start_column, start_column + sqrt_of_length):
                if line < start_row + sqrt_of_length:
                    column_in_block = (cell - 1) % sqrt_of_length + 1
                    self.calc_clauses_for_cell_in_block_list(row_in_block, column_in_block, start_row, start_column)
                clause.append(run)
                run += step_column
            run += step_row - step_column * sqrt_of_length
        for value in self.info.values_zero:
            to_append.append([variable + value for variable in clause])

    def calc_block_clauses_list(self) -> None:
        start = time.perf_counter()
        blocks_in_row = self.info.sqrt_of_length
        for block in range(self.info.length):
            start_row = int(block / blocks_in_row) * self.info.sqrt_of_length + 1
            start_column = (block % blocks_in_row) * self.info.sqrt_of_length + 1
            self.distinct_and_only_one_for_block_clauses_list(start_row, start_column)
        end = time.perf_counter()
        time_to_encode = end - start
        print(f"Finish block! Time: {time_to_encode}s", file=sys.stderr)

    def calc_column_clauses_list(self) -> None:
        start = time.perf_counter()
        for column in self.info.values:
            self.distinct_column_clause_list(column)
            self.only_one_solution_per_column_clause_list(column)
        end = time.perf_counter()
        time_to_encode = end - start
        print(f"Finish column! Time: {time_to_encode}s", file=sys.stderr)

    def calc_row_clauses_list(self) -> None:
        start = time.perf_counter()
        for row in self.info.values:
            self.distinct_row_clause_list(row)
            self.only_one_solution_per_row_clause_list(row)
        end = time.perf_counter()
        time_to_encode = end - start
        print(f"Finish row! Time: {time_to_encode}s", file=sys.stderr)

    def calc_cell_clauses_list(self, field) -> None:
        start = time.perf_counter()
        run = 0
        step_column = self.info.length
        append_to_unit = self.clauses["unit"]
        for row_count, row in enumerate(field):
            row_count += 1
            for cell_count, cell in enumerate(row):
                cell_count += 1
                if cell != 0:
                    # add known values to unit_clause
                    for value in self.info.values:
                        run += 1
                        append_to_unit.append([run, 1 if value == cell else 0])
                else:
                    # if not known add at least and exactly one value clauses to formula
                    self.one_value_per_cell_clause_list(row_count, cell_count)
                    self.only_one_value_per_cell_list(row_count, cell_count)
                    run += step_column
        end = time.perf_counter()
        time_to_encode = end - start
        print(f"Finish cell! Time: {time_to_encode}s", file=sys.stderr)

    def encode(self, field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
        self.info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
        # add clauses for at least one possible value in each cell

        sum_of_clauses = 0
        output_file_path = os.path.join("tmp", self.info.task, self.info.output_file_name)
        try:
            if not os.path.exists("tmp"):
                os.mkdir("tmp")
            sub_dir = os.path.join("tmp", self.info.task)
            if not os.path.exists(sub_dir):
                os.mkdir(sub_dir)
        except FileExistsError:
            pass

        with open(output_file_path, "w") as output:
            output_line = list()

            # add clauses for one cell
            self.calc_cell_clauses_list(field)
            field.clear()
            if self.info.length >= self.large_size:
                extra = [[self.clauses["dist"], binary_template_function], [self.clauses["one"], one_template_function]]
                sum_of_clauses += write_temp_cnf_file_multiple(self.clauses["unit"], self.info, "cell.txt",
                                                               unit_template_function, *extra)
            else:
                sum_of_clauses += len(self.clauses["dist"]) + len(self.clauses["one"]) + len(self.clauses["unit"])
                output_line.append("".join(binary_template_function(self.clauses["dist"])))
                output_line.append("".join(unit_template_function(self.clauses["unit"])))
                output_line.append("".join(one_template_function(self.clauses["one"])))

            # add clauses for row
            self.calc_row_clauses_list()
            if self.info.length >= self.large_size:
                sum_of_clauses += write_temp_cnf_file_multiple(self.clauses["row"], self.info, "row.txt",
                                                               binary_template_function,
                                                               [self.clauses["row_one"], one_template_function])
            else:
                sum_of_clauses += len(self.clauses["row"]) + len(self.clauses["row_one"])
                output_line.append("".join(binary_template_function(self.clauses["row"])))
                output_line.append("".join(one_template_function(self.clauses["row_one"])))

            # add clauses for column
            self.calc_column_clauses_list()
            if self.info.length >= self.large_size:
                sum_of_clauses += write_temp_cnf_file_multiple(self.clauses["column"], self.info, "column.txt",
                                                               binary_template_function,
                                                               [self.clauses["column_one"], one_template_function])
            else:
                sum_of_clauses += len(self.clauses["column"]) + len(self.clauses["column_one"])
                output_line.append("".join(binary_template_function(self.clauses["column"])))
                output_line.append("".join(one_template_function(self.clauses["column_one"])))

            # add clauses for block
            block_str = list()
            block_one_str = list()
            extra = [block_str, block_one_str]
            self.calc_block_clauses_list()
            if self.info.length >= self.large_size:
                sum_of_clauses += len(self.clauses["block"])
                block_str.extend(binary_template_function(self.clauses["block"]))
                del self.clauses["block"]
                sum_of_clauses += len(self.clauses["block_one"])
                block_one_str.extend(one_template_function(self.clauses["block_one"]))
                del self.clauses["block_one"]
                print("Finish block", file=sys.stderr)
            else:
                sum_of_clauses += len(self.clauses["block"]) + len(self.clauses["block_one"])
                output_line.append("".join(binary_template_function(self.clauses["block"])))
                output_line.append("".join(one_template_function(self.clauses["block_one"])))

            num_var = self.info.length * self.info.square_of_length
            start_line = f"p cnf {num_var} {sum_of_clauses}\n"

            start = time.perf_counter()
            if self.info.length >= self.large_size:
                write_cnf_file_from_parts(self.info.temp_files, output_file_path, start_line, *extra)
            else:
                output_line.insert(0, start_line)
                output.write("".join(output_line))
        end = time.perf_counter()
        time_to_encode = end - start
        print(f"Time to write CNF-File: {time_to_encode}s", file=sys.stderr)
        return self.info
