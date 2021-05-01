#!/usr/bin/env python3
import traceback
import argparse
import ipaddress


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_file', help='Set source file.')
    parser.add_argument('dst_file', help='Set destination file.')
    parser.add_argument('--stub', dest='stub', help='Set IP stub address.')
    return parser.parse_args()


def file_reader(fname):
    with open(fname) as fd:
        for line in fd:
            line = line.rstrip()

            if line:
                yield line


def file_writer(fname, itr_data):
    with open(fname, 'w') as fd:
        for line in itr_data:
            fd.write(line + '\n')


def data_formater(itr_data, ip_addr):
    for line in itr_data:
        template = 'local-data: "{} IN {} {}"'
        ip_addr = ipaddress.ip_address(ip_addr)

        if ip_addr.version == 4:
            yield template.format(line, 'A', str(ip_addr))

        else:
            yield template.format(line, 'AAAA', str(ip_addr))


if __name__ == '__main__':
    try:
        args = arg_parse()
        file_writer(args.dst_file, data_formater(file_reader(args.src_file), args.stub))

    except Exception:
        traceback.print_exc()
