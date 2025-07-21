import pytest
import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from rearc_pipeline.rearc_pipeline_stack import RearcPipelineStack

@pytest.mark.parametrize("environment,expected_bucket_name", [
    ("dev", "rearc-dev-datalake"),
    ("prod", "rearc-prod-dataLake"),
])
def test_stack_resources(environment, expected_bucket_name):
    app = cdk.App()
    stack = RearcPipelineStack(app, f"{environment}-Test", environment=environment)
    template = Template.from_stack(stack)

    # Assert SQS Queue with VisibilityTimeout = 310 exists
    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 310
    })

    # Use Match.object_like to partially match the Lambda properties
    template.resource_count_is("AWS::Lambda::Function", 2)
    template.has_resource_properties("AWS::Lambda::Function", Match.object_like({
        "Handler": "handler.main",
        "Environment": {
            "Variables": {
                "BUCKET_NAME": expected_bucket_name
            }
        }
    }))

    # EventBridge Rule with rate(1 day)
    template.has_resource_properties("AWS::Events::Rule", {
        "ScheduleExpression": "rate(1 day)"
    })

    # One Event Source Mapping exists
    template.resource_count_is("AWS::Lambda::EventSourceMapping", 1)
