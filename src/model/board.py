
from typing import List, Tuple, Optional, NamedTuple
from datetime import datetime
from psycopg2.extras import DictCursor

from .util import get_connection
from .boardinfo import BoardInfo
from .userinfo import UserInfo


class PagedBoardPosts(NamedTuple):
    posts: List[Tuple["Board", UserInfo]]
    has_older: bool
    older_until_id: int
    has_newer: bool
    newer_since_id: int


class Board:
    def __init__(
            self,
            post_id: int,
            board_id: int,
            body: str,
            author_user_id: int,
            created_at: datetime,
            deleted: bool) -> None:

        self.post_id = post_id
        self.board_id = board_id
        self.body = body
        self.author_user_id = author_user_id
        self.created_at = created_at
        self.deleted = deleted

    @staticmethod
    def add_post(
            board_id: int,
            body: str,
            author_user_id: int) -> "Board":

        sql = """
            INSERT INTO
                board (board_id, body, author_user_id)
            VALUES (%s, %s, %s)
            RETURNING *
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (board_id, body, author_user_id))
                inserted = Board(*cur.fetchone())
                con.commit()

        return inserted

    @staticmethod
    def get_post(board_id: int, post_id: int) -> Optional["Board"]:
        sql = """
            SELECT *
            FROM board
            WHERE board_id = %s AND post_id = %s AND deleted = false
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (board_id, post_id))
                row = cur.fetchone()
                con.commit()

        if row is None:
            return None
        else:
            return Board(*row)

    @staticmethod
    def get_post_by_board_id(
            board_id: int,
            count: int = 200) -> PagedBoardPosts:

        sql = """
            SELECT
                board.post_id           AS post_id,
                board.board_id          AS board_id,
                board.body              AS body,
                board.author_user_id    AS author_user_id,
                board.created_at        AS created_at,
                userinfo.name           AS author_name,
                userinfo.created_at     AS author_created_at,
                userinfo.deleted        AS author_deleted
            FROM board
                INNER JOIN userinfo
                    ON board.author_user_id = userinfo.user_id
            WHERE board.board_id = %s
                AND board.deleted = false
            ORDER BY board.created_at DESC
            LIMIT %s
        """

        board_contents = []

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                # 次のページを取得
                cur.execute(sql, (board_id, count + 1))
                board_contents = Board._create_board_contents_list(cur)
                con.commit()

        if len(board_contents) == count + 1:
            # count+1件のレコードがあれば次のページのさらに過去の書き込みが存在する
            has_older = True
            older_until_id = board_contents[-1][0].post_id

            # +1の分の要素を削除
            board_contents.pop()

        else:
            # それ以下であれば過去の書き込みは存在しない
            has_older = False
            older_until_id = 0

        return PagedBoardPosts(
            board_contents,
            has_older,
            older_until_id,
            False, 0) # 最新のものから取得するため，前のページは存在しない

    @staticmethod
    def get_post_by_board_id_older(
            board_id: int,
            until_id: int,
            count: int = 200) -> PagedBoardPosts:

        sql = """
            SELECT
                board.post_id           AS post_id,
                board.board_id          AS board_id,
                board.body              AS body,
                board.author_user_id    AS author_user_id,
                board.created_at        AS created_at,
                userinfo.name           AS author_name,
                userinfo.created_at     AS author_created_at,
                userinfo.deleted        AS author_deleted
            FROM board
                INNER JOIN userinfo
                    ON board.author_user_id = userinfo.user_id
            WHERE board.board_id = %s
                AND board.post_id <= %s
                AND board.deleted = false
            ORDER BY board.created_at DESC
            LIMIT %s
        """

        sql_newer_page_check = """
            SELECT post_id
            FROM board
            WHERE board_id = %s
                AND %s < post_id
                AND deleted = false
            ORDER BY created_at ASC
            LIMIT 1
        """

        board_contents = []

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (board_id, until_id, count + 1))
                board_contents = Board._create_board_contents_list(cur)

                # 前のページを1件だけ取得
                cur.execute(sql_newer_page_check, (board_id, until_id))
                newer_row = cur.fetchone()

                con.commit()

        if len(board_contents) == count + 1:
            # count+1件のレコードがあれば次のページのさらに過去の書き込みが存在する
            has_older = True
            older_until_id = board_contents[-1][0].post_id

            # +1の分の要素を削除
            board_contents.pop()

        else:
            # それ以下であれば過去の書き込みは存在しない
            has_older = False
            older_until_id = 0

        return PagedBoardPosts(
            board_contents,
            has_older,
            older_until_id,
            newer_row is not None,
            0 if newer_row is None else newer_row[0])

    @staticmethod
    def get_post_by_board_id_newer(
            board_id: int,
            since_id: int,
            count: int = 200) -> PagedBoardPosts:

        sql = """
            SELECT
                board.post_id           AS post_id,
                board.board_id          AS board_id,
                board.body              AS body,
                board.author_user_id    AS author_user_id,
                board.created_at        AS created_at,
                userinfo.name           AS author_name,
                userinfo.created_at     AS author_created_at,
                userinfo.deleted        AS author_deleted
            FROM board
                INNER JOIN userinfo
                    ON board.author_user_id = userinfo.user_id
            WHERE board.board_id = %s
                AND %s <= board.post_id
                AND board.deleted = false
            ORDER BY board.created_at ASC
            LIMIT %s
        """

        sql_older_page_check = """
            SELECT post_id
            FROM board
            WHERE board_id = %s
                AND post_id < %s
                AND deleted = false
            ORDER BY created_at DESC
            LIMIT 1
        """

        board_contents = []

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                # 前のページを取得
                cur.execute(sql, (board_id, since_id, count + 1))
                board_contents = Board._create_board_contents_list(cur)

                # 次のページを1件だけ取得
                cur.execute(sql_older_page_check, (board_id, since_id))
                older_row = cur.fetchone()

                con.commit()

        if len(board_contents) == count + 1:
            # count+1件のレコードがあれば前のページのさらに未来の書き込みが存在する
            has_newer = True
            newer_since_id = board_contents[-1][0].post_id

            # +1の分の要素を削除
            board_contents.pop()

        else:
            # それ以下であれば未来の書き込みは存在しない
            has_newer = False
            newer_since_id = 0

        # 古い順でDBから取得しているため新しい順に戻す
        board_contents.reverse()

        return PagedBoardPosts(
            board_contents,
            older_row is not None,
            0 if older_row is None else older_row[0],
            has_newer,
            newer_since_id)

    @staticmethod
    def _create_board_contents_list(cur) -> List[Tuple["Board", UserInfo]]:
        board_contents = []

        for row in cur.fetchall():
            board = Board(
                row["post_id"], row["board_id"], row["body"],
                row["author_user_id"], row["created_at"], False)

            userinfo = UserInfo(
                row["author_user_id"], row["author_name"],
                row["author_created_at"], "", row["author_deleted"])

            board_contents.append((board, userinfo))

        return board_contents

    @staticmethod
    def delete_post(board_id: int, post_id: int) -> None:
        sql = """
            UPDATE board
            SET deleted = true
            WHERE board_id = %s AND post_id = %s AND deleted = false
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (board_id, post_id,))
                con.commit()


