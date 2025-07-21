import aws_cdk as core
import aws_cdk.assertions as assertions

from rearc_pipeline.rearc_pipeline_stack import RearcPipelineStack
from cicd_pipeline_stack import CICDPipelineStack

def test_sqs_queue_created():
    app = core.App()
    # Pass environment argument (example: 'dev' or actual environment dict)
    stack = RearcPipelineStack(app, "TestStack", environment="dev")
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })

def test_rearc_pipeline_stack():
    app = core.App()
    stack = RearcPipelineStack(app, "TestStack", environment="dev")
    template = assertions.Template.from_stack(stack)
    template.has_resource("AWS::S3::Bucket", {})  # add empty dict for props

def test_cicd_pipeline_stack():
    app = core.App()
    stack = CICDPipelineStack(app, "TestPipelineStack")
    template = assertions.Template.from_stack(stack)
    template.has_resource("AWS::CodePipeline::Pipeline", {})  # add empty dict for props
