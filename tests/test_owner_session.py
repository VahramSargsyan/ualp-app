"""Synthetic HTTP session boundary checks; no Neon or real credentials."""
import pytest
from fastapi.testclient import TestClient
from webapp.main import app
from webapp import owner_session as sessions

KEY = 'synthetic-owner-key-' + 'a' * 40
ORIGIN = 'https://testserver'
MUTATION = {'X-UALP-Request': '1', 'Origin': ORIGIN}

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('UALP_ENV', 'TEST')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://localhost/unused')
    monkeypatch.setenv('UALP_ACCESS_KEY', KEY)
    with TestClient(app, base_url=ORIGIN) as c:
        yield c

def login(client, remember=True, **extra):
    return client.post('/api/session', json={'remember': remember},
                       headers={**MUTATION, 'X-UALP-Access-Key': KEY, **extra})

def test_remember_reload_and_logout(client):
    assert client.get('/api/session').status_code == 401
    response = login(client)
    assert response.status_code == 200
    cookie = response.headers['set-cookie']
    for flag in ('HttpOnly', 'Secure', 'SameSite=strict', 'Path=/', 'Max-Age=2592000'):
        assert flag in cookie
    assert 'Domain=' not in cookie
    assert KEY not in cookie and KEY not in response.text
    assert client.get('/api/session').status_code == 200
    # New client represents reopening the same host with persisted browser cookies.
    with TestClient(app, base_url=ORIGIN, cookies=client.cookies) as reopened:
        assert reopened.get('/api/session').status_code == 200
        assert reopened.delete('/api/session', headers=MUTATION).status_code == 200
        assert reopened.get('/api/session').status_code == 401
    assert client.get('/api/session').headers['cache-control'] == 'no-store, private'

def test_session_cookie_without_remember(client):
    response = login(client, remember=False)
    assert response.status_code == 200
    assert 'Max-Age=' not in response.headers['set-cookie']
    assert 'expires=' not in response.headers['set-cookie'].lower()

def test_wrong_key_and_csrf_fail_closed(client):
    assert login(client, **{'X-UALP-Access-Key': 'wrong'}).status_code == 401
    assert login(client, Origin='https://evil.example').status_code == 403
    assert login(client, **{'Sec-Fetch-Site': 'same-site'}).status_code == 403
    assert client.post('/api/session', json={}, headers={'X-UALP-Access-Key': KEY}).status_code == 403
    assert login(client).status_code == 200
    # Cookie must not authorize writes without the custom same-origin header.
    assert client.post('/api/runs', json={}).status_code == 403
    assert client.delete('/api/session').status_code == 403
    assert client.get('/api/session', headers={'X-UALP-Access-Key':'wrong'}).status_code == 401
    assert client.get('/api/session').status_code == 200

def test_tamper_expiry_rotation_and_host_binding(client, monkeypatch):
    now = 1800000000
    monkeypatch.setattr(sessions.time, 'time', lambda: now)
    assert login(client).status_code == 200
    token = client.cookies.get(sessions.COOKIE_NAME)
    assert sessions.valid_session(token, KEY, 'testserver')
    assert not sessions.valid_session(token, KEY, 'different-preview.example')
    assert not sessions.valid_session(token, KEY + 'rotated', 'testserver')
    assert not sessions.valid_session(token[:-1] + ('0' if token[-1]!='0' else '1'), KEY, 'testserver')
    monkeypatch.setattr(sessions.time, 'time', lambda: now + sessions.SESSION_SECONDS)
    assert client.get('/api/session').status_code == 401
    monkeypatch.setattr(sessions.time, 'time', lambda: now)
    monkeypatch.setenv('UALP_ACCESS_KEY', KEY + 'rotated')
    assert client.get('/api/session').status_code == 401
    monkeypatch.setenv('UALP_ENV', 'PROD')
    assert client.get('/api/session').status_code == 503

@pytest.mark.parametrize('token', ['', 'a.b.c', '1.'+'a'*48+'.'+'b'*64, 'x'*500, '∞.nonce.mac'])
def test_malformed_session(token):
    assert not sessions.valid_session(token, KEY, 'testserver')
