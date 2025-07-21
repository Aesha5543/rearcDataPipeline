from aws_cdk import Stack, pipelines, SecretValue
from constructs import Construct
from stages.dev_stage import DevStage
from stages.prod_stage import ProdStage

class CICDPipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        source = pipelines.CodePipelineSource.git_hub(
            "Aesha5543/rearcDataPipeline",
            "main",
            authentication=SecretValue.secrets_manager("github-token")
        )

        pipeline = pipelines.CodePipeline(self, "Pipeline",
            pipeline_name="RearcCICD",
            synth=pipelines.ShellStep("Synth",
                input=source,
                install_commands=["npm install -g aws-cdk", "pip install -r requirements.txt"],
                commands=["cdk synth"]
            )
        )

        test_step = pipelines.ShellStep("RunUnitTests",
            input=source,
            install_commands=["pip install -r requirements.txt"],
            commands=["pytest tests/unit"]
        )

        dev_stage = DevStage(self, "DevStage")
        prod_stage = ProdStage(self, "ProdStage")

        pipeline.add_stage(dev_stage, pre=[test_step])
        pipeline.add_stage(prod_stage, pre=[
            test_step,
            pipelines.ManualApprovalStep("ApproveProdDeploy")
        ])