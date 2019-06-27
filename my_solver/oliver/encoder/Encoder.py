from copy import copy

from my_solver.oliver.reader.Input import input_source


def one_value_per_cell_clause(line_count: int, cell_count: int, length: int) -> str:
    back = ""
    for i in range(length):
        back += str(line_count+1) + str(cell_count+1) + str(i+1) + " "
    back += "0\n"
    return back


def encode(input: str) -> str:
    field, length = input_source(input)
    file_name = input.split("/")[-1]
    output_file_name = copy(file_name).replace(".txt", ".cnf")
    path = copy(input).replace(file_name, "")
    unit_clauses = list()
    clauses = list()

    # num_var = (10 ** (round(math.log(length, 10), 1))) ** 3
    num_var = int(str(length) * 3)  # TODO IMPROVE THE NUMBER

    # add clauses for only one possible value in each cell
    for line_count, line in enumerate(field):
        for cell_count, cell in enumerate(line):
            clauses.append(one_value_per_cell_clause(line_count, cell_count, length))
            # add known values to unit_clause
            if cell != 0:
                unit_clauses.append(
                    "{line_count}{cell_count}{value} 0\n".format(line_count=line_count+1, cell_count=cell_count+1,
                                                                 value=cell))

    # add clauses for row

    # add clauses for column

    # create first line of output_file
    num_clause = len(clauses)
    start_line = "p cnf {num_var} {num_clause}\n".format(num_var=num_var, num_clause=num_clause)
    clauses.extend(unit_clauses)
    with open(path + output_file_name, "w")as output_file:
        output_file.write(start_line)
        output_file.writelines(clauses)


encode("../../../examples/bsp-sudoku-input.txt")
