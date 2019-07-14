#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import subprocess
import sys
import time

from my_solver.oliver.PuzzleInfo import PuzzleInfoEncode
from my_solver.oliver.decoder import Decoder
from my_solver.oliver.encoder import Encoder
from my_solver.oliver.reader import Input


def main(*args):
    puzzle_path = os.path.abspath(args[1])
    solver_name = args[2]
    rel_path = os.path.relpath(puzzle_path)

    start = time.perf_counter()
    field, info = Input.input_source(rel_path)
    end = time.perf_counter()
    time_to_read = end - start
    print("Time to read file: {time}s".format(time=time_to_read))

   # encode_info = PuzzleInfoEncode(info.input_file_complete_absolute(), info.length, info.text)
    """start = time.perf_counter()
    encode_info = Encoder.encode(field, info)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to encode to SAT: {time}s".format(time=time_to_encode))
     """
    """
    start = time.perf_counter()
    encode_info = Encoder.encode_parallel(field, info)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to encode to SAT parallel: {time}s".format(time=time_to_encode))
    """
    start = time.perf_counter()
    encode_info = Encoder.encode_parallel_p(field, info)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to encode to SAT parallel: {time}s".format(time=time_to_encode))

    input("""DAS SIMULIERT RISS!
    bitte Riss selber ausführen
    Bitte Enter drücken""")
    path_to_solver = ""
    if solver_name == "riss":
        path_to_solver = os.path.abspath(os.path.join(os.path.dirname(args[0]), "env/bin/riss"))
    else:
        path_to_solver = os.path.abspath(os.path.join(os.path.dirname(args[0]), "env/bin/clasp.exe"))
    input_file = encode_info.output_file_complete_absolute()
    output_file = encode_info.SAT_solution_file_complete_absolute()
    # subprocess.Popen(args=[path_to_solver, input_file, "> ".join(output_file)])
    #
    start = time.perf_counter()
    Decoder.decode(encode_info)
    end = time.perf_counter()
    time_to_decode = end - start
    print("Time to decode and get Solution SAT: {time}s".format(time=time_to_decode))


if __name__ == "__main__":
    # run main code
    main(*sys.argv)
