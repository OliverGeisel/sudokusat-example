import os
import time

from my_solver.oliver.PuzzleInfo import PuzzleInfoEncode

minus = "-"
empty = ""


def unit_template_function(temp_clauses):
    return [f"{empty if x[1] else minus}{x[0]} 0\n" for x in temp_clauses]


def binary_template_function(temp_clauses):
    return [f"-{x[0]} -{x[1]} 0\n" for x in temp_clauses]


def one_template_function(temp_clauses):
    back = list()
    for clause in temp_clauses:
        back.append(f"{' '.join([str(x) for x in clause])} 0\n")
    return back


def write_cnf_file(clauses, output_file_name, start_line):
    with open(output_file_name, "w")as output_file:
        output_file.write(start_line)
        output_file.writelines(clauses["unit"])
        output_file.writelines(clauses["dist"])

        output_file.writelines(clauses["row"])
        output_file.writelines(clauses["column"])
        output_file.writelines(clauses["block"])

        output_file.writelines(clauses["one"])


def write_cnf_file_list(clauses, output_file_name, start_line):
    with open(output_file_name, "w")as output_file:
        output_file.write(start_line)
        lines_to_write = list()
        for clause in clauses["unit"]:
            lines_to_write.append("%s%s 0\n" % (("" if clause[1] else "-"), clause[0]))
        for clause in clauses["dist"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        for clause in clauses["row"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        for clause in clauses["column"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        for clause in clauses["block"]:
            lines_to_write.append("-%s -%s 0\n" % (clause[0], clause[1]))
        for clause in clauses["one"]:
            clause.append("0\n")
            clause = list(map(lambda x: str(x), clause))
            lines_to_write.append(" ".join(clause))
        output_file.writelines(lines_to_write)


def write_cnf_file_list_join(clauses, output_file_name, start_line):
    space = " "
    minus = "-"
    empty = ""
    end = " 0\n"
    with open(output_file_name, "w")as output_file:
        output_file.write(start_line)
        lines_to_write = list()
        for clause in clauses["unit"]:
            lines_to_write.append(empty if clause[1] else minus)
            lines_to_write.append(str(clause[0]))
            lines_to_write.append(end)

        for clause in clauses["dist"]:
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[0]))
            lines_to_write.append(space)
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[1]))
            lines_to_write.append(end)

        for clause in clauses["row"]:
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[0]))
            lines_to_write.append(space)
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[1]))
            lines_to_write.append(end)
        for clause in clauses["column"]:
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[0]))
            lines_to_write.append(space)
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[1]))
            lines_to_write.append(end)
        for clause in clauses["block"]:
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[0]))
            lines_to_write.append(space)
            lines_to_write.append(minus)
            lines_to_write.append(str(clause[1]))
            lines_to_write.append(end)
        for clause in clauses["one"]:
            clause = list(map(lambda x: str(x), clause))
            clause.append("0\n")
            lines_to_write.append(" ".join(clause))
        write = "".join(lines_to_write)
        output_file.write(write)


def write_cnf_file_list_join_interpolation(clauses, output_file_name, start_line):
    minus = "-"
    empty = ""
    with open(output_file_name, "w")as output_file:
        lines_to_write = list()
        lines_to_write.append(start_line)
        for clause in clauses["unit"]:
            lines_to_write.append(f"{empty if clause[1] else minus}{clause[0]} 0\n")
        for clause in clauses["dist"]:
            lines_to_write.append(f"-{clause[0]} -{clause[1]} 0\n")
        for clause in clauses["row"]:
            lines_to_write.append(f"-{clause[0]} -{clause[1]} 0\n")
        for clause in clauses["column"]:
            lines_to_write.append(f"-{clause[0]} -{clause[1]} 0\n")
        for clause in clauses["block"]:
            lines_to_write.append(f"-{clause[0]} -{clause[1]} 0\n")
        for clause in clauses["one"]:
            lines_to_write.append(f"{' '.join([str(x) for x in clause])} 0\n")
        write = "".join(lines_to_write)
        output_file.write(write)


def write_cnf_file_list_join_interpolation_map(clauses, output_file_name, start_line):
    with open(output_file_name, "w")as output_file:
        lines_to_write = list()
        lines_to_write.append(start_line)
        lines_to_write.extend(unit_template_function(clauses["unit"]))
        lines_to_write.extend(binary_template_function(clauses["dist"]))
        lines_to_write.extend(binary_template_function(clauses["row"]))
        lines_to_write.extend(binary_template_function(clauses["column"]))
        lines_to_write.extend(binary_template_function(clauses["block"]))

        lines_to_write.extend(one_template_function(clauses["one"]))
        lines_to_write.extend(one_template_function(clauses["row_one"]))
        lines_to_write.extend(one_template_function(clauses["column_one"]))
        lines_to_write.extend(one_template_function(clauses["block_one"]))

        write = "".join(lines_to_write)
        output_file.write(write)


def write_temp_cnf_file(clauses, info: PuzzleInfoEncode, name: str, template, clear_clauses: bool = True) -> int:
    start = time.perf_counter()
    back = len(clauses)
    path = os.path.join(info.input_file_path, name)
    info.temp_files.append(path)
    lines_to_write = list()
    with open(path, "w") as temp_file:
        lines_to_write.extend(template(clauses))
        temp_file.write("".join(lines_to_write))
    end = time.perf_counter()
    # if clear_clauses:
    #    del clauses[:]
    print(f"Time to write {name}: {end - start}s.")
    return back


def write_cnf_file_from_parts(temp_files, output_file_name, start_line, *extra):
    lines_to_write = [start_line]
    for ex in extra:
        lines_to_write.append(ex)
    for file in temp_files:
        with open(file) as temp_file:
            lines_to_write.append(temp_file.read())
    with open(output_file_name, "w")as output_file:
        output_file.write("".join(lines_to_write))
