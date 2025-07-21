# Rearc Pipeline AWS Data Engineering Project

A robust, modular data pipeline built on AWS, designed to automate infrastructure, streamline data ingestion, power analytics, and ensure operational excellence.

## 🚀 Overview

This project is an AWS CDK-based data pipeline that:

- Syncs open BLS (Bureau of Labor Statistics) data to Amazon S3
- Fetches US population data from an external API and uploads it to S3
- Processes and analyzes data with AWS Lambda functions
- Triggers analytics processing via SQS messages after ingestion
- Monitors pipeline health and failures with CloudWatch alarms and SNS notifications

## 🗂️ Project Structure

rearc-pipeline/
│
├── lambda_fns/
│ ├── ingest/ # Lambda: data ingestion (BLS sync, population load)
│ │ └── handler.py
│ └── report/ # Lambda: analytics & reporting
│ └── handler.py
│
├── lambda_layer/ # Shared dependencies: beautifulsoup4, requests, etc.
│
├── rearc_pipeline/
│ └── rearc_pipeline_stack.py # CDK stack definition
│
├── stages/
│ ├── dev_stage.py # Development environment stage
│ └── prod_stage.py # Production environment stage
│
├── cicd_pipeline_stack.py # CDK stack for CI/CD pipeline
│
├── tests/
│ └── unit/
│ ├── test_lambda_ingest_handler.py
│ ├── test_lambda_report_handler.py
│ └── test_rearc_pipeline_stack.py
│
├── app.py # CDK app entrypoint
├── README.md # This documentation file
├── requirement-dev.txt # Dev-specific Python dependencies
└── requirements.txt # Core Python dependencies


## 🛠️ Prerequisites

- Python **3.9+**
- Node.js **16+** (for AWS CDK CLI)
- Configured AWS CLI with deployment permissions
- AWS CDK Toolkit (`npm install -g aws-cdk`)

## ⚡ Getting Started

1. **Clone the repository**
    ```
    git clone https://github.com/Aesha5543/rearcDataPipeline.git
    cd rearc-pipeline
    ```

2. **Set up your environment**
    ```
    python3 -m venv rearcvenv
    source rearcvenv/bin/activate
    ```

3. **Install dependencies**
    ```
    pip install -r requirements.txt
    ```

4. **Bootstrap AWS CDK**
    ```
    cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
    ```

5. **Deploy the pipeline**
    ```
    cdk deploy
    ```

## 🧪 Running Unit Tests

- Run all unit tests locally with:
    ```
    pytest tests/unit
    ```
- Coverage includes Lambda handlers and CDK stack/resource definitions.

## 🔁 CI/CD Pipeline

- Pulls the latest code from GitHub
- Executes automated unit tests on every commit
- Deploys infrastructure and Lambda functions to Dev & Prod environments
- Manages credentials (GitHub tokens via Secrets Manager)
- Manual approval is required before production deployment

## 🔒 Secrets Management

- Store sensitive secrets (e.g., GitHub tokens) securely:
    ```
    aws secretsmanager create-secret --name github-token --secret-string "<your-github-token>"
    ```

## 🧹 Cleanup

To destroy all deployed resources for a specific environment:
    ```
    cdk destroy
    ```


## 🌟 Additional Notes

- Lambda Layers are used to package external dependencies, speeding up deployment and keeping Lambda bundles small
- CloudWatch alarms monitor Lambda failures and notify via SNS email
- S3 event notifications trigger ingestion Lambda only when specific files (e.g., population JSON) are updated

_For questions, help, or contributions, please reach out!_
