import os
import sys
import time
from typing import List

from my_solver.oliver.PuzzleInfo import PuzzleInfoEncode

minus = "-"
empty = ""
size_of_deletion = -256


def unit_template_function(temp_clauses):
    return [f"{empty if x[1] else minus}{x[0]} 0\n" for x in temp_clauses]


def unit_template_function_delete(temp_clauses: List[List[int]]):
    back = list()
    while temp_clauses:
        back.extend([f"{empty if x[1] else minus}{x[0]} 0\n" for x in temp_clauses[size_of_deletion:]])
        del temp_clauses[size_of_deletion:]
    return back


def binary_template_function(temp_clauses):
    return [f"-{x[0]} -{x[1]} 0\n" for x in temp_clauses]


def binary_template_function_delete(temp_clauses: List[List[int]]):
    back = list()
    while temp_clauses:
        back.extend([f"-{x[0]} -{x[1]} 0\n" for x in temp_clauses[size_of_deletion:]])
        del temp_clauses[size_of_deletion:]
    return back


def binary_template_function_concat_delete(temp_clauses: List[List[int]]):
    back = list()
    while temp_clauses:
        back.extend(["-" + str(x[0]) + " -" + str(x[1]) + " 0\n" for x in temp_clauses[size_of_deletion:]])
        del temp_clauses[size_of_deletion:]
    return back


def binary_template_function_percent_delete(temp_clauses: List[List[int]]):
    back = list()
    while temp_clauses:
        back.extend(["-%s -%s 0\n" % (str(x[0]), str(x[1])) for x in temp_clauses[size_of_deletion:]])
        del temp_clauses[size_of_deletion:]
    return back


def one_template_function(temp_clauses):
    return [f"{' '.join([str(literal) for literal in clause])} 0\n" for clause in temp_clauses]


def one_template_function_delete(temp_clauses: List[List[int]]) -> List[str]:
    back = list()
    while temp_clauses:
        back.extend(
            [f"{' '.join([str(literal) for literal in clause])} 0\n" for clause in temp_clauses[size_of_deletion:]])
        del temp_clauses[size_of_deletion:]
    return back


def write_cnf_file(clauses: dict, output_file_name, start_line: str):
    with open(output_file_name, "w")as output_file:
        lines = [x for sub_clauses in clauses.values() for x in sub_clauses]
        lines.insert(0, start_line)
        output_file.write("".join(lines))


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
    with open(output_file_name, "w")as output_file:
        lines_to_write = [start_line]
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


def write_cnf_file_list_join_interpolation_map(clauses: dict, output_file_name, start_line):
    with open(output_file_name, "w")as output_file:
        lines_to_write = list()
        lines_to_write.append(clauses["unit"])
        lines_to_write.append(clauses["dist"])
        lines_to_write.append(clauses["row"])
        lines_to_write.append(clauses["column"])
        lines_to_write.append(clauses["block"])

        lines_to_write.append(clauses["one"])
        lines_to_write.append(clauses["row_one"])
        lines_to_write.append(clauses["column_one"])
        lines_to_write.append(clauses["block_one"])
        clauses.clear()
        write = [''.join(sub_list) for sub_list in lines_to_write]
        write.insert(0, start_line)
        output_file.write("".join(write))


def write_temp_cnf_file(clauses, info: PuzzleInfoEncode, name: str, template, ) -> int:
    start = time.perf_counter()
    back = len(clauses)
    path = os.path.join(info.input_file_path, name)
    info.temp_files.append(path)
    lines_to_write = list()
    with open(path, "w") as temp_file:
        lines_to_write.extend(template(clauses))
        temp_file.write("".join(lines_to_write))
    end = time.perf_counter()
    print(f"Time to write {name}: {end - start}s.", file=sys.stderr)
    return back


def write_temp_cnf_file_multiple(clauses, info: PuzzleInfoEncode, name: str, template,
                                 *extra_clauses) -> int:
    start = time.perf_counter()
    back = len(clauses)
    path = os.path.join(info.input_file_path, name)
    info.temp_files.append(path)
    lines_to_write = list()
    lines_to_write.extend(template(clauses))
    for extra in extra_clauses:
        back += len(extra[0])
        lines_to_write.extend(extra[1](extra[0]))
    with open(path, "w") as temp_file:
        temp_file.write("".join(lines_to_write))
    end = time.perf_counter()
    print(f"Time to write {name}: {end - start}s.", file=sys.stderr)
    return back


def write_cnf_file_from_parts(temp_files, output_file_name, start_line, *extra):
    lines_to_write = [start_line]
    for ex in extra:
        lines_to_write.extend(ex)
    for file in temp_files:
        with open(file) as temp_file:
            lines_to_write.append(temp_file.read())
    with open(output_file_name, "w")as output_file:
        output_file.write("".join(lines_to_write))
