import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from rearc_pipeline.rearc_pipeline_stack import RearcPipelineStack

@pytest.mark.parametrize("environment,expected_bucket_name", [
    ("dev", "rearc-dev-datalake"),
    ("prod", "rearc-prod-datalake"),
])
def test_stack_resources(environment, expected_bucket_name):
    app = cdk.App()
    stack = RearcPipelineStack(app, f"{environment}-Test", environment=environment)
    template = Template.from_stack(stack)

    # Assert SQS Queue exists with correct visibility timeout
    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 310
    })

    # Assert two Lambda functions exist (you created two)
    template.resource_count_is("AWS::Lambda::Function", 2)

    # Match at least one Lambda with correct environment and handler (partial match)
    template.has_resource_properties("AWS::Lambda::Function", Match.object_like({
        "Handler": "handler.main",
        "Environment": Match.object_like({
            "Variables": Match.object_like({
                "BUCKET_NAME": expected_bucket_name
            })
        })
    }))

    # Assert EventBridge Rule exists
    template.has_resource_properties("AWS::Events::Rule", {
        "ScheduleExpression": "rate(1 day)"
    })

    # Assert SQS is used as Lambda event source
    template.resource_count_is("AWS::Lambda::EventSourceMapping", 1)
