
from typing import Optional
import flask
from model.userinfo import UserInfo
from model.session import Session
from views.auth import get_logined_user
from .auth_deco import login_required


module = flask.Blueprint("user", __name__)


@module.route("/newuser", methods=["GET", "POST"])
def newuser():
    if flask.request.method == "GET":
        return flask.render_template("newuser.html")
    elif flask.request.method == "POST":
        return create_new_user()


def create_new_user():
    username = flask.request.form["name"]
    password = flask.request.form["password"]
    password_confirm = flask.request.form["password-confirm"]

    error_msg = check_auth_criteria(username, password, password_confirm)
    if error_msg is not None:
        return flask.render_template(
            "newuser.html",
            name=username, error_message=error_msg)

    added_user = UserInfo.add_user(username, password)

    session = Session.add_session(added_user.user_id)
    if session is None:
        return flask.render_template(
            "login.html",
            name=username,
            error_message="セッションの作成に失敗しました。")

    resp = flask.make_response(
        flask.render_template("newuser-succeeded.html", logined_user=added_user))
    resp.set_cookie("session_id", session.session_id)
    return resp


@module.route("/edituser", methods=["GET", "POST"])
@login_required
def edituser():
    logined_user = get_logined_user()
    if flask.request.method == "GET":
        return flask.render_template(
            "edituser.html", logined_user=logined_user)
    elif flask.request.method == "POST":
        return edit_user(logined_user)


def edit_user(logined_user: UserInfo):
    username = flask.request.form["name"]
    password = flask.request.form["password"]
    password_confirm = flask.request.form["password-confirm"]

    if logined_user.name == username:
        username = None

    if len(password) <= 0:
        password = None

    if len(password_confirm) <= 0:
        password_confirm = None

    error_msg = check_auth_criteria(username, password, password_confirm)

    if error_msg is not None:
        return flask.render_template(
            "edituser.html",
            logined_user=logined_user,
            error_message=error_msg)

    updated_user = UserInfo.update_user(
        logined_user.user_id, username, password)

    if updated_user is None:
        return flask.render_template(
            "edituser.html",
            logined_user=logined_user,
            succeeded_message="ユーザ情報に変更はありませんでした。")

    return flask.render_template(
        "edituser.html",
        logined_user=updated_user,
        succeeded_message="ユーザ情報の編集に成功しました。")


def check_auth_criteria(
        username: Optional[str],
        password: Optional[str],
        password_confirm: Optional[str]) -> Optional[str]:

    if username is not None:
        if len(username) < 4:
            return "ユーザ名は4文字以上である必要があります。"

        if UserInfo.find_by_name(username) is not None:
            return "ユーザ: \"{}\"はすでに存在します".format(username)

    if password is not None and len(password) < 8:
        return "パスワードは8文字以上である必要があります。"

    if password is not None and password != password_confirm:
        return "パスワード（確認）が一致しません。"

    return None

