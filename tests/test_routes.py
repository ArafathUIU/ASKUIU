from unittest.mock import patch


def test_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ASKUIU" in response.data


def test_index_post_empty_query(client):
    response = client.post("/", data={"user_message": "   "})
    assert response.status_code == 200
    assert b"Please enter a valid question" in response.data


def test_index_post_valid_query(client):
    with patch("app.routes.web.generator.generate_answer", return_value="Test answer"):
        response = client.post(
            "/",
            data={"user_message": "What is UIU?"},
            content_type="application/x-www-form-urlencoded",
        )
    assert response.status_code == 200
    assert b"Test answer" in response.data


def test_api_query_missing_query(client):
    response = client.post("/api/query", json={})
    assert response.status_code == 400
    assert b"No query provided" in response.data


def test_api_query_valid(client):
    with patch("app.routes.api.generator.generate_answer", return_value="API answer"):
        response = client.post("/api/query", json={"query": "What is UIU?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"] == "API answer"
    assert isinstance(data["sources"], list)
