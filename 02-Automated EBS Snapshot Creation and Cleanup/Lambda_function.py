import boto3
from datetime import datetime, timezone, timedelta

ec2 = boto3.client("ec2")

VOLUME_ID = "vol-0123456789abcdef0"

TAG_KEY = "CreatedBy"
TAG_VALUE = "Lambda-Backup"

RETENTION_DAYS = 30


def lambda_handler(event, context):

    response = ec2.create_snapshot(
        VolumeId=VOLUME_ID,
        Description="Lambda Automated Backup"
    )

    snapshot_id = response["SnapshotId"]

    ec2.create_tags(
        Resources=[snapshot_id],
        Tags=[
            {
                "Key": TAG_KEY,
                "Value": TAG_VALUE
            }
        ]
    )

    print(f"Created Snapshot: {snapshot_id}")

    snapshots = ec2.describe_snapshots(
        OwnerIds=["self"],
        Filters=[
            {
                "Name": "tag:CreatedBy",
                "Values": [TAG_VALUE]
            }
        ]
    )["Snapshots"]

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    deleted = []

    for snapshot in snapshots:

        if snapshot["StartTime"] < cutoff:

            ec2.delete_snapshot(
                SnapshotId=snapshot["SnapshotId"]
            )

            print(f"Deleted Snapshot: {snapshot['SnapshotId']}")

            deleted.append(snapshot["SnapshotId"])

    return {
        "CreatedSnapshot": snapshot_id,
        "DeletedSnapshots": deleted
    }
