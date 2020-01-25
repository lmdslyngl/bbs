
import flask
from .util import get_logined_user


def get_url() -> str:
    return flask.request.url


def register_template_functions(app: flask.Flask) -> None:
    app.jinja_env.globals.update({
        "get_url": get_url,
        "get_logined_user": get_logined_user
    })
