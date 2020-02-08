
from typing import Optional
import flask
from model.userinfo import UserInfo
from model.session import Session
from model.csrf_token import CSRFToken
from views.auth import get_logined_user
from .auth_deco import login_required, logout_required, csrf_token_required
from .util import get_logined_user


module = flask.Blueprint("user", __name__)


@module.route("/newuser", methods=["GET", "POST"])
@logout_required
def newuser():
    if flask.request.method == "GET":
        return flask.render_template("newuser.html")
    elif flask.request.method == "POST":
        return create_new_user()


def create_new_user():
    username = flask.request.form["name"]
    password = flask.request.form["password"]
    password_confirm = flask.request.form["password-confirm"]

    username_check_result = check_username_criteria(username)
    if username_check_result is not None:
        return flask.render_template(
            "newuser.html",
            name=username, error_message=username_check_result)

    password_check_result = check_password_criteria(password, password_confirm)
    if password_check_result is not None:
        return flask.render_template(
            "newuser.html",
            name=username, error_message=password_check_result)

    added_user = UserInfo.add_user(username, password)

    session = Session.add_session(added_user.user_id)
    if session is None:
        return flask.render_template(
            "login.html",
            name=username,
            error_message="セッションの作成に失敗しました。")

    CSRFToken.add_token(session.session_id)

    resp = flask.make_response(
        flask.render_template("newuser-succeeded.html",
            added_user=added_user))
    resp.set_cookie(
        "session_id", session.session_id,
        httponly=True, expires=session.expire_at)

    return resp


@module.route("/edituser", methods=["GET", "POST"])
@login_required
def edituser():
    logined_user = get_logined_user()
    if flask.request.method == "GET":
        return flask.render_template(
            "edituser.html", logined_user=logined_user)

    elif flask.request.method == "POST":
        if flask.request.form["action"] == "edit-username":
            return edit_username(logined_user)
        elif flask.request.form["action"] == "edit-password":
            return edit_password(logined_user)
        else:
            return flask.render_template(
                "edituser.html",
                error_message="actionが不正です。")


@csrf_token_required
def edit_username(logined_user: UserInfo):
    username = flask.request.form["name"]

    if username == logined_user.name:
        return flask.render_template(
            "edituser.html",
            succeeded_message="ユーザ名に変更はありませんでした。")

    check_result = check_username_criteria(username)
    if check_result is not None:
        return flask.render_template(
            "edituser.html",
            error_message=check_result)

    UserInfo.update_user(logined_user.user_id, username, None)

    # ユーザ名の変更を反映するためにユーザを強制取得
    get_logined_user(force_reload=True)

    return flask.render_template(
        "edituser.html",
        succeeded_message="ユーザ名を変更しました。")


@csrf_token_required
def edit_password(logined_user: UserInfo):
    password = flask.request.form["password"]
    password_confirm = flask.request.form["password-confirm"]

    check_result = check_password_criteria(password, password_confirm)
    if check_result is not None:
        return flask.render_template(
            "edituser.html",
            error_message=check_result)

    UserInfo.update_user(logined_user.user_id, None, password)

    return flask.render_template(
        "edituser.html",
        succeeded_message="パスワードを変更しました。")


def check_username_criteria(username: str) -> Optional[str]:
    if len(username) < 4:
        return "ユーザ名は4文字以上である必要があります。"

    if UserInfo.find_by_name(username) is not None:
        return "ユーザ: \"{}\"はすでに存在します".format(username)

    return None


def check_password_criteria(password: str, password_confirm: str) -> Optional[str]:
    if len(password) < 8:
        return "パスワードは8文字以上である必要があります。"

    if password != password_confirm:
        return "パスワード（確認）が一致しません。"

    return None

