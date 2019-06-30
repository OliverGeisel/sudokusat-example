#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import sys

from my_solver.oliver.decoder import Decoder
from my_solver.oliver.encoder import Encoder
from my_solver.oliver.reader import Input


def main(*args):
    puzzle_path = os.path.abspath(args[1])
    # path_to_solver = os.path.abspath(args[2])
    rel_path = os.path.relpath(puzzle_path)

    field, info = Input.input_source(rel_path)
    encode_info = Encoder.encode(field, info)
    input("""DAS SIMULIERT RISS!
    bitte Riss selber ausführen
    Bitte Enter drücken""")
    # input_file = encode_info.input_file_path + encode_info.output_file_name
    # subprocess.run([path_to_solver, input_file, ">", output_file])
    Decoder.decode(encode_info)


if __name__ == "__main__":
    # run main code
    main(*sys.argv)
