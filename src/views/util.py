
from typing import Optional
import flask
from model.userinfo import UserInfo
from model.session import Session


def get_logined_user() -> Optional[UserInfo]:
    if "logined_user" in flask.g:
        # キャッシュがあるならセッションから引かずにキャッシュを使う
        return flask.g.logined_user

    try:
        session_id = flask.request.cookies.get("session_id")
        if session_id is None:
            return None
    except KeyError:
        return None

    userinfo, session = Session.get_user_and_session_by_session_id(session_id)

    if session.is_expired():
        return None

    # キャッシュにも登録しておく
    flask.g.logined_user = userinfo
    return userinfo

