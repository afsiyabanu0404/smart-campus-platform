def test_dashboard_and_health_endpoints(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").get_json()["status"] == "healthy"

def test_missing_booking_details_are_rejected(client):
    assert client.post("/api/bookings", json={"room": "Lab-A"}).status_code == 400

def test_invalid_ticket_transition_is_rejected(client):
    created = client.post("/api/tickets", json={
        "title": "AC issue", "request_key": "ticket-100"
    }).get_json()
    response = client.patch(f"/api/tickets/{created['id']}", json={"status": "unknown"})
    assert response.status_code == 400

def test_sensor_api_threshold_boundary(client):
    assert client.post("/api/sensors/check", json={"value": 75}).get_json()["alert"]
    assert not client.post("/api/sensors/check", json={"value": 74}).get_json()["alert"]

def test_external_sync_retry_policy(client):
    assert client.post("/api/sync/retry-policy", json={"status_code": 503}).get_json()["retry"]
    assert not client.post("/api/sync/retry-policy", json={"status_code": 404}).get_json()["retry"]
