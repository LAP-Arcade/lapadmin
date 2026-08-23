import functools

TASKS = []


def task(trigger, **trigger_kwargs):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print(f"Task started: {f.__name__}")
            f(*args, **kwargs)
            print(f"Task finished: {f.__name__}")

        TASKS.append((wrapper, trigger, trigger_kwargs))
        return wrapper

    return decorator


def run_all():
    for fn, _trigger, _trigger_kwargs in TASKS:
        fn()


from . import auth_tokens  # noqa: E402 F401
