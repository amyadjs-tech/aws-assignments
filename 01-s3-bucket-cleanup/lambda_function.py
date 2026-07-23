import boto3
from datetime import datetime, timezone, timedelta

s3 = boto3.client("s3")

BUCKET_NAME = "amya-s3-cleanup-demo-2026"

AGE_DAYS = 30


def lambda_handler(event, context):

    cutoff_time = datetime.now(timezone.utc) - timedelta(days=AGE_DAYS)

    paginator = s3.get_paginator("list_objects_v2")

    deleted_files = []

    for page in paginator.paginate(Bucket=BUCKET_NAME):

        if "Contents" not in page:
            continue

        for obj in page["Contents"]:

            if obj["LastModified"] < cutoff_time:

                s3.delete_object(
                    Bucket=BUCKET_NAME,
                    Key=obj["Key"]
                )

                print(f"Deleted: {obj['Key']}")

                deleted_files.append(obj["Key"])

    return {
        "statusCode": 200,
        "deletedObjects": deleted_files
    }
