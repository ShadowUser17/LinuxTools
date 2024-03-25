#!/usr/bin/env python3
import os
import sys
import boto3
import pathlib
import traceback

# AWS_DEFAULT_REGION
# AWS_PROFILE
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# CDKTF_BUCKET_NAME
# CDKTF_BUCKET_ROOT
# CDKTF_FORCE_WRITE


def list_objects(client: any, bucket: str, prefix: str = "", items: int = 200) -> list:
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=items)
    return (response["IsTruncated"], response["Contents"])


def get_object_data(client: any, bucket: str, file: str) -> bytes:
    response = client.get_object(Bucket=bucket, Key=file)
    return response["Body"].read()


def put_file_data(file_name: str, data: bytes, force: bool = False) -> None:
    file = pathlib.Path(file_name)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=force)
    file.write_bytes(data)


try:
    CDKTF_BUCKET_NAME = os.environ.get("CDKTF_BUCKET_NAME", "")
    CDKTF_BUCKET_ROOT = os.environ.get("CDKTF_BUCKET_ROOT", "")
    CDKTF_FORCE_WRITE = bool(os.environ.get("CDKTF_FORCE_WRITE", ""))

    client = boto3.client("s3")

    print("Get files from {}.".format(CDKTF_BUCKET_NAME))
    (truncated, files) = list_objects(client, CDKTF_BUCKET_NAME, CDKTF_BUCKET_ROOT)
    if truncated:
        print("Warning! The list of files is truncated!")

    for item in filter(lambda item: item["Key"].endswith("tfstate"), files):
        try:
            print("Store {} to FS.".format(item["Key"]))
            data = get_object_data(client, CDKTF_BUCKET_NAME, item["Key"])
            put_file_data(item["Key"], data, CDKTF_FORCE_WRITE)

        except FileExistsError as msg:
            print(msg, file=sys.stderr)

except Exception:
    traceback.print_exc()
    sys.exit(1)
