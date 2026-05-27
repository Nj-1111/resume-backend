import json
import pytest
from unittest.mock import MagicMock, patch


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_mock_table(initial_count=0):
    """Return a mock DynamoDB Table that mimics update_item behaviour."""
    table = MagicMock()
    counter = {"value": initial_count}

    def fake_update_item(**kwargs):
        counter["value"] += 1
        return {"Attributes": {"count": counter["value"]}}

    table.update_item.side_effect = fake_update_item
    return table


# ── Tests ─────────────────────────────────────────────────────────────────────

@patch("lambda_function.dynamodb")
def test_returns_200(mock_dynamodb):
    mock_dynamodb.Table.return_value = make_mock_table(5)
    from lambda_function import lambda_handler

    result = lambda_handler({}, {})
    assert result["statusCode"] == 200


@patch("lambda_function.dynamodb")
def test_count_increments(mock_dynamodb):
    mock_dynamodb.Table.return_value = make_mock_table(10)
    from lambda_function import lambda_handler

    result = lambda_handler({}, {})
    body = json.loads(result["body"])
    assert body["count"] == 11


@patch("lambda_function.dynamodb")
def test_response_has_cors_headers(mock_dynamodb):
    mock_dynamodb.Table.return_value = make_mock_table(0)
    from lambda_function import lambda_handler

    result = lambda_handler({}, {})
    assert result["headers"]["Access-Control-Allow-Origin"] == "*"


@patch("lambda_function.dynamodb")
def test_body_is_valid_json(mock_dynamodb):
    mock_dynamodb.Table.return_value = make_mock_table(3)
    from lambda_function import lambda_handler

    result = lambda_handler({}, {})
    body = json.loads(result["body"])
    assert "count" in body
    assert isinstance(body["count"], int)


@patch("lambda_function.dynamodb")
def test_multiple_calls_increment_each_time(mock_dynamodb):
    mock_dynamodb.Table.return_value = make_mock_table(0)
    from lambda_function import lambda_handler

    r1 = json.loads(lambda_handler({}, {})["body"])
    r2 = json.loads(lambda_handler({}, {})["body"])
    assert r2["count"] > r1["count"]
