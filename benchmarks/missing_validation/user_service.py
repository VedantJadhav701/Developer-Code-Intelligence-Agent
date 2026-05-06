def register_user(name, email):
    # BUG: No validation at all
    return {"name": name, "email": email, "active": True}
