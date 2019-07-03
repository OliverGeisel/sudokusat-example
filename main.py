#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import sys
import time

from my_solver.oliver.decoder import Decoder
from my_solver.oliver.encoder import Encoder
from my_solver.oliver.reader import Input


def main(*args):
    puzzle_path = os.path.abspath(args[1])
    # path_to_solver = os.path.abspath(args[2])
    rel_path = os.path.relpath(puzzle_path)
    start = time.perf_counter()
    field, info = Input.input_source(rel_path)
    end = time.perf_counter()
    time_to_read = end - start
    print("Time to read file: {time}s".format(time=time_to_read))

    start = time.perf_counter()
    encode_info = Encoder.encode(field, info)
    end = time.perf_counter()
    time_to_encode = end - start
    print("Time to encode to SAT: {time}s".format(time=time_to_encode))

    input("""DAS SIMULIERT RISS!
    bitte Riss selber ausführen
    Bitte Enter drücken""")
    # input_file = encode_info.input_file_path + encode_info.output_file_name
    # subprocess.run([path_to_solver, input_file, ">", output_file])

    start = time.perf_counter()
    Decoder.decode(encode_info)
    end = time.perf_counter()
    time_to_decode = end - start
    print("Time to decode and get Solution SAT: {time}s".format(time=time_to_decode))


if __name__ == "__main__":
    # run main code
    main(*sys.argv)
