import re


def read_source(source_path: str) -> None:
    with open(source_path) as solution:
        content = solution.readlines()
    variables = content[-1]
    variables = variables.replace("v ", "")
    variables = re.sub(r"-\d+ ", "", variables).split()

    variables = list(map(lambda x: int(x), variables))
    for count, i in enumerate(variables):
        if count % 9 == 0:
            print()
        print(str(i)+"|", end="")
    i = 5
    i += 2


read_source("../../../examples/bsp-sudoku-SAT-sol.txt")
