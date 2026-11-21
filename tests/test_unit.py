import pytest
from modules.booking import validate_booking, has_overlap
from modules.maintenance import calculate_sla_deadline, valid_transition
from modules.sensors import threshold_exceeded
from modules.approval import can_approve

def test_valid_booking():
    assert validate_booking("2026-11-21T09:00", "2026-11-21T10:00")[0]

def test_reject_booking_below_minimum():
    assert not validate_booking("2026-11-21T09:00", "2026-11-21T09:20")[0]

def test_reject_booking_above_maximum():
    assert not validate_booking("2026-11-21T09:00", "2026-11-21T14:00")[0]

def test_detect_overlapping_booking():
    assert has_overlap("2026-11-21T09:30", "2026-11-21T10:30",
                       [("2026-11-21T09:00", "2026-11-21T10:00")])

def test_sensor_threshold_boundary():
    assert threshold_exceeded(75, 75)
    assert not threshold_exceeded(74, 75)

def test_sla_deadline_for_high_priority():
    assert str(calculate_sla_deadline("2026-11-21T08:00", "high")) == "2026-11-21 16:00:00"

def test_valid_ticket_transition():
    assert valid_transition("open", "in_progress")

def test_reject_transition_from_closed():
    assert not valid_transition("closed", "open")

def test_restricted_approval_requires_approver():
    assert can_approve("approver", True)
    assert not can_approve("student", True)
