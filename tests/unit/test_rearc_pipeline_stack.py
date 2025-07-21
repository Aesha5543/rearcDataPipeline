import pytest
import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from rearc_pipeline.rearc_pipeline_stack import RearcPipelineStack

@pytest.mark.parametrize("environment,expected_bucket_name", [
    ("dev", "Dev-DataLake"),
    ("prod", "Prod-DataLake"),
])

def test_stack_resources(environment, expected_bucket_name):
    app = cdk.App()
    stack = RearcPipelineStack(app, f"{environment}-Test", environment=environment)
    template = Template.from_stack(stack)

    # Check SQS Queue exists
    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 310
    })

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

    # Check EventBridge Rule exists
    template.has_resource_properties("AWS::Events::Rule", {
        "ScheduleExpression": "rate(1 day)"
    })

    # Check Lambda Event Source Mapping exists
    template.resource_count_is("AWS::Lambda::EventSourceMapping", 1)