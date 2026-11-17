import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "HealthSutra"
    assert data["status"] == "online"

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["faiss_index_loaded"] is True
    assert data["total_documents_registered"] >= 5

def test_documents_list_endpoint():
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 5
    assert len(data["documents"]) >= 5

def test_evaluation_endpoint():
    response = client.get("/api/v1/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert data["total_questions"] == 50
    assert "grounded_system" in data
    assert "ungrounded_system" in data

def test_admin_analytics_endpoint():
    response = client.get("/api/v1/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "totals" in data
    assert "rates" in data
    assert "performance" in data

def test_chat_emergency_query():
    payload = {
        "question": "Patient is having severe chest pain and cannot breathe",
        "language": "en"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "emergency_alert"
    assert "EMERGENCY ADVISORY" in data["answer"]
    assert len(data["citations"]) == 0

def test_chat_out_of_scope_refusal():
    payload = {
        "question": "Who will win the next cricket world cup championship?",
        "language": "en"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "insufficient_evidence"
    assert "could not find sufficient verified information" in data["answer"]
    assert len(data["citations"]) == 0

def test_chat_grounded_answerable_query():
    payload = {
        "question": "What are the early symptoms of dengue according to WHO?",
        "language": "en"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "answered"
    assert len(data["citations"]) > 0
    assert data["citations"][0]["organization"] == "WHO"
