from functools import wraps
from flask import request, abort


def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if 'x-api-key' in request.headers and request.headers['x-api-key'] == 'random_hackathon_key_plash':
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function
