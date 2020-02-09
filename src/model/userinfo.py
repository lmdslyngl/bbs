
from typing import Optional
from datetime import datetime
import bcrypt
from .util import get_connection


class UserInfo:
    def __init__(
            self,
            user_id: int,
            name: str,
            created_at: datetime,
            password_hash: str,
            deleted: bool) -> None:

        self.user_id = user_id
        self.name = name
        self.created_at = created_at
        self.password_hash = password_hash
        self.deleted = deleted

    @staticmethod
    def add_user(name: str, password: str) -> "UserInfo":
        sql = """
            INSERT INTO userinfo (name, password_hash)
            VALUES (%s, %s)
            RETURNING *
        """

        password_hashed = bcrypt.hashpw(
            password.encode("ascii"), bcrypt.gensalt()).decode("ascii")

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (name, password_hashed))
                inserted = UserInfo(*cur.fetchone())
                con.commit()

        return inserted

    @staticmethod
    def update_user(
            user_id: int,
            name: Optional[str],
            password: Optional[str]) -> "UserInfo":

        set_clause = ""
        placeholders = []

        if name is not None:
            set_clause += "name = %s,"
            placeholders.append(name)

        if password is not None:
            password_hashed = bcrypt.hashpw(
                password.encode("ascii"), bcrypt.gensalt()).decode("ascii")
            set_clause += "password_hash = %s,"
            placeholders.append(password_hashed)

        if len(set_clause) <= 0:
            # 変更なしの場合はNoneを返す
            return None
        else:
            # SET句の最後のコンマを削除
            set_clause = set_clause[:-1]

        sql = """
            UPDATE userinfo
            SET {}
            WHERE user_id = %s
            RETURNING name, created_at
        """.format(set_clause)

        placeholders.append(user_id)

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, placeholders)
                row = cur.fetchone()
                con.commit()

        return UserInfo(user_id, row[0], row[1], "", False)

    @staticmethod
    def find_by_name(name: str) -> "UserInfo":
        sql = """
            SELECT user_id, name, created_at, deleted FROM userinfo WHERE name = %s
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (name,))
                row = cur.fetchone()
                con.commit()

        if row is None:
            return None
        else:
            return UserInfo(row[0], row[1], row[2], "", row[3])

    @staticmethod
    def check_password(name: str, password: str) -> "UserInfo":
        sql = """
            SELECT
                user_id,
                created_at,
                password_hash,
                deleted
            FROM userinfo
            WHERE name = %s
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (name,))
                row = cur.fetchone()
                con.commit()

        if row is None:
            return None

        if row[3]:
            # 削除済みユーザはパスワードチェックを行わない
            return None

        user_password_hash = row[2]
        if bcrypt.checkpw(
                password.encode("ascii"),
                user_password_hash.encode("ascii")):
            return UserInfo(row[0], name, row[1], "", False)
        else:
            return None

    @staticmethod
    def check_password_by_user_id(user_id: int, password: str) -> Optional["UserInfo"]:
        sql = """
            SELECT
                name,
                created_at,
                password_hash
            FROM userinfo
            WHERE user_id = %s AND deleted = false
        """

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (user_id,))
                row = cur.fetchone()
                con.commit()

        if row is None:
            return None

        user_password_hash = row[2]
        if bcrypt.checkpw(
                password.encode("ascii"),
                user_password_hash.encode("ascii")):
            return UserInfo(user_id, row[0], row[1], "", False)
        else:
            return None

    @staticmethod
    def delete_user(user_id: str) -> None:
        sql = """
            UPDATE userinfo SET deleted = true WHERE user_id = %s
        """
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (user_id,))
                con.commit()

