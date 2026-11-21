def can_approve(role, restricted):
    if not restricted:
        return role in {"admin", "approver", "facility_manager"}
    return role in {"admin", "approver"}
