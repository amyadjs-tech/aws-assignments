# Assignment 2: Automated EBS Snapshot Creation and Cleanup

## Objective

Automate EBS volume backups by:

- Creating a snapshot of an EBS volume.
- Tagging the snapshot.
- Deleting snapshots older than 30 days.
- Logging the created and deleted snapshot IDs.
- Scheduling the Lambda function to run weekly.

---

# Step 1: Login to AWS

1. Login to the AWS Management Console.
2. Select one AWS Region for the entire assignment (recommended: **us-east-1**).

---

# Step 2: Create an EC2 Instance (if needed)

If you already have an EC2 instance with an attached EBS volume, you can skip this step.

1. Open the **EC2 Console**.
2. Click **Launch Instance**.
3. Select **Amazon Linux 2023 AMI**.
4. Choose the instance type:

```text
t3.micro
```

5. Launch the instance.

---

# Step 3: Find the EBS Volume ID

1. Open the **EC2 Console**.
2. Select **Volumes**.
3. Locate the attached EBS volume.
4. Copy the **Volume ID**.

Example:

```text
vol-0123456789abcdef0
```

📸 **Screenshot 1:** EC2 Volume with Volume ID.

---

# Step 4: Create the IAM Role

Navigate to:

```text
IAM
→ Roles
→ Create Role
```

Choose:

```text
AWS Service
Lambda
```

Attach the managed policy:

```text
AWSLambdaBasicExecutionRole
```

Role Name:

```text
LambdaEBSBackupRole
```

---

# Step 5: Create the Least-Privilege IAM Policy

Navigate to:

```text
Permissions
→ Add Inline Policy
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
        "ec2:CreateSnapshot",
        "ec2:DescribeSnapshots",
        "ec2:DeleteSnapshot",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

Policy Name:

```text
EBSBackupPolicy
```

📸 **Screenshot 2:** IAM Role with Inline Policy.

---

# Step 6: Create the Lambda Function

Go to:

```text
Lambda
→ Create Function
```

Choose:

```text
Author from Scratch
```

Configure the function:

| Setting | Value |
|---------|-------|
| Function Name | EBSBackupCleanupLambda |
| Runtime | Python 3.12 |
| Execution Role | LambdaEBSBackupRole |

Click **Create Function**.

📸 **Screenshot 3:** Lambda Configuration.

---

# Step 7: Replace the Default Code

Replace the default Lambda code with the following:

```python
import boto3
from datetime import datetime, timezone, timedelta

ec2 = boto3.client("ec2")

VOLUME_ID = "vol-08d5ea27230084df8"

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
```

Replace:

```python
VOLUME_ID = "vol-0123456789abcdef0"
```

with your actual EBS Volume ID.

Click **Deploy**.

---

# Step 8: Testing

Click:

```text
Test
```

Create a new test event.

Event JSON:

```json
{}
```

Save the test event and click **Test**.

Expected output:

```json
{
  "CreatedSnapshot": "snap-0123456789",
  "DeletedSnapshots": []
}
```

📸 **Screenshot 4:** Successful Test Invocation.

---

# Step 9: Verify Snapshot

Go to:

```text
EC2
→ Snapshots
```

Verify a new snapshot has been created.

The snapshot should contain the tag:

```text
CreatedBy = Lambda-Backup
```

📸 **Screenshot 5:** Snapshot created successfully.

---

# Step 10: Configure EventBridge

Navigate to:

```text
Amazon EventBridge
→ Rules
→ Create Rule
```

Configure:

| Setting | Value |
|---------|-------|
| Rule Name | Weekly-EBS-Backup |
| Rule Type | Schedule |

Cron Expression:

```text
cron(0 2 ? * SUN *)
```

This runs every Sunday at **02:00 UTC**.

Target:

```text
Lambda
→ EBSBackupCleanupLambda
```

Save the rule.

📸 **Screenshot 6:** EventBridge Rule.

---

# Step 11: CloudWatch Logs

Navigate to:

```text
Lambda
→ Monitor
→ View CloudWatch Logs
```

Example log output:

```text
Created Snapshot:
snap-0123456789

Deleted Snapshot:
snap-9876543210
```

📸 **Screenshot 7:** CloudWatch Logs.

---

# Step 12: GitHub Repository Structure

```text
aws-lambda-boto3-assignments/
│
├── 02-ebs-snapshot-cleanup/
│   ├── lambda_function.py
│   ├── iam_policy.json
│   ├── README.md
│   └── screenshots/
│       ├── 01-ebs-volume.png
│       ├── 02-iam-role.png
│       ├── 03-lambda-config.png
│       ├── 04-test-output.png
│       ├── 05-created-snapshot.png
│       ├── 06-eventbridge-rule.png
│       └── 07-cloudwatch-logs.png
```

---

# Step 13: Documentation Discussion

> AWS Data Lifecycle Manager (DLM) is the preferred solution for automated EBS snapshot creation and retention because it is fully managed and requires minimal configuration. Lambda is more suitable when backup policies require custom retention logic, cross-account or cross-region snapshot copies, conditional tagging, notifications, or integration with other AWS services.

---

# Step 14: Clean Up Resources

After capturing all required screenshots:

- Delete the test snapshots.
- Delete the EventBridge rule.
- Delete the Lambda function.
- Delete the IAM role.
- Terminate the EC2 instance if it was created only for this assignment.

This prevents unnecessary AWS charges and follows AWS cost management best practices.

---

## Deliverables

- ✅ `lambda_function.py`
- ✅ `iam_policy.json`
- ✅ `README.md`
- ✅ Screenshots:
  - IAM Role
  - Lambda Configuration
  - Test Invocation
  - Created Snapshot
  - EventBridge Rule
  - CloudWatch Logs
- ✅ GitHub Repository Link
