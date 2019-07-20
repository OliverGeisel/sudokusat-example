
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
    minus = "-"
    empty = ""
    with open(output_file_name, "w")as output_file:
        lines_to_write = list()
        lines_to_write.append(start_line)
        lines_to_write.extend([f"{empty if x[1] else minus}{x[0]} 0\n" for x in clauses["unit"]])
        lines_to_write.extend([f"-{x[0]} -{x[1]} 0\n" for x in clauses["dist"]])
        lines_to_write.extend([f"-{x[0]} -{x[1]} 0\n" for x in clauses["row"]])
        lines_to_write.extend([f"-{x[0]} -{x[1]} 0\n" for x in clauses["column"]])
        lines_to_write.extend([f"-{x[0]} -{x[1]} 0\n" for x in clauses["block"]])
        for clause in clauses["one"]:
            lines_to_write.append(f"{' '.join([str(x) for x in clause])} 0\n")
        for clause in clauses["row_one"]:
            lines_to_write.append(f"{' '.join([str(x) for x in clause])} 0\n")
        for clause in clauses["column_one"]:
            lines_to_write.append(f"{' '.join([str(x) for x in clause])} 0\n")
        for clause in clauses["block_one"]:
            lines_to_write.append(f"{' '.join([str(x) for x in clause])} 0\n")
        write = "".join(lines_to_write)
        output_file.write(write)
