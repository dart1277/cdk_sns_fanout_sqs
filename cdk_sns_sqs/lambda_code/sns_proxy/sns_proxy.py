import json
import boto3
import os

sns_client = boto3.client('sns')
topic_arn = os.environ['TOPIC_ARN']


def handler(event, context):
    try:
        # Extract payload from HTTP POST request body
        body = json.loads(event['body'])

        # Publish the payload to the SNS topic
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(body)  # Convert payload to JSON string
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Payload sent to SNS topic", "response": response})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
