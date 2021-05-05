#!/usr/bin/env python3
import traceback
import argparse


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_file', help='Set source file.')
    parser.add_argument('dst_file', help='Set destination file.')
    return parser.parse_args()


def file_reader(fname):
    with open(fname) as fd:
        for line in fd:
            line = line.rstrip()
            line = line.lstrip()

            if line:
                yield line


def file_writer(fname, itr_data):
    with open(fname, 'w') as fd:
        for line in itr_data:
            fd.write(line + '\n')


def data_parse(itr_data):
    for line in itr_data:
        if line.startswith('local-data'):
            line = line.split()
            line = line[1]
            yield line.lstrip('"')


if __name__ == "__main__":
    try:
        args = arg_parse()
        freader = file_reader(args.src_file)
        dparser = data_parse(freader)
        file_writer(args.dst_file, dparser)

    except Exception:
        traceback.print_exc()
