from functools import wraps
from flask import request, jsonify

def require_token(settings):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"ok": False, "reason": "missing token"}), 401
            token = auth.split(" ", 1)[1].strip()
            if token not in settings.allowed_tokens:
                return jsonify({"ok": False, "reason": "invalid token"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
