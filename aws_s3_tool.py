#!/usr/bin/env python3
import sys
import boto3
import pathlib
import argparse
import traceback

# AWS_DEFAULT_REGION
# AWS_PROFILE
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY

def list_objects(client: any, bucket: str, prefix: str = "", items: int = 200) -> list:
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=items)
    return (response["IsTruncated"], response["Contents"])


def get_object_data(client: any, bucket: str, file: str) -> bytes:
    response = client.get_object(Bucket=bucket, Key=file)
    return response["Body"].read()


def put_object_data(client: any, bucket: str, file: str, data: bytes) -> dict:
    return client.put_object(Bucket=bucket, Key=file, Body=data)


def delete_object(client: any, bucket: str, file: str) -> None:
    client.delete_object(Bucket=bucket, Key=file)


def get_file_data(file_name: str) -> bytes:
    file = pathlib.Path(file_name)
    return file.read_bytes()


def put_file_data(file_name: str, data: bytes) -> None:
    file = pathlib.Path(file_name)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)
    file.write_bytes(data)


def print_objects(items: list) -> None:
    for item in items:
        print("{} {} {}".format(item["Key"], item["Size"], item["LastModified"]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["ls", "get", "put", "rm", "cat"], help="Set action.")
    parser.add_argument("src", help="Set source file path or bucket name.")
    parser.add_argument("dst", help="Set destination file path or bucket name.")
    parser.add_argument("--limit", dest="limit", default="100", type=int, help="Set items output limit.")
    return parser.parse_args()


try:
    args = parse_args()
    client = boto3.client("s3")

    if args.cmd == "ls":
        # Args: <bucket> <path> [--limit]
        (truncated, items) = list_objects(client, args.src, args.dst, args.limit)
        if truncated:
            print("Warning! The list of files is truncated!", file=sys.stderr)

        print("Resource: arn:aws:s3:::{}".format(args.src))
        print_objects(items)

    elif args.cmd == "get":
        # Args: <bucket> <file>
        print("{} {}/{}".format(args.cmd, args.src, args.dst))
        put_file_data(args.dst, get_object_data(client, args.src, args.dst))

    elif args.cmd == "put":
        # Args: <bucket> <file>
        print("{} {}/{}".format(args.cmd, args.src, args.dst))
        put_object_data(client, args.src, args.dst, get_file_data(args.dst))

    elif args.cmd == "cat":
        # Args: <bucket> <file>
        print("{} {}/{}".format(args.cmd, args.src, args.dst))
        print(get_object_data(client, args.src, args.dst))

    if args.cmd == "rm":
        # Args: <bucket> <file>
        print("{} {}/{}".format(args.cmd, args.src, args.dst))
        delete_object(client, args.src, args.dst)

except Exception:
    traceback.print_exc()
    sys.exit(1)
