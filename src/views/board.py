
from datetime import datetime
import html
import flask
from model.userinfo import UserInfo
from model.boardinfo import BoardInfo
from model.board import Board
from .util import get_logined_user, datetime2str
from .auth_deco import login_required, csrf_token_required
from util import get_current_logger
import conf


module = flask.Blueprint("board", __name__)


@module.route("/board/<board_id>", methods=["GET", "POST"])
def board(board_id: int):
    if flask.request.method == "GET":
        return show_board(board_id)

    elif flask.request.method == "POST":
        action = flask.request.form["action"]
        if action == "post":
            return post_board(board_id)
        elif action == "delete":
            return delete_post(board_id)


def show_board(board_id: int):
    logined_user = get_logined_user()

    if "older_until_id" in flask.request.args:
        older_until_id = flask.request.args["older_until_id"]
        posts = Board.get_post_by_board_id_older(
            board_id, older_until_id,
            count=conf.board_posts_per_page)

    elif "newer_since_id" in flask.request.args:
        newer_since_id = flask.request.args["newer_since_id"]
        posts = Board.get_post_by_board_id_newer(
            board_id, newer_since_id,
            count=conf.board_posts_per_page)

    else:
        # 何も指定されていないときは最新の投稿から取得
        posts = Board.get_post_by_board_id(
            board_id, count=conf.board_posts_per_page)

    board = BoardInfo.get_board(board_id)

    posts_for_tempalte = []
    board_info_for_tempalte = {
        "name": board.name,
        "board_id": board.board_id,
        "created_at": datetime2str(board.created_at),
    }

    for (board, user_info) in posts.posts:
        posts_for_tempalte.append({
            "post_id": board.post_id,
            "author_name": user_info.name,
            "author_user_id": user_info.user_id,
            "created_at": datetime2str(board.created_at),
            "body": board.body
        })

    return flask.render_template(
        "board_template.html",
        logined_user=logined_user,
        boardinfo=board_info_for_tempalte,
        posts=posts_for_tempalte,
        has_older=posts.has_older,
        older_until_id=posts.older_until_id,
        has_newer=posts.has_newer,
        newer_since_id=posts.newer_since_id)


@login_required
@csrf_token_required
def post_board(board_id: int):
    body = flask.request.form["body"]
    if 0 < len(body):
        logined_user = get_logined_user()
        author_user_id = logined_user.user_id

        body = html.escape(body).replace("\n", "<br>")
        added_post = Board.add_post(board_id, body, author_user_id)

    get_current_logger().info(
        "Posted: user_id={}, post_id={}".format(
            logined_user.user_id, added_post.post_id))

    return show_board(board_id)


@login_required
@csrf_token_required
def delete_post(board_id: int):
    post_id = int(flask.request.form["post_id"])

    post = Board.get_post(board_id, post_id)
    if post is None:
        return flask.render_template(
            "error.html",
            error_message="Not found post: post_id={}".format(post_id))

    logined_user = get_logined_user()
    if logined_user.user_id != post.author_user_id:
        return flask.render_template(
            "error.html",
            error_message="Author and logined user are mismatched: " +
                "logined_user_id={}, author_id={}".format(
                    logined_user.user_id, post.author_user_id))

    Board.delete_post(board_id, post_id)

    get_current_logger().info(
        "Deleted post: user_id={}, post_id={}".format(
            logined_user.user_id, post_id))

    return show_board(board_id)

