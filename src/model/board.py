
from typing import List, Tuple, Optional
from datetime import datetime
from psycopg2.extras import DictCursor

from .util import get_connection
from .boardinfo import BoardInfo
from .userinfo import UserInfo


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
    def get_post_by_board_id(board_id: int) -> List[Tuple["Board", UserInfo]]:
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
            WHERE board.board_id = %s AND board.deleted = false
            ORDER BY board.created_at DESC
        """

        board_contents = []

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (board_id,))

                for row in cur.fetchall():
                    board = Board(
                        row["post_id"], row["board_id"], row["body"],
                        row["author_user_id"], row["created_at"], False)

                    userinfo = UserInfo(
                        row["author_user_id"], row["author_name"],
                        row["author_created_at"], "", row["author_deleted"])

                    board_contents.append((board, userinfo))

                con.commit()

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


