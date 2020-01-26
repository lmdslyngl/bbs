
from typing import Optional
from urllib.parse import quote
import flask
from model.userinfo import UserInfo
from model.session import Session
from .util import get_logined_user, extract_path_from_url
from .auth_deco import logout_required


module = flask.Blueprint("auth", __name__)


@module.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    if flask.request.method == "GET":
        return show_login()
    elif flask.request.method == "POST":
        return perform_login()


def show_login():
    login_url = "/login"
    if "next" in flask.request.args:
        # 別ドメインにリダイレクトしないように，URLのパスだけを抜き出す
        next_url = extract_path_from_url(flask.request.args["next"])
        if 0 < len(next_url):
            login_url = "/login?next=" + next_url

    return flask.render_template(
        "login.html",
        login_url=login_url)


def perform_login():
    if "next" in flask.request.args:
        next_url = extract_path_from_url(flask.request.args["next"])
    else:
        next_url = "/board"
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

    resp = flask.redirect(next_url)
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

    resp = flask.redirect("/login")
    resp.set_cookie("session_id", "", expires=0)
    return resp

