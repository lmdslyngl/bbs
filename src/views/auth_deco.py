
import functools
import flask
from .util import get_logined_user, get_csrf_token


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logined_user = get_logined_user()
        if logined_user is None:
            return flask.redirect("/login?next=" + flask.request.path)
        return func(*args, **kwargs)
    return wrapper


def logout_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logined_user = get_logined_user()
        if logined_user is not None:
            return flask.render_template(
                "error.html",
                error_message="ログインしている状態では使用できないページです。")
        return func(*args, **kwargs)
    return wrapper


def csrf_token_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = get_csrf_token()

        if "csrf-token" in flask.request.form:
            token_in_request = flask.request.form["csrf-token"]
        else:
            return flask.render_template(
                "error.html",
                error_message="CSRFトークンが見つかりません。")

        if token_in_request != token:
            return flask.render_template(
                "error.html",
                error_message="CSRFトークンが一致しません。")

        return func(*args, **kwargs)

    return wrapper

