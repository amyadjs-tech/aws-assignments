import boto3
from datetime import datetime

ec2 = boto3.client("ec2")

VOLUME_ID = "vol-05ebd628402d2bff6"

def lambda_handler(event, context):

    snapshots = ec2.describe_snapshots(
        OwnerIds=["self"],
        Filters=[
            {
                "Name": "volume-id",
                "Values": [VOLUME_ID]
            }
        ]
    )["Snapshots"]

    if not snapshots:
        raise Exception("No snapshots found.")

    latest_snapshot = sorted(
        snapshots,
        key=lambda x: x["StartTime"],
        reverse=True
    )[0]

    snapshot_id = latest_snapshot["SnapshotId"]

    ami_name = f"restore-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    response = ec2.register_image(
        Name=ami_name,
        RootDeviceName="/dev/xvda",
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "SnapshotId": snapshot_id,
                    "DeleteOnTermination": True,
                    "VolumeType": "gp3"
                }
            }
        ]
    )

    image_id = response["ImageId"]

    waiter = ec2.get_waiter("image_available")
    waiter.wait(ImageIds=[image_id])

    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1
    )

    instance_id = response["Instances"][0]["InstanceId"]

    ec2.create_tags(
        Resources=[instance_id],
        Tags=[
            {
                "Key": "RestoredFrom",
                "Value": snapshot_id
            }
        ]
    )

    print(f"New Instance Created: {instance_id}")

    return {
        "statusCode": 200,
        "InstanceId": instance_id,
        "SnapshotId": snapshot_id,
        "AMI": image_id
    }
