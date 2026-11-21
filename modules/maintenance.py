from datetime import datetime, timedelta

SLA_HOURS = {"low": 72, "medium": 24, "high": 8, "critical": 2}
ALLOWED_TRANSITIONS = {
    "open": {"in_progress", "closed"},
    "in_progress": {"waiting", "closed"},
    "waiting": {"in_progress", "closed"},
    "closed": set(),
}

def calculate_sla_deadline(created_at, priority):
    if priority not in SLA_HOURS:
        raise ValueError("Unknown priority")
    return datetime.fromisoformat(created_at) + timedelta(hours=SLA_HOURS[priority])

def valid_transition(current, new):
    return new in ALLOWED_TRANSITIONS.get(current, set())
