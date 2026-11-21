from datetime import datetime

def _parse(value):
    return datetime.fromisoformat(value)

def validate_booking(start, end, minimum_minutes=30, maximum_minutes=240):
    try:
        start_dt, end_dt = _parse(start), _parse(end)
    except (TypeError, ValueError):
        return False, "Invalid date/time format"
    duration = (end_dt - start_dt).total_seconds() / 60
    if duration <= 0:
        return False, "End time must be after start time"
    if duration < minimum_minutes or duration > maximum_minutes:
        return False, "Booking duration outside allowed limits"
    return True, "Valid booking"

def has_overlap(start, end, existing):
    new_start, new_end = _parse(start), _parse(end)
    for old_start, old_end in existing:
        if new_start < _parse(old_end) and _parse(old_start) < new_end:
            return True
    return False
