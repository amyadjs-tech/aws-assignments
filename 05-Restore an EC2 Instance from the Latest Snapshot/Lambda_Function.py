import boto3
from datetime import datetime

ec2 = boto3.client("ec2")

# Replace with your EBS Volume ID
VOLUME_ID = "vol-05ebd628402d2bff6"

def lambda_handler(event, context):

    # Get all snapshots for the volume
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
        raise Exception(f"No snapshots found for volume {VOLUME_ID}")

    # Get latest snapshot
    latest_snapshot = sorted(
        snapshots,
        key=lambda x: x["StartTime"],
        reverse=True
    )[0]

    snapshot_id = latest_snapshot["SnapshotId"]

    print(f"Latest Snapshot: {snapshot_id}")

    ami_name = f"restore-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Register AMI from snapshot
    response = ec2.register_image(
        Name=ami_name,
        Description="AMI created from latest EBS snapshot",
        Architecture="x86_64",
        RootDeviceName="/dev/xvda",
        VirtualizationType="hvm",
        EnaSupport=True,
        BootMode="uefi-preferred",
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "SnapshotId": snapshot_id,
                    "VolumeType": "gp3",
                    "DeleteOnTermination": True
                }
            }
        ]
    )

    image_id = response["ImageId"]

    print(f"AMI Created: {image_id}")

    # Wait until AMI becomes available
    waiter = ec2.get_waiter("image_available")
    waiter.wait(ImageIds=[image_id])

    print("AMI is now available")

    # Launch EC2 Instance
    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "RestoredFrom",
                        "Value": snapshot_id
                    }
                ]
            }
        ]
    )

    instance_id = response["Instances"][0]["InstanceId"]

    print(f"New Instance Created: {instance_id}")

    return {
        "statusCode": 200,
        "SnapshotId": snapshot_id,
        "ImageId": image_id,
        "InstanceId": instance_id
    }
