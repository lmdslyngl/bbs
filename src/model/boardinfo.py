
from typing import List, Tuple, Optional
from datetime import datetime
from psycopg2.extras import DictCursor
from .util import get_connection
from model.userinfo import UserInfo


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
    def get_boards() -> List[Tuple["BoardInfo", UserInfo]]:
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
        """

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                con.commit()

        board_and_owners = []
        for row in rows:
            board = BoardInfo(
                row["board_id"], row["board_name"],
                row["board_owner_user_id"], row["board_created_at"],
                row["board_deleted"])
            user = UserInfo(
                row["board_owner_user_id"], row["owner_name"],
                row["owner_created_at"], "", False)
            board_and_owners.append((board, user))

        return board_and_owners

    @staticmethod
    def delete_board(board_id: int) -> None:
        sql = """
            UPDATE boardinfo SET deleted = true WHERE board_id = %s
        """
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (board_id,))
                con.commit()

