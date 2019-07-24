#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import subprocess
import sys
import time

from my_solver.oliver.decoder import Decoder
from my_solver.oliver.encoder.EncoderList import EncoderList
from my_solver.oliver.reader import Input


def main(*args):
    puzzle_path = os.path.abspath(args[1])
    solver_name = args[2]
    rel_path = os.path.abspath(puzzle_path)

    start = time.perf_counter()
    field, info = Input.input_source(rel_path)
    end = time.perf_counter()
    time_to_read = end - start
    print("Time to read file: {time}s".format(time=time_to_read), file=sys.stderr)

    # encode_info = PuzzleInfoEncode(info.input_file_complete_absolute(), info.length, info.text)
    start = time.perf_counter()
    encoder = EncoderList(None)
    encode_info = encoder.encode(field, info)
    end = time.perf_counter()
    time_to_encode = end - start
    print(f"Time to encode to SAT: {time_to_encode}s", file=sys.stderr)

    if solver_name.lower() == "riss":
        path_to_solver = os.path.abspath(os.path.join(os.path.dirname(args[0]), "env/bin/riss"))
    else:
        path_to_solver = os.path.abspath(os.path.join(os.path.dirname(args[0]), "env/bin/clasp.exe"))
    input_file = encode_info.output_file_name
    output_file = encode_info.SAT_solution_file_name

    start = time.perf_counter()

    solver_process = subprocess.Popen([path_to_solver, input_file], stdout=subprocess.PIPE)
    if solver_process.poll():
        solver_process.wait()
    with open(output_file, "wb") as output_SAT:
        output_SAT.write(solver_process.stdout.read())
    end = time.perf_counter()
    print(f"Finish solving in {end - start}s", file=sys.stderr)

    start = time.perf_counter()
    Decoder.decode(encode_info)
    end = time.perf_counter()
    time_to_decode = end - start
    print(f"Time to decode and get Solution SAT: {time_to_decode}s", file=sys.stderr)


if __name__ == "__main__":
    # run main code
    main(*sys.argv)
