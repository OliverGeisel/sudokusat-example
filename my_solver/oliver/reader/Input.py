from typing import List, Tuple

import math


def input_source(path: str) -> Tuple[List[List[int]],int]:
    with open(path) as source:
        content = source.readlines()
    length = content[3].split()[2]  # line with length
    length = int(length.split("x")[0])  # get concrete length of sudoku as int
    start_line = 5
    end_line = start_line + length + int(math.sqrt(length))
    field_raw = content[start_line:end_line]
    for line in field_raw:  # remove split lines TODO improve the iteration
        if line[0] == "+":
            field_raw.remove(line)
    for i in field_raw:
        print(i, end="")

    # Now get field in an array
    field_data = list()

    for line in field_raw:
        raw_data_line = line.split("|")
        data_line = list()
        for part in raw_data_line:
            if part == "" or part == "\n":
                continue
            part = part.replace(" ", "")  # TODO Stringbuilder? improve
            part = part.replace("_", "0")
            data_line.extend(part)
        data_line = list(map(lambda x: int(x), data_line))   # convert str to int
        field_data.append(data_line)
    for line in field_data:
        for cell in line:
            print(cell,end="")
        print()
    return field_data, length



