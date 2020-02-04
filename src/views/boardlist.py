
import flask
from model.userinfo import UserInfo
from model.boardinfo import BoardInfo
from .util import get_logined_user
from .auth_deco import login_required, csrf_token_required


module = flask.Blueprint("boardlist", __name__)


@module.route("/board", methods=["GET", "POST"])
def serve_boards():

    if flask.request.method == "GET":
        return show_boards()

    elif flask.request.method == "POST":
        action = flask.request.form["action"]
        if action == "delete":
            return delete_board()


def show_boards():
    if "older_until_id" in flask.request.args:
        older_until_id = flask.request.args["older_until_id"]
        boards = BoardInfo.get_boards_older(older_until_id, count=2)

    elif "newer_since_id" in flask.request.args:
        newer_since_id = flask.request.args["newer_since_id"]
        boards = BoardInfo.get_boards_newer(newer_since_id, count=2)

    else:
        # 何も指定されていないときは最新の掲示板から取得
        boards = BoardInfo.get_boards(count=2)

    return flask.render_template(
        "boardlist.html",
        boards=boards.boards,
        has_older=boards.has_older,
        older_until_id=boards.older_until_id,
        has_newer=boards.has_newer,
        newer_since_id=boards.newer_since_id)


@login_required
@csrf_token_required
def delete_board():
    board_id = int(flask.request.form["board_id"])

    logined_user = get_logined_user()
    if logined_user is None:
        return flask.render_template(
            "error.html",
            error_message="Not logged in.")

    board = BoardInfo.get_board(board_id)
    if board is None:
        return flask.render_template(
            "error.html",
            error_message="Not found board: board_id={}".format(board_id))

    if logined_user.user_id != board.owner_user_id:
        return flask.render_template(
            "error.html",
            error_message="Board owner and logined user are mismatched: " +
                "logined_user_id={}, owner_user_id={}".format(
                    logined_user.user_id, board.owner_user_id))

    BoardInfo.delete_board(board_id)

    return flask.render_template(
        "boardlist.html",
        boards=BoardInfo.get_boards(),
        logined_user=get_logined_user(),
        succeeded_message="掲示板を削除しました。")


@login_required
@module.route("/newboard", methods=["GET", "POST"])
def serve_newboard():
    if flask.request.method == "GET":
        return flask.render_template(
            "newboard.html",
            logined_user=get_logined_user())

    elif flask.request.method == "POST":
        return new_board()


@csrf_token_required
def new_board():
    board_name = flask.request.form["name"]
    logined_user = get_logined_user()

    if len(board_name) <= 0:
        return flask.render_template(
            "newboard.html",
            logined_user=get_logined_user(),
            error_message="掲示板名を入力してください。")

    if BoardInfo.get_board_by_name(board_name) is not None:
        return flask.render_template(
            "newboard.html",
            logined_user=get_logined_user(),
            error_message="同名の掲示板が存在しています。")

    added_board = BoardInfo.add_board(board_name, logined_user.user_id)
    return flask.redirect("/board/{}".format(added_board.board_id))
