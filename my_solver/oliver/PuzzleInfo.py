import os

import math


class PuzzleInfo:

    def __init__(self, path_of_file: str, length: int = 9, text: str = ""):
        self.input_file_path, self.input_file_name = os.path.split(os.path.abspath(path_of_file))
        self.length = length  # values from 1 to length
        self.sqrt_of_length = int(math.sqrt(self.length))
        self.text = text  # further information

    def input_file_complete_absolute(self):
        return os.path.join(self.input_file_path, self.input_file_name)

    def input_file_complete_rel(self):
        return os.path.relpath(self.input_file_complete_absolute())


class PuzzleInfoInput(PuzzleInfo):

    def __init__(self, path_of_file: str, length: int = 9, text: str = ""):
        super().__init__(path_of_file, length, text)
        self.start_line = 5  # depends on first line with '+'
        self.end_line = self.start_line + length + int(math.sqrt(length))


class PuzzleInfoEncode(PuzzleInfo):

    def __init__(self, path: str, length=9, text=""):
        super().__init__(path, length, text)
        self.output_file_path = self.SAT_solution_file_path = self.input_file_path
        self.output_file_name = self.input_file_name.replace(".txt", ".cnf")
        self.SAT_solution_file_name = self.output_file_name.replace(".cnf", "-SAT-sol.txt")

    def __int__(self, info: PuzzleInfoInput):
        self.__init__(info.input_file_complete_absolute(), info.length, info.text)

    def output_file_complete_absolute(self):
        return os.path.join(self.output_file_path, self.output_file_name)

    def output_file_complete_rel(self):
        return os.path.relpath(self.output_file_complete_absolute())

    def SAT_solution_file_complete_absolute(self):
        return os.path.join(self.SAT_solution_file_path, self.SAT_solution_file_name)

    def SAT_solution_file_complete_rel(self):
        return os.path.relpath(self.SAT_solution_file_complete_absolute())


class PuzzleInfoOutput(PuzzleInfo):
    def __init__(self, encode_info: PuzzleInfoEncode):
        super().__init__(encode_info.output_file_complete_absolute(), encode_info.length, encode_info.text)
        self.output_file_path = self.input_file_path
        self.input_file_name = encode_info.SAT_solution_file_name
        self.output_file_name = encode_info.SAT_solution_file_name.replace("-SAT-sol.txt", "-solution.txt")

    def output_file_complete_absolute(self):
        return os.path.join(self.output_file_path, self.output_file_name)

    def output_file_complete_rel(self):
        return os.path.relpath(self.output_file_complete_absolute())
