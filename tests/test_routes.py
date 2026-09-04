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
    assert len(data["sources"]) > 0
    # Check that rich metadata is preserved
    first_source = data["sources"][0]
    assert "title" in first_source
    assert "source" in first_source
    assert "category" in first_source


def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "index_stats" in data
    assert data["index_stats"]["total_documents"] > 0


def test_api_stream(client):
    response = client.get("/api/stream?query=What+is+UIU")
    assert response.status_code == 200
    assert response.mimetype == "text/event-stream"
    assert b"data: " in response.data
    assert b"\"type\": \"sources\"" in response.data
    assert b"\"type\": \"done\"" in response.data
