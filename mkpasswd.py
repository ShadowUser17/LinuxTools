#!/usr/bin/env python3
import argparse
import traceback
import crypt
import random
import string

methods = {
    'blowfish': crypt.METHOD_BLOWFISH,
    'sha512': crypt.METHOD_SHA512,
    'sha256': crypt.METHOD_SHA256,
    'md5': crypt.METHOD_MD5
}


def get_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='password', default='')
    parser.add_argument('-l', dest='length', type=int, default=8)
    parser.add_argument('-m', dest='method', choices=methods.keys(), default='sha512')
    return parser.parse_args(args)


def gen_passwd(length):
    passwd = random.choices(string.ascii_letters, k=length)
    return ''.join(passwd)


def gen_hash(method, passwd):
    salt = crypt.mksalt(method)
    return crypt.crypt(passwd, salt)


def main(args=None):
    try:
        args = get_args(args)
        method = methods.get(args.method)

        if args.password == '':
            password = gen_passwd(args.length)
            print('Generated password:', password)
            print(method.name, ': ', gen_hash(method, password), sep='')

        else:
            length = len(args.password)

            if length >= args.length:
                print(method.name, ': ', gen_hash(method, args.password), sep='')

            else:
                print('Password: ', length, ' < ', args.length, sep='')

    except Exception:
        traceback.print_exc()


if __name__ == '__main__':
    main()
