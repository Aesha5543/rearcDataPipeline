from aws_cdk import Stage
from constructs import Construct
from rearc_pipeline.rearc_pipeline_stack import RearcPipelineStack

class ProdStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        RearcPipelineStack(self, "RearcProdStack", environment="prod")