# Assignment 5: Restore an EC2 Instance from the Latest Snapshot

## Objective

Automate disaster recovery by restoring an EC2 instance from the most recent EBS snapshot using **AWS Lambda**, **Amazon EC2**, and **Boto3**.

---

# Step 1: Login to AWS

1. Sign in to the **AWS Management Console**.
2. Select one AWS Region for the assignment (recommended: **us-east-1**).

---

# Step 2: Prerequisites

Before starting this assignment, ensure that:

- An EC2 instance already exists.
- At least one snapshot of the instance's **root EBS volume** exists.
- (You can use the snapshot created in **Assignment 2**.)

Find the Volume ID:

```text
EC2
→ Volumes
```

Example:

```text
vol-05ebd628402d2bff6
```

📸 **Screenshot 1:** Existing EBS Volume and Snapshot.

---

# Step 3: Create an IAM Role for Lambda

Go to:

```text
IAM
→ Roles
→ Create Role
```

Choose:

- **Trusted Entity:** AWS Service
- **Use Case:** Lambda

Attach the managed policy:

```text
AWSLambdaBasicExecutionRole
```

Role Name:

```text
LambdaEC2RestoreRole
```

Click **Create Role**.

📸 **Screenshot 2:** IAM Role Created.

---

# Step 4: Create an Inline IAM Policy

Open the role.

Go to:

```text
Permissions
→ Add Permissions
→ Create Inline Policy
→ JSON
```

Paste the following policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeSnapshots",
        "ec2:RegisterImage",
        "ec2:RunInstances",
        "ec2:DescribeImages",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

Policy Name:

```text
EC2RestorePolicy
```

Click **Create Policy**.

📸 **Screenshot 3:** Inline Policy.

---

# Step 5: Create the Lambda Function

Go to:

```text
AWS Lambda
→ Create Function
```

Choose:

```text
Author from Scratch
```

Configure:

| Setting | Value |
|----------|-------|
| Function Name | EC2RestoreFromSnapshot |
| Runtime | Python 3.12 |
| Architecture | x86_64 |
| Execution Role | Use Existing Role |
| Existing Role | LambdaEC2RestoreRole |

Click **Create Function**.

📸 **Screenshot 4:** Lambda Configuration.

---

# Step 6: Add the Lambda Code

Replace the default code with:

import boto3 from datetime import datetime

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
        raise Exception(f"No snapshots found for volume {VOLUME_ID}")

    latest_snapshot = sorted(
        snapshots,
        key=lambda x: x["StartTime"],
        reverse=True
    )[0]

    snapshot_id = latest_snapshot["SnapshotId"]

    print(f"Latest Snapshot: {snapshot_id}")

    ami_name = f"restore-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

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

    waiter = ec2.get_waiter("image_available")
    waiter.wait(ImageIds=[image_id])

    print("AMI is now available")

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

Click **Deploy**.

📸 **Screenshot 5:** Lambda Code.

> **Note:** If your Lambda times out during testing, increase the Lambda timeout from **3 seconds** to **2–5 minutes** under **Configuration → General configuration**.

---

# Step 7: Test the Lambda Function

Click:

```text
Test
```

Create a new test event.

Event JSON:

```json
{}
```

Click **Test**.

Expected output:

```json
{
  "statusCode": 200,
  "InstanceId": "i-0123456789abcdef0",
  "SnapshotId": "snap-0123456789abcdef0",
  "AMI": "ami-0123456789abcdef0"
}
```

📸 **Screenshot 6:** Successful Test Execution.

---

# Step 8: Verify the Restored Instance

Go to:

```text
EC2
→ Instances
```

Verify that:

- A new EC2 instance has been created.
- Instance state is **Running**.
- Instance type is **t3.micro**.

Open the **Tags** tab.

Expected tag:

| Key | Value |
|------|-------|
| RestoredFrom | snap-xxxxxxxx |

📸 **Screenshot 7:** Restored EC2 Instance.

---

# Step 9: Verify the Data

Connect to the restored EC2 instance using **EC2 Instance Connect** or **SSH**.

Verify that the files and data stored on the original root EBS volume are present on the restored instance.

📸 **Screenshot 8:** Restored Data Verification.

---

# Step 10: Verify CloudWatch Logs

Go to:

```text
Lambda
→ Monitor
→ View CloudWatch Logs
```

Expected output:

```text
Latest Snapshot: snap-0123456789abcdef0
AMI Created: ami-0123456789abcdef0
AMI is now available
New Instance Created: i-0123456789abcdef0
```

📸 **Screenshot 9:** CloudWatch Logs.

---

# Step 11: GitHub Repository Structure

```text
aws-lambda-boto3-assignments/
│
├── 05-restore-ec2-from-snapshot/
│   ├── lambda_function.py
│   ├── iam_policy.json
│   ├── README.md
│   └── screenshots/
│       ├── 01-existing-snapshot.png
│       ├── 02-iam-role.png
│       ├── 03-inline-policy.png
│       ├── 04-lambda-config.png
│       ├── 05-lambda-code.png
│       ├── 06-test-output.png
│       ├── 07-restored-instance.png
│       ├── 08-restored-data.png
│       └── 09-cloudwatch-logs.png
```

---

# Discussion

Creating an AMI from the latest EBS snapshot and launching a new EC2 instance automates disaster recovery. This approach helps quickly restore workloads after failures, minimizes downtime, and ensures consistent recovery from the most recent backup. In production environments, this process can be integrated with EventBridge, AWS Backup, or disaster recovery workflows for automated recovery.

---

# Step 12: Clean Up Resources

After capturing all required screenshots:

- Terminate the restored EC2 instance.
- Deregister the AMI created during testing.
- Delete the test AMI snapshots if they are no longer needed.
- Delete the Lambda function if it was created only for this assignment.
- Delete the IAM role if it was created only for this assignment.

This helps prevent unnecessary AWS charges.

---

# Deliverables

Your GitHub folder should contain:

- `lambda_function.py`
- `iam_policy.json`
- `README.md`
- Screenshots of:
  - Existing Snapshot
  - IAM Role
  - Inline Policy
  - Lambda Configuration
  - Lambda Code
  - Test Output
  - Restored EC2 Instance
  - Restored Data Verification
  - CloudWatch Logs
- GitHub Repository Link

This completes **Assignment 5: Restore an EC2 Instance from the Latest Snapshot** according to the assignment requirements.
