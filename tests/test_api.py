from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'ok'
    assert body['model_ready'] is False


def test_rejects_non_image_upload():
    response = client.post('/api/v1/inspect', files={'file': ('test.txt', b'hello', 'text/plain')})
    assert response.status_code == 415
