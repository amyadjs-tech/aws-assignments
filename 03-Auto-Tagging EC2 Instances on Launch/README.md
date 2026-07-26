# Assignment 3: Auto-Tagging EC2 Instances on Launch

## Objective

Automatically tag newly launched EC2 instances for **resource tracking, ownership, and cost allocation** using **AWS Lambda**, **Amazon EventBridge**, and **Boto3**.

---

# Step 1: Login to AWS

1. Sign in to the **AWS Management Console**.
2. Select one AWS Region for the assignment (recommended: **us-east-1**).

---

# Step 2: Create an IAM Role for Lambda

## 2.1 Open IAM

- Go to **IAM Console**
- Click **Roles**
- Click **Create Role**

## 2.2 Select Trusted Entity

Choose:

- **Trusted Entity:** AWS Service
- **Use Case:** Lambda

Click **Next**.

## 2.3 Attach AWS Managed Policy

Attach the following managed policy:

```text
AWSLambdaBasicExecutionRole
```

This policy allows Lambda to write logs to CloudWatch.

Click **Next**.

## 2.4 Role Name

Enter:

```text
LambdaEC2AutoTagRole
```

Click **Create Role**.

📸 **Screenshot 1:** IAM Role Created.

---

# Step 3: Create an Inline IAM Policy

Open the newly created role.

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
        "ec2:CreateTags",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

Click **Next**.

Policy Name:

```text
EC2AutoTagPolicy
```

Click **Create Policy**.

📸 **Screenshot 2:** Inline Policy.

---

# Step 4: Create the Lambda Function

Go to **AWS Lambda**.

Click:

```text
Create Function
```

Choose:

```text
Author from Scratch
```

Fill in the following details:

| Setting | Value |
|---------|-------|
| Function Name | EC2AutoTagLambda |
| Runtime | Python 3.12 |
| Architecture | x86_64 |
| Execution Role | Use Existing Role |
| Existing Role | LambdaEC2AutoTagRole |

Click **Create Function**.

📸 **Screenshot 3:** Lambda Configuration.

---

# Step 5: Add the Lambda Code

Replace the default code with the following:

```python
import boto3
from datetime import datetime

ec2 = boto3.client("ec2")

def lambda_handler(event, context):

    # Extract Instance ID from EventBridge event
    instance_id = event["detail"]["instance-id"]

    # Get today's date
    launch_date = datetime.utcnow().strftime("%Y-%m-%d")

    # Add tags to the instance
    ec2.create_tags(
        Resources=[instance_id],
        Tags=[
            {
                "Key": "LaunchDate",
                "Value": launch_date
            },
            {
                "Key": "Environment",
                "Value": "Development"
            }
        ]
    )

    print(f"Successfully tagged instance: {instance_id}")

    return {
        "statusCode": 200,
        "InstanceId": instance_id
    }
```

Click **Deploy**.

📸 **Screenshot 4:** Lambda Code.

---

# Step 6: Create the EventBridge Rule

Go to:

```text
Amazon EventBridge
→ Rules
→ Create Rule
```

## Rule Details

Enter the following details:

| Setting | Value |
|---------|-------|
| Name | EC2-Auto-Tagging |
| Description | (Optional) Automatically tag EC2 instances on launch |
| Event Bus | Default |
| Rule Status | Enabled |
| Builder Mode | Advanced builder |

> **Note:** In the latest AWS EventBridge console, the **Rule Type** option has been replaced by **Builder Mode**. Select **Advanced builder** to create a rule using a custom JSON event pattern.

Click **Next**.

### Build Event Pattern

Under **Event Source**, select:

```text
Other
```

Choose:

```text
Custom pattern (JSON editor)
```

Paste the following JSON:

```json
{
  "source": [
    "aws.ec2"
  ],
  "detail-type": [
    "EC2 Instance State-change Notification"
  ],
  "detail": {
    "state": [
      "running"
    ]
  }
}
```

Verify the console displays:

```text
JSON is valid
```

Click **Next**.

📸 **Screenshot 5:** Event Pattern Configuration.

### Select Target

Configure the target as follows:

| Setting | Value |
|---------|-------|
| Target Type | AWS Service |
| Target | Lambda Function |
| Function | EC2AutoTagLambda |
| Input | Matched Event |

> The **Matched Event** option passes the complete EventBridge event to the Lambda function. This allows the Lambda code to extract the EC2 instance ID using:
>
> ```python
> event["detail"]["instance-id"]
> ```

Click **Next**.

### Configure Tags (Optional)

This step is used to tag the **EventBridge rule itself**, not the EC2 instance.

You can leave this section empty and click **Next**.

### Review and Create

Review the configuration:

- Rule Name: **EC2-Auto-Tagging**
- Event Bus: **Default**
- Event Pattern:
  - Source: `aws.ec2`
  - Detail Type: `EC2 Instance State-change Notification`
  - State: `running`
- Target: **EC2AutoTagLambda**
- Input: **Matched Event**

Click **Create Rule**.

📸 **Screenshot 6:** EventBridge Rule Created Successfully.

---

# Step 7: Test the Assignment

Launch a new EC2 instance.

Recommended configuration:

- Amazon Linux 2023 AMI
- t3.micro
- Default VPC
- Default Security Group

Wait until the instance reaches the **Running** state.

---

# Step 8: Verify the Tags

Go to:

```text
EC2
→ Instances
```

Select the newly launched EC2 instance.

Open the **Tags** tab.

You should see tags similar to:

| Key | Value |
|------|-------|
| LaunchDate | 2026-07-26 |
| Environment | Development |

📸 **Screenshot 7:** EC2 Instance Tags.

---

# Step 9: Verify CloudWatch Logs

Go to:

```text
Lambda
→ Monitor
→ View CloudWatch Logs
```

Expected log output:

```text
Successfully tagged instance: i-0123456789abcdef0
```

📸 **Screenshot 8:** CloudWatch Logs.

---

# Step 10: Bonus (Interview Scenario)

Instead of using a fixed value for the **Owner** tag, you can automatically determine who launched the EC2 instance.

### How it works

1. Enable **AWS CloudTrail**.
2. Capture the **RunInstances** API event.
3. Read the IAM user or assumed role from the CloudTrail event.
4. Add an additional tag such as:

| Key | Value |
|------|-------|
| LaunchDate | 2026-07-26 |
| Environment | Development |
| Owner | amya |

> **Note:** In a production environment, the **Owner** value should be dynamically extracted from the CloudTrail event rather than hardcoded.

This approach improves:

- Resource ownership tracking
- Cost allocation
- Auditing
- Security compliance

---

# Step 11: GitHub Repository Structure

```text
aws-lambda-boto3-assignments/
│
├── 03-ec2-auto-tagging/
│   ├── lambda_function.py
│   ├── iam_policy.json
│   ├── README.md
│   └── screenshots/
│       ├── 01-iam-role.png
│       ├── 02-inline-policy.png
│       ├── 03-lambda-config.png
│       ├── 04-lambda-code.png
│       ├── 05-event-pattern.png
│       ├── 06-eventbridge-rule.png
│       ├── 07-ec2-tags.png
│       └── 08-cloudwatch-logs.png
```

---

# Discussion

Automatically tagging EC2 instances ensures that every instance has consistent metadata such as launch date, environment, and owner. This simplifies resource management, improves cost allocation, supports governance policies, and makes auditing easier. Lambda with EventBridge provides a flexible solution for automatically applying tags based on EC2 instance state change events.

---

# Step 12: Clean Up Resources

After capturing all required screenshots:

- Terminate the test EC2 instance.
- Delete the EventBridge Rule.
- Delete the Lambda Function if it is no longer required.
- Delete the IAM Role if it was created only for this assignment.

This helps avoid unnecessary AWS charges.

---

# Deliverables

Your GitHub folder should contain:

- `lambda_function.py`
- `iam_policy.json`
- `README.md`
- Screenshots of:
  - IAM Role
  - Inline Policy
  - Lambda Configuration
  - Lambda Code
  - Event Pattern
  - EventBridge Rule
  - EC2 Instance Tags
  - CloudWatch Logs
- GitHub Repository Link

This completes **Assignment 3: Auto-Tagging EC2 Instances on Launch** according to the assignment requirements.
