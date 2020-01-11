
import functools
import flask
from .auth import get_logined_user


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logined_user = get_logined_user()
        if logined_user is None:
            return flask.redirect("/login")
        return func(*args, **kwargs, logined_user=logined_user)
    return wrapper

