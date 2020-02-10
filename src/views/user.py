
from typing import Optional
import flask
from model.userinfo import UserInfo
from model.session import Session
from model.csrf_token import CSRFToken
from views.auth import get_logined_user
from .auth_deco import \
    login_required, logout_required, \
    csrf_token_required, enable_feature_by_flag
from .util import get_logined_user, get_session
from util import get_current_logger
import conf


module = flask.Blueprint("user", __name__)


@module.route("/newuser", methods=["GET", "POST"])
@enable_feature_by_flag(conf.allow_create_user)
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

    get_current_logger().info(
        "Created user: user_id={}".format(added_user.user_id))

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

    get_current_logger().info(
        "Edited username: user_id={}".format(logined_user.user_id))

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

    get_current_logger().info(
        "Edited password: user_id={}".format(logined_user.user_id))

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


@module.route("/deleteuser", methods=["GET", "POST"])
@enable_feature_by_flag(conf.allow_delete_user)
@login_required
def deleteuser():
    if flask.request.method == "GET":
        return flask.render_template("deleteuser.html")
    elif flask.request.method == "POST":
        return perform_delete_user()


@csrf_token_required
def perform_delete_user():
    password = flask.request.form["password"]
    agree_check = "agree" in flask.request.form

    if not agree_check:
        return flask.render_template(
            "deleteuser.html",
            error_message="同意のチェックボックスにチェックを入れてください。")

    logined_user = get_logined_user()
    if UserInfo.check_password_by_user_id(logined_user.user_id , password) is None:
        return flask.render_template(
            "deleteuser.html",
            error_message="パスワードが正しくありません。")

    session = get_session()
    CSRFToken.delete_token(session.session_id)
    Session.delete_session(session.session_id)

    UserInfo.delete_user(logined_user.user_id)

    resp = flask.redirect("/login")
    resp.set_cookie("session_id", "", expires=0)

    get_current_logger().info(
        "Deleted user: user_id={}".format(logined_user.user_id))

    return resp
