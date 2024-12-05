def handler(event, context):
    print("Event received in Lambda Function 2:", event)
    return {"statusCode": 200, "body": "Hello from Lambda 2"}