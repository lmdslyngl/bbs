
from urllib.parse import urlparse
import flask
from .util import get_logined_user, get_csrf_token


def get_url(with_args=True) -> str:
    parsed_url = urlparse(flask.request.url)
    if with_args:
        return parsed_url.path + "?" + parsed_url.query
    else:
        return parsed_url.path


def register_template_functions(app: flask.Flask) -> None:
    app.jinja_env.globals.update({
        "get_url": get_url,
        "get_logined_user": get_logined_user,
        "get_csrf_token": get_csrf_token
    })
