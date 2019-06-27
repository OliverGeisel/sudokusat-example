from copy import copy

from my_solver.oliver.reader.Input import input_source


def one_value_per_cell_clause(line_count: int, cell_count: int, length: int) -> str:
    back = ""
    for i in length:
        back += str(line_count) + str(cell_count) + str(i) + " "
    back += "0\n"
    return


def encode(input: str) -> None:
    field, length = input_source(input)
    file_name = input.split("/")[-1]
    output_file_name = copy(file_name).replace(".txt", ".cnf")
    path = copy(input).replace(file_name, "")
    clauses = list()

    # num_var = (10 ** (round(math.log(length, 10), 1))) ** 3
    num_var = int(str(length) * 3)  # TODO IMPROVE THE NUMBER

    # add clauses for only one possible value in each cell
    for line_count, line in enumerate(field):
        for cell_count, cell in enumerate(line):
            clauses.append(one_value_per_cell_clause(line_count, cell_count, length))

    # add known values as unit-clause
    for line in field:
        for cell in line:
            if cell != 0:
                clauses.append("{} 0\n").format(str(cell))

    num_clause = len(clauses)
    start_line = "p cnf {num_var} {num_clause}\n".format(num_var, num_clause)

    with open(path + output_file_name)as output_file:
        output_file.write(start_line)
        output_file.writelines(clauses)


encode("../../../examples/bsp-sudoku-input.txt")
