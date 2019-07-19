from my_solver.oliver import PuzzleInfo


class Position:

    def __init__(self, info: PuzzleInfo, row=1, column=1, value=1):
        self.info = info  # information
        self.row = row  # starts by 1
        self.column = column  # starts by 1
        self.value = value  # starts by 1

    def to_string(self) -> str:
        return str(self.row) + str(self.column) + str(self.value)

    def get_tuple(self):
        return self.row, self.column, self.value

    def __eq__(self, other):
        return self.to_string() == other.to_string()
