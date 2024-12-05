import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_sns_sqs.cdk_sns_sqs_stack import CdkSnsSqsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_sns_sqs/cdk_sns_sqs_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkSnsSqsStack(app, "cdk-sns-sqs")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
