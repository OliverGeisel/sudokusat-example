import os
from pathlib import Path

from reprobench.tools.executable import ExecutableTool

DIR = os.path.dirname(__file__)


class MySudokuSolver(ExecutableTool):
    name = "My Sudoku Solver"

    path = os.path.join(DIR, "my_solver.sh")

    @classmethod
    def setup(cls):
        super().setup()
        # # for example you can use subprocess to execute GNU Make:s
        # subprocess.run(["make"], cwd=DIR)

    def get_cmdline(self):
        # - `self.path` is as defined above
        # - `self.task` contains the path for the sudoku instance
        # - `self.parameters` contains the parameter for the run,
        #   in this case this is the `solver` parameter, whose value
        #   is either `riss` or `glucose`.

        # For example to run the solver as ./solver [sat_solver] [task]:
        solver = self.parameters.get("solver")
        return [self.path, solver, self.task]

    @classmethod
    def is_ready(cls):
        """This checks if your solver is ready.
        If it returns false, the `setup()` method is executed
        """

        if not super().is_ready():
            return False

        return Path(cls.path).is_file()
