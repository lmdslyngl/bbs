
from typing import Optional
from urllib.parse import quote
import flask
from model.userinfo import UserInfo
from model.session import Session
from model.csrf_token import CSRFToken
from .util import get_logined_user, extract_path_from_url
from .auth_deco import logout_required
from util import get_current_logger


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
        get_current_logger().warning(
            "Invalid credential: username={}".format(username))

        return flask.render_template(
            "login.html",
            name=username,
            error_message="ユーザ名またはパスワードが違います。")

    session = Session.add_session(logined_user.user_id)
    if session is None:
        get_current_logger().error(
            "Failed to create session: user_id={}".format(logined_user.user_id))

        return flask.render_template(
            "login.html",
            name=username,
            error_message="セッションの作成に失敗しました。")

    CSRFToken.add_token(session.session_id)

    resp = flask.redirect(next_url)
    resp.set_cookie(
        "session_id", session.session_id,
        httponly=True, expires=session.expire_at)

    get_current_logger().info(
        "Logged in: user_id={}".format(logined_user.user_id))

    return resp


@module.route("/logout", methods=["GET"])
def logout():
    try:
        logouted_user = get_logined_user()
        session_id = flask.request.cookies.get("session_id")
        CSRFToken.delete_token(session_id)
        Session.delete_session(session_id)
    except KeyError:
        pass

    resp = flask.redirect("/login")
    resp.set_cookie("session_id", "", expires=0)

    get_current_logger().info(
        "Logged out: user_id={}".format(logouted_user.user_id))

    return resp

