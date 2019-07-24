from typing import List, Tuple

from my_solver.oliver.PuzzleInfo import PuzzleInfoInput

control = ["", "|", "\n"]


def get_PuzzleInfo(file_path: str, infos: List[str]) -> PuzzleInfoInput:
    length = int((infos[3].split()[2]).split("x")[0])
    back = PuzzleInfoInput(file_path, length, str.join("", infos))
    return back


def input_source(path: str) -> Tuple[List[List[int]], PuzzleInfoInput]:
    with open(path, "r") as source:
        content = source.readlines()
    info = get_PuzzleInfo(path, content[0:4])
    field_raw = content[info.start_line:info.end_line]
    # for line in field_raw:  # remove split lines
    #     if line[0] == "+":
    #         field_raw.remove(line)
    field_raw = [line for line in field_raw if line[0] != "+"]

    # print field without separator
    # for i in field_raw:
    #     print(i, end="")

    # Now get field in an array
    field_data = list()

    for line in field_raw:
        raw_data_line = line.split()
        data_line = list()
        for part in raw_data_line:
            if part in control:
                continue
            part = "0" if "_" in part else part
            data_line.append(part)
        data_line = [int(x) for x in data_line]  # convert str to int
        field_data.append(data_line)
    return field_data, info
