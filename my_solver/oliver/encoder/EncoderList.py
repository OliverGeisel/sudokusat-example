import time
from collections import defaultdict
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoEncode, PuzzleInfoInput, PuzzleInfo
from my_solver.oliver.encoder.Position import Position
from my_solver.oliver.encoder.WriteCNFFile import write_cnf_file_list_join_interpolation_map, \
    write_cnf_file_from_parts, binary_template_function_delete as binary_template_function, \
    unit_template_function_delete as unit_template_function, \
    one_template_function_delete as one_template_function, write_temp_cnf_file_multiple


class EncoderList:
    large_size = 65

    def __init__(self, info: PuzzleInfo):
        self.info = info
        self.clauses = defaultdict(lambda: list())

    def distinct_column_clause_list(self, column: int) -> List[List[int]]:
        """  Create the clauses, that describe, that one column has every value exactly once

        :param column: column that get the clauses.
        :return: clauses for the column as list
        """
        length = self.info.length
        back = list()
        first_pos = Position(self.info, column=column)
        second_pos = Position(self.info, column=column)
        for upper_row in self.info.values:
            first_pos.set_row(upper_row)
            for lower_row in range(upper_row + 1, length + 1):
                second_pos.set_row(lower_row)
                run1 = first_pos.var
                run2 = second_pos.var
                for value in self.info.values:
                    back.append([run1, run2])
                    run1 += 1
                    run2 += 1
        return back

    def distinct_row_clause_list(self, row: int) -> List[List[int]]:
        """

        :param row: row that get clauses
        :return: clauses for the row
        """
        length = self.info.length
        back = list()
        first_pos = Position(self.info, row, 0)
        second_pos = Position(self.info, row, 0)
        for left_column in self.info.values:
            first_pos.set_column(left_column)
            for right_column in range(left_column + 1, length + 1):
                second_pos.set_column(right_column)
                run1 = first_pos.var
                run2 = second_pos.var
                for value in self.info.values:
                    back.append([run1, run2])
                    run1 += 1
                    run2 += 1
        return back

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

    def only_one_solution_per_row_clause_list(self, row: int) -> List[List[int]]:
        back = list()
        pos = Position(self.info, row)
        for value in self.info.values:
            pos.set_value(value)
            clause = list()
            for column in self.info.values:
                pos.set_column(column)
                clause.append(pos.var)
            back.append(clause)
        return back

    def only_one_solution_per_column_clause_list(self, column: int) -> List[List[int]]:
        back = list()
        pos = Position(self.info, column=column)
        for value in self.info.values:
            pos.set_value(value)
            clause = list()
            for row in self.info.values:
                pos.set_row(row)
                clause.append(pos.var)
            back.append(clause)
        return back

    def only_one_solution_per_block_clause_list(self, block_pos: List[int]) -> List[List[int]]:
        back = list()
        sqrt_of_length = self.info.sqrt_of_length
        start_row = block_pos[0] * sqrt_of_length + 1
        start_column = block_pos[1] * sqrt_of_length + 1
        pos = Position(self.info, start_row, start_column)
        for value in self.info.values:
            pos.set_value(value)
            clause = list()
            for row_in_block in range(start_row, start_row + sqrt_of_length):
                pos.set_row(row_in_block)
                for column_in_block in range(start_column, start_column + sqrt_of_length):
                    pos.set_column(column_in_block)
                    clause.append(pos.var)
            back.append(clause)
        return back

    def calc_clauses_for_cell_in_block_list(self, row_in_block, column_in_block, start_row,
                                            start_column) -> List[List[int]]:
        """
        Get Clauses that encode that the cell(start_row,start_column) to be distinct from the other cells
        :param row_in_block:
        :param column_in_block:
        :param start_row:
        :param start_column:
        :return:
        """
        result = list()
        sqrt_of_length = self.info.sqrt_of_length
        first_cell_pos_in_block = (row_in_block - 1) * self.info.sqrt_of_length + column_in_block
        first_pos = Position(self.info, start_row - 1 + row_in_block, start_column - 1 + column_in_block)
        second_pos = Position(self.info)
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
                    result.append([run1, run2])
                    run1 += 1
                    run2 += 1
        return result

    def distinct_block_clauses_list(self, block_pos: List[int]) -> List[List[int]]:
        """
        Calculate all clauses for one block in puzzle
        :param block_pos: position of the block in puzzle
        :return: clauses for the block as string
        """
        block_clauses = list()
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
                block_clauses.extend(
                    self.calc_clauses_for_cell_in_block_list(row_in_block, column_in_block, start_row, start_column))
        return block_clauses

    def calc_block_clauses_list(self, block_clauses, block_one_clauses) -> None:
        start = time.perf_counter()
        block_pos = [0, 0]  # goes from 0,0 to sgrt(length)-1,sqrt(length)-1
        blocks_in_row = self.info.sqrt_of_length
        for block in range(self.info.length):
            block_pos[0] = int(block / blocks_in_row)
            block_pos[1] = block % blocks_in_row
            block_clauses.extend(self.distinct_block_clauses_list(block_pos))
            block_one_clauses.extend(self.only_one_solution_per_block_clause_list(block_pos))
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish block! Time: " + str(time_to_encode))

    def calc_column_clauses_list(self, column_clauses, column_one_clauses) -> None:
        start = time.perf_counter()
        for column in self.info.values:
            column_clauses.extend(self.distinct_column_clause_list(column))
            column_one_clauses.extend(self.only_one_solution_per_column_clause_list(column))
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish column! Time: " + str(time_to_encode))

    def calc_row_clauses_list(self, row_clauses, row_one_clauses) -> None:
        start = time.perf_counter()
        for row in self.info.values:
            row_clauses.extend(self.distinct_row_clause_list(row))
            row_one_clauses.extend(self.only_one_solution_per_row_clause_list(row))
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish row! Time: " + str(time_to_encode))

    def calc_cell_clauses_list(self, distinct_cell_clauses, one_per_cell_clauses, unit_clauses, field) -> None:
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
                    unit_clauses.append([u_clause, 1])
                    pos.set_value(1)
                    run = pos.var
                    for value in self.info.values:
                        if value == cell:
                            run += 1
                            continue
                        unit_clauses.append([run, 0])
                        run += 1
                else:
                    # if not known add at least and exactly one value clauses to formula
                    clause = self.one_value_per_cell_clause_list(row_count, cell_count)
                    one_per_cell_clauses.append(clause)
                    cell_clauses = self.exactly_one_value_per_cell_list(row_count, cell_count)
                    distinct_cell_clauses.extend(cell_clauses)
        end = time.perf_counter()
        time_to_encode = end - start
        print("Finish cell! Time: " + str(time_to_encode))

    def encode(self, field: List[List[int]], info_input: PuzzleInfoInput) -> PuzzleInfoEncode:
        self.info = PuzzleInfoEncode(info_input.input_file_complete_absolute(), info_input.length, info_input.text)

        # add clauses for at least one possible value in each cell
        self.calc_cell_clauses_list(self.clauses["dist"], self.clauses["one"], self.clauses["unit"], field)
        sum_of_clauses = 0
        if self.info.length >= self.large_size:
            extra = [[self.clauses["dist"], binary_template_function], [self.clauses["one"], one_template_function]]
            sum_of_clauses += write_temp_cnf_file_multiple(self.clauses["unit"], self.info, "cell.txt",
                                                           unit_template_function, *extra)

        # add clauses for row distinction
        self.calc_row_clauses_list(self.clauses["row"], self.clauses["row_one"])
        if self.info.length >= self.large_size:
            sum_of_clauses += write_temp_cnf_file_multiple(self.clauses["row"], self.info, "row.txt",
                                                           binary_template_function,
                                                           [self.clauses["row_one"], one_template_function])

        # add clauses for column  distinction
        self.calc_column_clauses_list(self.clauses["column"], self.clauses["column_one"])
        if self.info.length >= self.large_size:
            sum_of_clauses += write_temp_cnf_file_multiple(self.clauses["column"], self.info, "column.txt",
                                                           binary_template_function,
                                                           [self.clauses["column_one"], one_template_function])
        block_str = list()
        block_one_str = list()
        extra = [block_str, block_one_str]
        # add clauses for block distinction
        self.calc_block_clauses_list(self.clauses["block"], self.clauses["block_one"])
        if self.info.length >= self.large_size:
            block_str.extend(binary_template_function(self.clauses["block"]))
            sum_of_clauses += len(self.clauses["block"])
            del self.clauses["block"]
            block_one_str.extend(one_template_function(self.clauses["block_one"]))
            sum_of_clauses += len(self.clauses["block_one"])
            del self.clauses["block_one"]
            print("Finish block")
        num_clause = sum(
            [len(x) for x in self.clauses.values()]) if self.info.length < self.large_size else sum_of_clauses
        num_var = self.info.length * self.info.square_of_length
        start_line = f"p cnf {num_var} {num_clause}\n"
        output_file = self.info.output_file_complete_absolute()

        start = time.perf_counter()
        if self.info.length >= self.large_size:
            write_cnf_file_from_parts(self.info.temp_files, output_file, start_line, *extra)
        else:
            write_cnf_file_list_join_interpolation_map(self.clauses, output_file, start_line)
        end = time.perf_counter()
        time_to_encode = end - start
        print("Time to write CNF-File: {time}s".format(time=time_to_encode))
        return self.info
