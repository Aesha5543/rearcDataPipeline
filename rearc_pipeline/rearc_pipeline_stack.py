from aws_cdk import Duration
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_s3_notifications as s3n,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda_event_sources as lambda_events
)
from constructs import Construct

class RearcPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = "Dev-DataLake" if environment == "dev" else "Prod-DataLake"

        bucket = s3.Bucket.from_bucket_name(self, "DataLake", bucket_name=bucket_name)

        queue = sqs.Queue(
            self, "IngestToReportQueue",
            visibility_timeout=Duration.seconds(310)
        )

        common_layer = _lambda.LayerVersion(
            self, "DependenciesLayer",
            code=_lambda.Code.from_asset("lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Layer for beautifulsoup4 and requests"
        )

        numpy_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "NumpyPandasLayer",
            "arn:aws:lambda:ap-south-1:336392948345:layer:AWSSDKPandas-Python39:28"
        )

        ingest_fn = _lambda.Function(
            self, "IngestLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.main",
            code=_lambda.Code.from_asset("lambda_fns/ingest"),
            timeout=Duration.minutes(5),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "QUEUE_URL": queue.queue_url
            },
            layers=[common_layer]
        )

        report_fn = _lambda.Function(
            self, "ReportLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.main",
            code=_lambda.Code.from_asset("lambda_fns/report"),
            timeout=Duration.minutes(5),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            },
            layers=[common_layer, numpy_layer]
        )

        bucket.grant_read_write(ingest_fn)
        bucket.grant_read(report_fn)
        queue.grant_send_messages(ingest_fn)
        queue.grant_consume_messages(report_fn)

        rule = events.Rule(
            self, "DailyIngestSchedule",
            schedule=events.Schedule.rate(Duration.days(1))
        )
        rule.add_target(targets.LambdaFunction(ingest_fn))

        notification = s3n.SqsDestination(queue)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, notification)

        report_fn.add_event_source(
            lambda_events.SqsEventSource(queue)
        )