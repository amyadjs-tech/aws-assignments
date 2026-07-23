# Automated S3 Bucket Cleanup Using AWS Lambda and Boto3

## Objective

This project automates the cleanup of Amazon S3 objects older than **30 days** using **AWS Lambda**, **Python 3.12**, **Boto3**, **IAM Least Privilege**, and **CloudWatch Logs**.

---

# AWS Services Used

- Amazon S3
- AWS Lambda
- IAM
- CloudWatch Logs
- Boto3 (Python SDK)

---

# Architecture

```
S3 Bucket
     │
     ▼
AWS Lambda (Python 3.12)
     │
     ▼
List Objects using Boto3 Paginator
     │
     ▼
Delete Objects Older Than 30 Days
     │
     ▼
CloudWatch Logs
```

---

# Step 1: Login to AWS

1. Login to the AWS Management Console.
2. Select the region:

```
us-east-1 (N. Virginia)
```

---

# Step 2: Create an S3 Bucket

Navigate to:

```
Amazon S3
→ Create Bucket
```

Bucket Name:

```
amya-s3-cleanup-demo-2026
```

Keep all default settings and create the bucket.

### Upload Sample Files

Example:

```
Hello.txt
Hi.txt
image.png
notes.docx
```

---

## Screenshot

![S3 Bucket](screenshots/01-s3-bucket.png)

---

# Step 3: Create IAM Role

Navigate to:

```
IAM
→ Roles
→ Create Role
```

Choose:

- AWS Service
- Lambda

Role Name:

```
LambdaS3CleanupRole
```

Attach Managed Policy:

```
AWSLambdaBasicExecutionRole
```

---

# Step 4: Create Least Privilege Inline Policy

Navigate to:

```
Permissions
→ Add Inline Policy
→ JSON
```

Paste the following policy.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::amya-s3-cleanup-demo-2026"
    },
    {
      "Effect": "Allow",
      "Action": "s3:DeleteObject",
      "Resource": "arn:aws:s3:::amya-s3-cleanup-demo-2026/*"
    }
  ]
}
```

Policy Name:

```
S3CleanupPolicy
```

---

## Screenshot

![IAM Role](screenshots/01-iam-role.png)

---

# Step 5: Create Lambda Function

Navigate to:

```
Lambda
→ Create Function
```

Configuration

| Setting | Value |
|----------|-------|
| Function Name | S3CleanupLambda |
| Runtime | Python 3.12 |
| Execution Role | LambdaS3CleanupRole |

---

## Screenshot

![Lambda Configuration](screenshots/02-lambda-config.png)

---

# Step 6: Lambda Function Code

Create `lambda_function.py`

```python
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
```

Deploy the Lambda function.

---

# Step 7: Testing

For testing purposes, temporarily change:

```python
AGE_DAYS = 0
```

Deploy again.

---

# Step 8: Create Test Event

Create a test event with the following JSON:

```json
{}
```

Save the event.

---

# Step 9: Invoke Lambda

Click **Test**.

Expected Output

```json
{
  "statusCode": 200,
  "deletedObjects": [
    "Hello.txt",
    "Hi.txt"
  ]
}
```

---

## Screenshot

![Lambda Test](screenshots/03-test-invocation.png)

---

# Step 10: Verify S3 Bucket

Before Cleanup

```
Hello.txt
Hi.txt
image.png
notes.docx
```

After Cleanup

```
notes.docx
```

---

## Screenshot

![Final Bucket](screenshots/05-final-result.png)

---

# Step 11: CloudWatch Logs

Navigate to:

```
Lambda
→ Monitor
→ View CloudWatch Logs
```

Example Log Output

```
Deleted: Hello.txt
Deleted: Hi.txt
Deleted: image.png
```

---

## Screenshot

![CloudWatch Logs](screenshots/04-cloudwatch-logs.png)

---

# Step 12: Restore Final Code

Before submission, change:

```python
AGE_DAYS = 30
```

Deploy the function again.

---

# Repository Structure

```
aws-lambda-boto3-assignments/
│
├── README.md
│
└── 01-s3-bucket-cleanup/
    ├── lambda_function.py
    ├── iam_policy.json
    ├── README.md
    └── screenshots/
        ├── 01-s3-bucket.png
        ├── 01-iam-role.png
        ├── 02-lambda-config.png
        ├── 03-test-invocation.png
        ├── 04-cloudwatch-logs.png
        └── 05-final-result.png
```

---

# Discussion

### Why use Amazon S3 Lifecycle Rules?

Amazon S3 Lifecycle Rules are the preferred solution for simple age-based object deletion because they are fully managed, require no code, and are cost-effective.

### Why use AWS Lambda?

AWS Lambda is useful when deletion depends on:

- Object metadata
- File name patterns
- Custom business logic
- Notifications after deletion
- Integration with other AWS services

---

# Cleanup

After completing the assignment:

- Delete test objects from the S3 bucket.
- Delete the S3 bucket.
- Delete the Lambda function.
- Delete the IAM role (if created only for this assignment).

---

# Author

**Amya Prakash Behera**

GitHub: https://github.com/amyadjs-tech

Project: **AWS Lambda Automation using Boto3**
