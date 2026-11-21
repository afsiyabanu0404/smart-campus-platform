def booking(room="Lab-A", start="2026-11-21T09:00", end="2026-11-21T10:00", user="student1"):
    return {"room": room, "start": start, "end": end, "user": user}

def test_booking_is_persisted(client):
    response = client.post("/api/bookings", json=booking())
    assert response.status_code == 201
    assert len(client.get("/api/bookings").get_json()) == 1

def test_overlapping_booking_is_rejected(client):
    assert client.post("/api/bookings", json=booking()).status_code == 201
    response = client.post("/api/bookings", json=booking(start="2026-11-21T09:30",
                                                         end="2026-11-21T10:30"))
    assert response.status_code == 409

def test_duplicate_ticket_request_is_idempotent(client):
    payload = {"title": "Projector fault", "request_key": "sensor-event-001"}
    first = client.post("/api/tickets", json=payload)
    second = client.post("/api/tickets", json=payload)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.get_json()["id"] == second.get_json()["id"]

def test_student_cannot_approve_restricted_booking(client):
    response = client.post("/api/approvals", json={"restricted": True},
                           headers={"X-Role": "student"})
    assert response.status_code == 403

def test_approver_can_approve_restricted_booking(client):
    response = client.post("/api/approvals", json={"restricted": True},
                           headers={"X-Role": "approver"})
    assert response.status_code == 200
