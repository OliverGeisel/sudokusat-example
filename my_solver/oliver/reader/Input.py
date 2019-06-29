from typing import List, Tuple


from my_solver.oliver.PuzzleInfo import PuzzleInfoType, PuzzleInfoInput


def get_PuzzleInfo(infos: List[str]) -> PuzzleInfoType:
    length = int((infos[3].split()[2]).split("x")[0])
    back = PuzzleInfoInput(length, str.join("", infos))
    return back


def input_source(path: str) -> Tuple[List[List[int]], int, PuzzleInfoType]:
    with open(path) as source:
        content = source.readlines()
    info = get_PuzzleInfo(content[0:4])
    length = info.length  # line with length
    field_raw = content[info.start_line:info.end_line]
    for line in field_raw:  # remove split lines TODO improve the iteration  FILTER
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
            part = part.replace("__", "0")  # Find better replacement
            part = part.replace("___", "0")
            part = part.replace("_", "0")
            part = part.replace(" ", "")  # TODO Stringbuilder? improve
            data_line.extend(part)
        data_line = list(map(lambda x: int(x), data_line))  # convert str to int
        field_data.append(data_line)
    for line in field_data:
        for cell in line:
            print(cell, end="")
        print()
    return field_data, length, info
