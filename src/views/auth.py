
from typing import Optional
import flask
from model.userinfo import UserInfo
from model.session import Session
from .util import get_logined_user


module = flask.Blueprint("auth", __name__)


@module.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")
    elif flask.request.method == "POST":
        return perform_login()


def perform_login():
    username = flask.request.form["name"]
    password = flask.request.form["password"]

    logined_user = UserInfo.check_password(username, password)

    if logined_user is None:
        return flask.render_template(
            "login.html",
            name=username,
            error_message="ユーザ名またはパスワードが違います。")

    session = Session.add_session(logined_user.user_id)
    if session is None:
        return flask.render_template(
            "login.html",
            name=username,
            error_message="セッションの作成に失敗しました。")

    resp = flask.redirect("/board")
    resp.set_cookie(
        "session_id", session.session_id,
        httponly=True, expires=session.expire_at)

    return resp


@module.route("/logout", methods=["GET"])
def logout():
    try:
        session_id = flask.request.cookies.get("session_id")
        Session.delete_session(session_id)
    except KeyError:
        pass

    resp = flask.make_response(flask.render_template(
        "login.html",
        succeeded_message="ログアウトしました。"))
    resp.set_cookie("session_id", "", expires=0)

    return resp

