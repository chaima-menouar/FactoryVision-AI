from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'ok'
    assert body['model_ready'] is False


def test_inspection_history_shape():
    response = client.get('/api/v1/inspections?limit=5')
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 0
    assert body['anomalous'] >= 0
    assert body['normal'] >= 0
    assert 0.0 <= body['defect_rate'] <= 1.0
    assert isinstance(body['items'], list)


def test_copilot_context_shape():
    response = client.get('/api/v1/copilot/context?limit=5')
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 0
    assert body['anomalous'] >= 0
    assert body['normal'] >= 0
    assert 0.0 <= body['defect_rate'] <= 1.0
    assert 0.0 <= body['average_anomaly_score'] <= 1.0
    assert isinstance(body['recent_anomalies'], list)
    assert isinstance(body['suggested_questions'], list)
    assert body['suggested_questions']


def test_rejects_non_image_upload():
    response = client.post('/api/v1/inspect', files={'file': ('test.txt', b'hello', 'text/plain')})
    assert response.status_code == 415
