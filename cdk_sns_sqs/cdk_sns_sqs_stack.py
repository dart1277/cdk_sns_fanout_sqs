import os

from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_kms as kms,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as event_sources, Duration,
    aws_apigateway as apigateway, CfnOutput,
)
from constructs import Construct


class CdkSnsSqsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkSnsSqsQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        # Create a custom KMS Key
        kms_key_sns = kms.Key(
            self, "CustomKmsKey",
            enable_key_rotation=True,
            alias="alias/custom-sns"
        )

        kms_key_sqs = kms.Key(
            self, "CustomKmsKey2",
            enable_key_rotation=True,
            alias="alias/custom-sqs"
        )

        # Create a KMS encrypted SNS Topic
        sns_topic = sns.Topic(
            self, "KmsEncryptedTopic",
            topic_name="in-topic",
            master_key=kms_key_sns,
            enforce_ssl=True,
        )


        # Create the first KMS encrypted SQS Queue
        sqs_queue_1 = sqs.Queue(
            self, "KmsEncryptedQueue1",
            queue_name="out-queue-1",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=kms_key_sqs,
            enforce_ssl=True,
            retention_period=Duration.days(14),
            visibility_timeout=Duration.seconds(30),
        )


        # Create the second KMS encrypted SQS Queue
        sqs_queue_2 = sqs.Queue(
            self, "KmsEncryptedQueue2",
            queue_name="out-queue-2",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=kms_key_sqs,
            enforce_ssl=True,
            retention_period=Duration.days(14),
            visibility_timeout=Duration.seconds(30),
        )


        # Subscribe the SQS Queues to the SNS Topic
        sns_topic.add_subscription(subscriptions.SqsSubscription(sqs_queue_1))
        sns_topic.add_subscription(subscriptions.SqsSubscription(sqs_queue_2))

        # Lambda code directory
        lambda_code_dir = os.path.join(os.path.dirname(__file__), "lambda_code")

        # Create the first Lambda function
        lambda_function_1 = _lambda.Function(
            self, "LambdaFunction1",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="lambda_function_1.handler",
            code=_lambda.Code.from_asset(os.path.join(lambda_code_dir, "lambda_function_1"))
        )

        # Add SQS Queue as an event source for the first Lambda function
        lambda_function_1.add_event_source(
            event_sources.SqsEventSource(sqs_queue_1)
        )

        # Create the second Lambda function
        lambda_function_2 = _lambda.Function(
            self, "LambdaFunction2",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="lambda_function_2.handler",
            code=_lambda.Code.from_asset(os.path.join(lambda_code_dir, "lambda_function_2"))
        )

        # Add SQS Queue as an event source for the second Lambda function
        lambda_function_2.add_event_source(
            event_sources.SqsEventSource(sqs_queue_2)
        )

        kms_key_sqs.grant_decrypt(lambda_function_2)
        kms_key_sqs.grant_decrypt(lambda_function_1)

        # Create a Lambda function to publish messages to SNS
        sns_publisher_function = _lambda.Function(
            self, "SnsPublisherFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="sns_proxy.handler",
            code=_lambda.Code.from_asset(os.path.join(lambda_code_dir, "sns_proxy")),
            environment={
                "TOPIC_ARN": sns_topic.topic_arn
            }
        )

        # Grant Lambda permission to publish to the SNS topic
        sns_topic.grant_publish(sns_publisher_function)
        kms_key_sns.grant_encrypt_decrypt(sns_publisher_function)

        # # Create a REST API Gateway
        # api = apigateway.RestApi(
        #     self, "RestApi",
        #     rest_api_name="PayloadToSnsApi",
        #     description="API Gateway to forward POST payloads to an SNS topic"
        # )
        #
        # # Create the '/send' resource
        # send_resource = api.root.add_resource("send")
        #
        # # Add HTTP POST method to '/send' resource, integrated with Lambda
        # send_resource.add_method(
        #     "POST",
        #     apigateway.LambdaIntegration(sns_publisher_function),
        #     method_responses=[
        #         apigateway.MethodResponse(status_code="200"),
        #         apigateway.MethodResponse(status_code="500")
        #     ]
        # )
        #
        # CfnOutput(self, "ObjectKey",
        #           key="ApiUrl",
        #           value=api.url,
        #           description="API URL"
        #           )
