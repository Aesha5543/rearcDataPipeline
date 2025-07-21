import json
import os
import pytest
from unittest.mock import patch, MagicMock

# Set environment variable for testing
with patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"}):
    from lambda_fns.ingest import handler

# Test for loading population data to S3
@patch("lambda_fns.ingest.handler.requests.get")
@patch("lambda_fns.ingest.handler.s3")
def test_load_population_to_s3(mock_s3, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": "mocked"}

    success = handler.load_population_to_s3()
    assert success
    mock_s3.put_object.assert_called_once()
    args, kwargs = mock_s3.put_object.call_args
    assert kwargs["Bucket"] == "test-bucket"
    assert kwargs["Key"] == "datausa/acs_population.json"

# Test for syncing BLS file when it's new
@patch("lambda_fns.ingest.handler.requests.get")
@patch("lambda_fns.ingest.handler.s3")
def test_sync_bls_new_file(mock_s3, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"sample file content"
    mock_get.return_value.text = """
    <html><body><a href="pr.data.0.Current">Download</a></body></html>
    """

    mock_s3.get_paginator.return_value.paginate.return_value = []

    success = handler.sync_bls()
    assert success
    mock_s3.put_object.assert_called_once()

# Test for Lambda main handler with both components succeeding
@patch("lambda_fns.ingest.handler.sync_bls", return_value=True)
@patch("lambda_fns.ingest.handler.load_population_to_s3", return_value=True)
def test_main_success(mock_pop, mock_bls):
    response = handler.main({}, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["bls_sync"] is True
    assert body["population_upload_success"] is True
