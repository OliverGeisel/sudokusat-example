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

    def distinct_column_clause_list(self, column: int) -> None:
        """  Create the clauses, that describe, that one column has every value exactly once

        :param column: column that get the clauses.
        :return: clauses for the column as list
        """
        length = self.info.length
        to_append = self.clauses["column"]
        first_pos = Position(self.info, column=column)
        second_pos = Position(self.info, 2, column=column)
        run1 = first_pos.var
        run2 = second_pos.var
        step = self.info.square_of_length
        for upper_row in self.info.values:
            for lower_row in range(upper_row + 1, length + 1):
                for value in self.info.values:
                    to_append.append([run1, run2])
                    run1 += 1
                    run2 += 1
                run1 -= length
                run2 -= length
                run2 += step
            run2 -= step * (length - upper_row - 1)
            run1 += step       


    def distinct_row_clause_list(self, row: int) -> None:
        """

        :param row: row that get clauses
        :return: clauses for the row
        """
        length = self.info.length
        to_append = self.clauses["row"]
        first_pos = Position(self.info, row)
        second_pos = Position(self.info, row, 2)
        run1 = first_pos.var
        run2 = second_pos.var
        for left_column in self.info.values:
            for right_column in range(left_column + 1, length + 1):
                for value in self.info.values:
                    to_append.append([run1, run2])
                    run1 += 1
                    run2 += 1
                run1 -= length
            run2 -= length * (length - left_column - 1)
            run1 += length

    def one_value_per_cell_clause_list(self, row_count: int, cell_count: int) -> List[int]:
        literals = list()
        pos = Position(self.info, row_count, cell_count)
        run = pos.var
        for value in self.info.values:
            literals.append(run)
            run += 1
        return literals

    def exactly_one_value_per_cell_list(self, row: int, column: int) -> List[List[int]]:
        exactly_one_value_per_cell_clause = list()
        first_pos = Position(self.info, row, column)
        second_pos = Position(self.info, row, column)
        run1 = first_pos.var
        for value in self.info.values:
            run2 = second_pos.var + value
            for other in range(value + 1, self.info.length + 1):
                clause = [run1, run2]
                exactly_one_value_per_cell_clause.append(clause)
                run2 += 1
            run1 += 1
        return exactly_one_value_per_cell_clause

    def only_one_solution_per_row_clause_list(self, row: int) -> None:
        step = self.info.length
        pos = Position(self.info, row)
        to_append = self.clauses["row_one"]
        for value in self.info.values:
            pos.set_value(value)
            run = pos.var
            clause = list()
            for column in self.info.values:
                clause.append(run)
                run += step
            to_append.append(clause)

    def only_one_solution_per_column_clause_list(self, column: int) -> None:
        pos = Position(self.info, column=column)
        step = self.info.square_of_length
        to_append = self.clauses["column_one"]
        for value in self.info.values:
            pos.set_value(value)
            clause = list()
            run = pos.var
            for row in self.info.values:
                clause.append(run)
                run += step
            to_append.append(clause)

    def only_one_solution_per_block_clause_list(self, block_pos: List[int]) -> List[List[int]]:
        back = list()
        sqrt_of_length = self.info.sqrt_of_length
        start_row = block_pos[0] * sqrt_of_length + 1
        start_column = block_pos[1] * sqrt_of_length + 1
        pos = Position(self.info, start_row, start_column)
        step = self.info.square_of_length
        for value in self.info.values:
            pos.set_value(value)
            clause = list()
            for row_in_block in range(start_row, start_row + sqrt_of_length):
                pos.set_row(row_in_block)
                run = pos.var
                for column_in_block in range(start_column, start_column + sqrt_of_length):
                    clause.append(run)
                    run += step
            back.append(clause)
        return back

    def calc_clauses_for_cell_in_block_list(self, row_in_block, column_in_block, start_row,
                                            start_column) -> None:
        """
        Get Clauses that encode that the cell(start_row,start_column) to be distinct from the other cells
        :param row_in_block:
        :param column_in_block:
        :param start_row:
        :param start_column:
        :return:
        """
        sqrt_of_length = self.info.sqrt_of_length
        first_cell_pos_in_block = (row_in_block - 1) * self.info.sqrt_of_length + column_in_block
        first_pos = Position(self.info, start_row - 1 + row_in_block, start_column - 1 + column_in_block)
        second_pos = Position(self.info)
        to_append = self.clauses["block"]
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
                run1 = first_pos.var
                run2 = second_pos.var
                for value in self.info.values:
                    to_append.append([run1, run2])
                    run1 += 1
                    run2 += 1

    def distinct_block_clauses_list(self, block_pos: List[int]) -> None:
        """
        Calculate all clauses for one block in puzzle
        :param block_pos: position of the block in puzzle
        :return: clauses for the block as string
        """
        # for 1.1 1 will reached by    1.2 1.3 are not 1
        #                          2.1 2.2 2.3
        #                          3.1 3.2 3.3
        # same for 2 to 9
        # this continue with 1.2 2 by ...
        sqrt_of_length = self.info.sqrt_of_length
        start_row = block_pos[0] * sqrt_of_length + 1
        start_column = block_pos[1] * sqrt_of_length + 1
        # for one pos in block
        for line in range(start_row, start_row + sqrt_of_length - 1):
            for cell in range(start_column, start_column + sqrt_of_length):
                row_in_block = (line - 1) % sqrt_of_length + 1
                column_in_block = (cell - 1) % sqrt_of_length + 1
                self.calc_clauses_for_cell_in_block_list(row_in_block, column_in_block, start_row, start_column)

    def calc_block_clauses_list(self) -> None:
        start = time.perf_counter()
        block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
        blocks_in_row = self.info.sqrt_of_length
        for block in range(self.info.length):
            block_pos[0] = int(block / blocks_in_row)
            block_pos[1] = block % blocks_in_row
            self.distinct_block_clauses_list(block_pos)
            self.only_one_solution_per_block_clause_list(block_pos)
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
        pos = Position(self.info)
        append_to_unit = self.clauses["unit"]
        append_to_one = self.clauses["one"]
        append_to_dist = self.clauses["dist"]
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
                    append_to_unit.append([u_clause, 1])
                    u_clause -= (cell - 1)
                    for value in self.info.values:
                        if value == cell:
                            pass
                        else:
                            append_to_unit.append([u_clause, 0])
                        u_clause += 1
                else:
                    # if not known add at least and exactly one value clauses to formula
                    clause = self.one_value_per_cell_clause_list(row_count, cell_count)
                    append_to_one.append(clause)
                    cell_clauses = self.exactly_one_value_per_cell_list(row_count, cell_count)
                    append_to_dist.extend(cell_clauses)
        end = time.perf_counter()
        time_to_encode = end - start
        print(f"Finish cell! Time: {time_to_encode}s", file=sys.stderr)

    def encode(self, field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
        self.info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)
        # add clauses for at least one possible value in each cell
        self.calc_cell_clauses_list(field)
        field.clear()
        sum_of_clauses = 0
        output_file = self.info.output_file_name
        with open(output_file, "w") as output:
            output_line = list()
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
                write_cnf_file_from_parts(self.info.temp_files, output_file, start_line, *extra)
            else:
                output_line.insert(0, start_line)
                output.writelines(output_line)
                # with open(output_file, "w")as output_file:
                #     lines_to_write = [start_line]
                #     lines_to_write.extend(solution_strs)
                #     write = ''.join(lines_to_write)
                #     output_file.write(write)
                #  write_cnf_file_list_join_interpolation_map(self.clauses, output_file, start_line)
        end = time.perf_counter()
        time_to_encode = end - start
        print(f"Time to write CNF-File: {time_to_encode}s", file=sys.stderr)
        return self.info
