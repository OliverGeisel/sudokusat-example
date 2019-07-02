class Position:

    def __init__(self, row, column, value):
        self.row = row
        self.column = column
        self.value = value

    def to_string(self) -> str:
        return str(self.row) + str(self.column) + str(self.value)

    def __eq__(self, other):
        return self.to_string() == other.to_string()
