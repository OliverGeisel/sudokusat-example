import sys

from my_solver.oliver.reader.Input import input_source


def main(*args):
    puzzle_path = args[1]
    =input_source(puzzle_path)


if __name__ == "__main__":
    # run main code
    main(*sys.argv)
