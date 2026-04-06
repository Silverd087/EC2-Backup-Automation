# EC2 Automated Backup & Retention Pipeline

A serverless AWS solution designed to automate EBS snapshots for tagged EC2 instances and manage storage costs by enforcing a 7-day retention policy.

## 🚀 Overview
This project uses **AWS Lambda** and **Amazon EventBridge** to create a hands-off backup system. Instead of manually creating snapshots, the system scans your infrastructure for a specific tag and handles the lifecycle of the data automatically.

### Key Features
* **Tag-Based Selection**: Only backs up instances with the `Backup: true` tag.
* **Automated Lifecycle**: Automatically deletes snapshots older than 7 days to prevent unexpected AWS billing.
* **Failure Notifications**: Integrated with **Amazon SNS** to alert administrators if the backup fails.
* **Region Specific**: Configured for `us-east-1` (easily adjustable).

---

## 🛠 Architecture
The architecture follows a serverless event-driven pattern. You can visualize the flow using the diagram below:

![Architecture Diagram](./architecture-diagram.png)

1. **EventBridge (Trigger)**: Fires a Cron schedule (e.g., daily at midnight).
2. **AWS Lambda (Logic)**: The central engine that identifies instances, creates snapshots, and prunes old data.
3. **Amazon SNS (Alerts)**: Sends an error report if any part of the execution fails.

---

## 📋 Prerequisites
* **AWS CLI** configured with appropriate credentials.
* **IAM Role Permissions**: Your Lambda role must have a policy allowing the following actions:
    * `ec2:DescribeInstances`
    * `ec2:CreateSnapshot`
    * `ec2:DescribeSnapshots`
    * `ec2:DeleteSnapshot`
    * `ec2:CreateTags`
    * `sns:Publish`
    * `logs:CreateLogGroup`, `logs:CreateLogStream`, and `logs:PutLogEvents`
* **SNS Topic**: An SNS Topic ARN created and subscribed to your email for error notifications.

---

## ⚙️ Configuration
The behavior of the pipeline can be adjusted using these variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| **REGION** | The AWS region where your instances reside. | `us-east-1` |
| **RETENTION_DAYS** | How many days to keep a snapshot before deletion. | `7` |
| **SNS_TOPIC_ARN** | The ARN for your error notification topic (Environment Variable). | *Required* |

---

## 📖 Usage

### 1. Tag your Instances
Add the following tag to any EC2 instance you want to include in the backup cycle:
* **Key**: `Backup`
* **Value**: `true`

### 2. Deploy the Lambda
* Create a new Lambda function with the **Python 3.12** runtime.
* Copy the Python script into the function editor.
* Under the **Configuration** tab, add an Environment Variable named `SNS_TOPIC_ARN`.
* **Important:** Go to "General Configuration" and increase the **Timeout** to **1 minute**.

### 3. Set the Schedule
* Navigate to **Amazon EventBridge** > **Schedules**.
* Create a new schedule using a Cron expression (e.g., `cron(0 0 * * ? *)` for midnight).
* Select your Lambda function as the target.

### 4. Monitor
Check **CloudWatch Logs** for execution details. If a backup fails, an alert will be sent to the email or phone number subscribed to your SNS Topic.

