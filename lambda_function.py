import json
from botocore.exceptions import ClientError
import boto3
from datetime import datetime, timedelta, timezone
import os
REGION = "us-east-1"
RETENTION_DAYS = 7
ec2_client = boto3.client('ec2',region_name=REGION)
def lambda_handler(event, context):
    try:
        try:
            ec2_instances = ec2_client.describe_instances(
            Filters=[{"Name":"tag:Backup","Values":["true"]}])
        except ClientError as e:
            print("Error fetching EC2 metadata")

        try:
            for reservation in ec2_instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']

                    for device in instance['BlockDeviceMappings']:
                        volume_id = device['Ebs']['VolumeId']
                        description = f"Backup of {instance_id} volume {volume_id}"

                        snapshot = ec2_client.create_snapshot(Description=description,VolumeId=volume_id,Tags=[{"ResourceType":"snapshot"},{"CreatedBy":"Auto-Backup-EC2"},{"InstanceId":instance_id}])

                        print(f"created snapshot {snapshot['SnapshotId']} for volume {volume_id}")
        except ClientError as e:
            print("Error creating snapshots")

        delete_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        try:
            old_backups = ec2_client.describe_snapshots(Filters=[{"Name":"tag:CreatedBy",Values:["Auto-Backup-EC2"]}])
        except ClientError as e:
            print("Error fetching old snapshots")


        try:
            for snapshot in old_backups['Snapshots']:
                if snapshot['StartTime']<delete_date:
                    print(f"Deleting old snapshot {snapshot["SnapshotId"]}")
                    ec2_client.delete_snapshot(SnapshotId = snapshot['SnapshotId'])
        except ClientError as e:
            print("Error Deleting old snapshots")
            
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        sns = boto3.client("sns")
        SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
        sns.publish(TopicArn=SNS_TOPIC_ARN,Subject="Pipeline Error: EC2 Backup",Message=f"Lambda error in EC2 Backup Pipeline\n\n {str(e)}")
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error on server.')
        }

