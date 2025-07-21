import pytest
import aws_cdk as cdk
from aws_cdk.assertions import Template

from rearc_pipeline.rearc_pipeline_stack import RearcPipelineStack

@pytest.mark.parametrize("environment,expected_bucket_name", [
    ("dev", "rearc-dev-datalake"),
    ("prod", "reac-prod-dataLake"),
])
def test_stack_resources(environment, expected_bucket_name):
    app = cdk.App()
    stack = RearcPipelineStack(app, f"{environment}-Test", environment=environment)
    template = Template.from_stack(stack)

    # Assert SQS Queue exists with correct VisibilityTimeout
    assert template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 310
    }), "SQS Queue with VisibilityTimeout=310 not found"

    # Find all Lambda functions with specified handler and bucket environment variable
    lambdas = template.find_resources("AWS::Lambda::Function", {
        "Handler": "handler.main",
        "Environment": {
            "Variables": {
                "BUCKET_NAME": expected_bucket_name
            }
        }
    })

    # Assert exactly 2 such Lambda functions exist
    assert len(lambdas) == 2, f"Expected 2 Lambda functions but found {len(lambdas)}"

    # Assert EventBridge rule exists with the daily schedule
    assert template.has_resource_properties("AWS::Events::Rule", {
        "ScheduleExpression": "rate(1 day)"
    }), "EventBridge rule with daily schedule not found"

    # Assert exactly one Lambda event source mapping exists
    count = template.resource_count("AWS::Lambda::EventSourceMapping")
    assert count == 1, f"Expected 1 Lambda EventSourceMapping but found {count}"
