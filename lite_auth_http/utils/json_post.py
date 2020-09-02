import json
from functools import wraps


def json_post():
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method == "POST":
                j = json.loads(request.body)

                request.POST = j
            return func(request, *args, **kwargs)

        return inner

    return decorator
