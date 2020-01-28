
from typing import Optional, Tuple
from urllib.parse import urlparse
import flask
from model.userinfo import UserInfo
from model.session import Session
from model.csrf_token import CSRFToken


def get_logined_user_and_session(
        force_reload=False) -> Optional[Tuple[UserInfo, Session]]:

    if not force_reload and "logined_user_and_session" in flask.g:
        # 強制リロードではないときにキャッシュがあるならそれを使う
        return flask.g.logined_user_and_session

    try:
        session_id = flask.request.cookies.get("session_id")
        if session_id is None:
            return None
    except KeyError:
        return None

    user_and_session = Session.get_user_and_session_by_session_id(session_id)
    if user_and_session is None:
        return None

    _, session = user_and_session
    if session.is_expired():
        return None

    flask.g.logined_user_and_session = user_and_session
    return user_and_session


def get_logined_user(force_reload=False) -> Optional[UserInfo]:
    logined_user_and_session = get_logined_user_and_session(force_reload)
    if logined_user_and_session is None:
        return None
    else:
        return logined_user_and_session[0]


def get_session(force_reload=False) -> Optional[Session]:
    logined_user_and_session = get_logined_user_and_session(force_reload)
    if logined_user_and_session is None:
        return None
    else:
        return logined_user_and_session[1]


def get_csrf_token() -> Optional[str]:
    if "csrf_token" in flask.g:
        return flask.g.csrf_token

    session = get_session()
    if session is None:
        return None
    else:
        token = CSRFToken.get_token_by_session_id(session.session_id)
        flask.g.csrf_token = token.token
        return token.token


def extract_path_from_url(url: str) -> str:
    return urlparse(url).path

