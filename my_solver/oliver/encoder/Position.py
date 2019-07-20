from my_solver.oliver import PuzzleInfo


class Position:

    def __init__(self, info: PuzzleInfo, row=1, column=1, value=1):
        self.info = info  # information
        self.row = row  # starts by 1
        self.column = column  # starts by 1
        self.value = value  # starts by 1
        self.var = self.update_var()

    def update_var(self) -> int:
        back = (self.row - 1) * self.info.square_of_length \
               + (self.column - 1) * self.info.length \
               + self.value
        return back

    def to_string(self) -> str:
        return str(self.row) + str(self.column) + str(self.value)

    def get_tuple(self):
        return self.row, self.column, self.value

    def __eq__(self, other):
        return self.to_string() == other.to_string()

    def set_row(self, row: int):
        temp = self.row
        self.row = row
        self.var += (row - temp) * self.info.square_of_length

    def set_column(self, column: int):
        temp = self.column
        self.column = column
        self.var += (column - temp) * self.info.length

    def set_value(self, value: int):
        temp = self.value
        self.value = value
        self.var += value - temp

    def set_info(self, info):
        self.info = info
        self.var = self.update_var()
