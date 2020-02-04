
from typing import List, Tuple, Optional, NamedTuple
from datetime import datetime
from psycopg2.extras import DictCursor
from .util import get_connection
from model.userinfo import UserInfo


class PagedBoards(NamedTuple):
    boards: List[Tuple["BoardInfo", UserInfo]]
    has_older: bool
    older_until_id: int
    has_newer: bool
    newer_since_id: int


class BoardInfo:
    def __init__(
            self,
            board_id: int,
            name: str,
            owner_user_id: int,
            created_at: datetime,
            deleted: bool) -> None:

        self.board_id = board_id
        self.name = name
        self.owner_user_id = owner_user_id
        self.created_at = created_at
        self.deleted = deleted

    @staticmethod
    def add_board(name: str, owner_user_id: int) -> "BoardInfo":
        sql = """
            INSERT INTO
                boardinfo (name, owner_user_id)
            VALUES (%s, %s)
            RETURNING *
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (name, owner_user_id))
                inserted = BoardInfo(*cur.fetchone())
                con.commit()

        return inserted

    @staticmethod
    def get_board(board_id: int) -> Optional["BoardInfo"]:
        sql = """
            SELECT * FROM boardinfo WHERE board_id = %s AND deleted = false
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (board_id,))
                row = cur.fetchone()
                con.commit()

        if row is None:
            return None
        else:
            return BoardInfo(*row)

    @staticmethod
    def get_board_by_name(name: str) -> Optional["UserInfo"]:
        sql = """
            SELECT * FROM boardinfo WHERE name = %s AND deleted = false
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (name,))
                row = cur.fetchone()
                con.commit()

        if row is None:
            return None
        else:
            return BoardInfo(*row)

    @staticmethod
    def get_boards(count: int = 200) -> PagedBoards:
        sql = """
            SELECT
                boardinfo.board_id AS board_id,
                boardinfo.name AS board_name,
                boardinfo.owner_user_id AS board_owner_user_id,
                boardinfo.created_at AS board_created_at,
                boardinfo.deleted AS board_deleted,
                userinfo.name AS owner_name,
                userinfo.created_at AS owner_created_at
            FROM boardinfo
                INNER JOIN userinfo
                    ON boardinfo.owner_user_id = userinfo.user_id
            WHERE boardinfo.deleted = false
            ORDER BY boardinfo.created_at DESC
            LIMIT %s
        """

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (count + 1,))
                boards = BoardInfo._create_board_list(cur)
                con.commit()

        if len(boards) == count + 1:
            # count+1件のレコードがあれば次のページのさらに過去の書き込みが存在する
            has_older = True
            older_until_id = boards[-1][0].board_id

            # +1の分の要素を削除
            boards.pop()

        else:
            # それ以下であれば書こんお書き込みは存在しない
            has_older = False
            older_until_id = 0

        return PagedBoards(
            boards,
            has_older,
            older_until_id,
            False, 0) # 最新のものから取得するため，前のページは存在しない

    @staticmethod
    def get_boards_older(
            until_id: int,
            count: int = 200) -> PagedBoards:

        sql = """
            SELECT
                boardinfo.board_id      AS board_id,
                boardinfo.name          AS board_name,
                boardinfo.owner_user_id AS board_owner_user_id,
                boardinfo.created_at    AS board_created_at,
                boardinfo.deleted       AS board_deleted,
                userinfo.name           AS owner_name,
                userinfo.created_at     AS owner_created_at
            FROM boardinfo
                INNER JOIN userinfo
                    ON boardinfo.owner_user_id = userinfo.user_id
            WHERE boardinfo.deleted = false
                AND boardinfo.board_id <= %s
            ORDER BY boardinfo.created_at DESC
            LIMIT %s
        """

        sql_newer_page_check = """
            SELECT board_id
            FROM boardinfo
            WHERE deleted = false AND %s < board_id
            ORDER BY created_at ASC
            LIMIT 1
        """

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                # 次のページを取得
                cur.execute(sql, (until_id, count + 1))
                boards = BoardInfo._create_board_list(cur)

                # 前のページを1件だけ取得
                cur.execute(sql_newer_page_check, (until_id,))
                newer_row = cur.fetchone()

                con.commit()

        if len(boards) == count + 1:
            # count+1件のレコードがあれば次のページのさらに過去の書き込みが存在する
            has_older = True
            older_until_id = boards[-1][0].board_id

            # +1の分の要素を削除
            boards.pop()

        else:
            # それ以下であれば書こんお書き込みは存在しない
            has_older = False
            older_until_id = 0

        return PagedBoards(
            boards,
            has_older,
            older_until_id,
            newer_row is not None,
            0 if newer_row is None else newer_row[0])

    @staticmethod
    def get_boards_newer(
            since_id: int,
            count: int = 200) -> PagedBoards:

        sql = """
            SELECT
                boardinfo.board_id      AS board_id,
                boardinfo.name          AS board_name,
                boardinfo.owner_user_id AS board_owner_user_id,
                boardinfo.created_at    AS board_created_at,
                boardinfo.deleted       AS board_deleted,
                userinfo.name           AS owner_name,
                userinfo.created_at     AS owner_created_at
            FROM boardinfo
                INNER JOIN userinfo
                    ON boardinfo.owner_user_id = userinfo.user_id
            WHERE boardinfo.deleted = false
                AND %s <= boardinfo.board_id
            ORDER BY boardinfo.created_at ASC
            LIMIT %s
        """

        sql_older_page_check = """
            SELECT board_id
            FROM boardinfo
            WHERE deleted = false AND board_id < %s
            ORDER BY created_at DESC
            LIMIT 1
        """

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                # 次のページを取得
                cur.execute(sql, (since_id, count + 1))
                boards = BoardInfo._create_board_list(cur)

                # 前のページを1件だけ取得
                cur.execute(sql_older_page_check, (since_id,))
                newer_row = cur.fetchone()

                con.commit()

        if len(boards) == count + 1:
            # count+1件のレコードがあれば次のページのさらに過去の書き込みが存在する
            has_newer = True
            newer_since_id = boards[-1][0].board_id

            # +1の分の要素を削除
            boards.pop()

        else:
            # それ以下であれば書こんお書き込みは存在しない
            has_newer = False
            newer_since_id = 0

        # 古い順でDBから取得しているため新しい順に戻す
        boards.reverse()

        return PagedBoards(
            boards,
            newer_row is not None,
            0 if newer_row is None else newer_row[0],
            has_newer,
            newer_since_id)

    def _create_board_list(cur) -> List[Tuple["BoardInfo", UserInfo]]:
        boards = []

        for row in cur.fetchall():
            board = BoardInfo(
                row["board_id"], row["board_name"],
                row["board_owner_user_id"], row["board_created_at"],
                row["board_deleted"])

            user = UserInfo(
                row["board_owner_user_id"], row["owner_name"],
                row["owner_created_at"], "", False)

            boards.append((board, user))

        return boards

    @staticmethod
    def delete_board(board_id: int) -> None:
        sql = """
            UPDATE boardinfo SET deleted = true WHERE board_id = %s
        """
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (board_id,))
                con.commit()

