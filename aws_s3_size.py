#!/usr/bin/env python3
import sys
import boto3
import datetime
import traceback

# AWS_DEFAULT_REGION
# AWS_PROFILE
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY


try:
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=3)
    bucket = sys.argv[1]
    client = boto3.client("cloudwatch")

    responce = client.get_metric_statistics(
        Namespace="AWS/S3",
        MetricName="BucketSizeBytes",
        Statistics=["Average"],
        Dimensions=[
            {"Name": "BucketName",  "Value": bucket},
            {"Name": "StorageType", "Value": "StandardStorage"}
        ],
        Period=3600,
        StartTime=start_time.isoformat(),
        EndTime=now.isoformat()
    )

    for item in responce["Datapoints"]:
        time = item["Timestamp"]
        size = item["Average"]

        print("{} s3://{}/ {}".format(
            time.strftime(r"%Y-%m-%d %H:%M:%S"),
            bucket,
            (size / 1024 / 1024 / 1024)
        ))

except Exception:
    traceback.print_exc()
    sys.exit(1)
