Rearc Pipeline AWS Data Engineering Project

This project is an AWS CDK-based data pipeline that:
- Syncs open BLS (Bureau of Labor Statistics) data to an S3 bucket
- Fetches US population data via an external API and uploads it to S3
- Processes and analyzes this data with AWS Lambda functions
- Uses SQS to trigger analytics processing after ingestion
- Implements monitoring with CloudWatch alarms and SNS email notifications

Project Structure

rearc-pipeline/
│
├── lambda_fns/
│   │
│   ├── ingest/           # Lambda function to ingest data (sync BLS, load population)
│   │   └── handler.py
│   │
│   ├── report/           # Lambda function for analytics and reporting
│   │   └── handler.py
│
├── lambda_layer/         # Lambda layer with dependencies (beautifulsoup4, requests, etc.)
│
├── rearc_pipeline/
│   └── rearc_pipeline_stack.py  # CDK stack definition
│
├── stages/                # CDK stages folder
│   ├── dev_stage.py       # CDK stack for Dev environment stage
│   └── prod_stage.py      # CDK stack for Prod environment stage
│
├── cicd_pipeline_stack.py  # CDK stack for CI/CD pipeline
│
├── tests/
│   └── unit/
│       ├── test_lambda_ingest_handler.py
│       ├── test_lambda_report_handler.py
│       └── test_rearc_pipeline_stack.py
│
├── app.py                 # CDK app entrypoint
├── README.md              # This file
├── requirement-dev.txt    # Additional or dev-specific Python dependencies
└── requirements.txt       # Core Python dependencies

---

Prerequisites

- Python 3.9+
- Node.js 16+ (for AWS CDK CLI)
- AWS CLI configured with permissions to deploy resources
- AWS CDK Toolkit installed globally (npm install -g aws-cdk)

---

Setup & Deployment

1. Clone repository:
   git clone https://github.com/Aesha5543/rearcDataPipeline.git
   cd rearc-pipeline

2. Create and activate Python virtual environment:
   python3 -m venv rearcvenv
   source rearcvenv/bin/activate

3. Install Python dependencies:
   pip install -r requirements.txt

4. Bootstrap AWS CDK (run once per AWS environment):
   cdk bootstrap aws://<ACCOUNT_ID>/<REGION>

5. Deploy stack for your environment (dev or prod):
   cdk deploy

---

Running Unit Tests

Run unit tests locally using pytest:
   pytest tests/unit

---

CI/CD Pipeline Overview

- Automated pipeline pulls code from GitHub repository
- Runs unit tests on every commit
- Deploys infrastructure and Lambda functions to Dev and Prod environments
- Uses AWS Secrets Manager for managing GitHub tokens and credentials
- Manual approval before Prod deployment

---

Managing Secrets

Store sensitive values like GitHub tokens securely using AWS Secrets Manager:
   aws secretsmanager create-secret --name github-token --secret-string "<your-github-token>"

---

Cleanup

Remove all deployed resources:
   cdk destroy --context environment=dev

---

Notes

- Lambda Layers package external dependencies for faster deployment and smaller function code
- CloudWatch alarms monitor Lambda failures and send SNS email notifications to the configured address
- S3 event notifications trigger ingestion workflows only when relevant files (e.g., population JSON) are updated

---

If you need help or want to contribute, feel free to reach out!
