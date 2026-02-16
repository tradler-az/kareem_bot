def check_permission(intent):
    dangerous = ["shutdown"]

    if intent in dangerous:
        return False
    return True