import pytest
import aws_cdk as cdk
from aws_cdk.assertions import Template

from rearc_pipeline.rearc_pipeline_stack import RearcPipelineStack

@pytest.mark.parametrize("environment,expected_bucket_name", [
    ("dev", "rearc-dev-datalake"),
    ("prod", "rearc-prod-dataLake"),
])

def test_stack_resources(environment, expected_bucket_name):
    app = cdk.App()
    stack = RearcPipelineStack(app, f"{environment}-Test", environment=environment)
    template = Template.from_stack(stack)

    #SQS Queue with VisibilityTimeout = 310 exists
    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 310
    })

    #Lambda Functions exist with given handler and environment variable
    lambdas = template.find_resources("AWS::Lambda::Function", {
        "Handler": "handler.main",
        "Environment": {
            "Variables": {
                "BUCKET_NAME": expected_bucket_name
            }
        }
    })
    assert len(lambdas) == 2, f"Expected 2 Lambda functions but found {len(lambdas)}"

    #Assert EventBridge Rule with rate(1 day)
    template.has_resource_properties("AWS::Events::Rule", {
        "ScheduleExpression": "rate(1 day)"
    })

    #Assert one Lambda Event Source Mapping exists
    count = template.resource_count("AWS::Lambda::EventSourceMapping")
    assert count == 1, f"Expected 1 EventSourceMapping, but found {count}"
