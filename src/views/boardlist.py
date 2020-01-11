
import flask
from model.userinfo import UserInfo
from model.boardinfo import BoardInfo
from views.auth import get_logined_user


module = flask.Blueprint("boardlist", __name__)


@module.route("/board", methods=["GET", "POST"])
def serve_boards():

    if flask.request.method == "GET":
        return flask.render_template(
            "boardlist.html",
            boards=BoardInfo.get_boards(),
            logined_user=get_logined_user())

    elif flask.request.method == "POST":
        action = flask.request.form["action"]
        if action == "delete":
            return delete_board()


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


@module.route("/newboard", methods=["GET", "POST"])
def serve_newboard():
    if flask.request.method == "GET":
        return flask.render_template(
            "newboard.html",
            logined_user=get_logined_user())

    elif flask.request.method == "POST":
        return new_board()


def new_board():
    board_name = flask.request.form["name"]
    logined_user = get_logined_user()

    if BoardInfo.get_board_by_name(board_name) is not None:
        return flask.render_template(
            "newboard.html",
            logined_user=get_logined_user(),
            error_message="同名の掲示板が存在しています。")

    added_board = BoardInfo.add_board(board_name, logined_user.user_id)
    return flask.redirect("/board/{}".format(added_board.board_id))
