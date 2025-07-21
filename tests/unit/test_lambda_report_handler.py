import json
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from io import BytesIO

with patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"}):
    from lambda_fns.report import handler

# @pytest.fixture(autouse=True)
# def patch_env_bucket():
#     with patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"}):
#         yield

def mock_s3_get_object(key, content):
    """Helper to mock s3.get_object() based on key"""
    return {
        'Body': BytesIO(content.encode('utf-8')) if isinstance(content, str) else BytesIO(content)
    }

@patch("lambda_fns.report.handler.s3.get_object")
def test_main_function(mock_get_object):
    # Mock PR data
    pr_csv = """series_id\tyear\tperiod\tvalue\tfootnote_codes
            PRS30006032\t2017\tQ01\t123.4\t
            PRS30006032\t2018\tQ01\t456.7\t
            """
    # Mock Population JSON
    population_json = {
        "data": [
            {"Nation ID": "010", "Nation": "USA", "Year": 2017, "Population": 300000000},
            {"Nation ID": "010", "Nation": "USA", "Year": 2018, "Population": 320000000}
        ]
    }

    def side_effect(Bucket, Key):
        if "pr.data" in Key:
            return mock_s3_get_object(Key, pr_csv)
        elif "acs_population" in Key:
            return mock_s3_get_object(Key, json.dumps(population_json))
        else:
            raise ValueError("Unexpected key")

    mock_get_object.side_effect = side_effect

    result = handler.main({}, {})
    assert result["statusCode"] == 200

    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert "top_yearly_values" in body
    assert "series_population_data" in body

    # Check specific report row
    series_data = body["series_population_data"]
    assert len(series_data) == 2
    assert any(d["series_id"] == "PRS30006032" for d in series_data)
    assert any(d["period"] == "Q01" for d in series_data)
