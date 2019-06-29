from copy import copy
from typing import NewType

import math


class PuzzleInfo:

    def __init__(self, path_of_file: str, length: int = 9, text: str = ""):
        self.input_file_name = path_of_file.split("/")[-1]
        self.input_file_path = copy(path_of_file).replace(self.input_file_name, "")

        self.length = length
        self.sqrt_of_length = int(math.sqrt(self.length))
        self.text = text
        self.start_line = 5
        self.end_line = self.start_line + length + int(math.sqrt(length))


class PuzzleInfoInput(PuzzleInfo):

    def __init__(self, path_of_file: str, length: int = 9, text: str = ""):
        super().__init__(path_of_file, length, text)
        self.output_file_name = copy(self.input_file_name).replace(".txt", ".cnf")

    pass


class PuzzleInfoOutput(PuzzleInfo):
    pass


PuzzleInfoType = NewType("PuzzleInfo", PuzzleInfo)
PuzzleInfoInputType = NewType("PuzzleInfoInput", PuzzleInfoInput)
PuzzleInfoOutputType = NewType("PuzzleInfoOutput", PuzzleInfoOutput)
