from fastapi.testclient import TestClient

from backend.app import main as main_module


client = TestClient(main_module.app)


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


def test_copilot_ask_requires_configured_provider():
    response = client.post(
        '/api/v1/copilot/ask',
        json={'question': 'Summarize the latest defects.'},
    )
    assert response.status_code == 503
    assert 'not configured' in response.json()['detail'].lower()


def test_rejects_non_image_upload():
    response = client.post('/api/v1/inspect', files={'file': ('test.txt', b'hello', 'text/plain')})
    assert response.status_code == 415


def test_rejects_image_larger_than_configured_limit(monkeypatch):
    monkeypatch.setenv('FACTORYVISION_DAILY_INSPECTION_LIMIT', '0')
    monkeypatch.setenv('FACTORYVISION_MAX_UPLOAD_BYTES', '10')

    response = client.post(
        '/api/v1/inspect',
        files={'file': ('large.png', b'01234567890', 'image/png')},
    )

    assert response.status_code == 413
    assert 'size limit' in response.json()['detail'].lower()


def test_daily_inspection_limit_fails_closed(monkeypatch):
    monkeypatch.setenv('FACTORYVISION_DAILY_INSPECTION_LIMIT', '1')
    monkeypatch.setattr(main_module.store, 'count_since', lambda _: 1)

    response = client.post(
        '/api/v1/inspect',
        files={'file': ('inspection.png', b'not-read-because-quota-is-full', 'image/png')},
    )

    assert response.status_code == 429
    assert 'zero-cost' in response.json()['detail'].lower()
