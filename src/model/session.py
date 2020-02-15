
from typing import Tuple, Optional
from datetime import datetime
import secrets
import string
import psycopg2
from psycopg2.extras import DictCursor
from .util import get_connection
from .userinfo import UserInfo


class Session:
    def __init__(
            self,
            session_id: str,
            user_id: int,
            expire_at: datetime,
            created_at: datetime) -> None:

        self.session_id = session_id
        self.user_id = user_id
        self.created_at = created_at
        self.expire_at = expire_at

    @staticmethod
    def add_session(user_id: int) -> "Session":
        return Session._add_session_internal(user_id)

    @staticmethod
    def _add_session_internal(user_id: int, num_trying: int = 1) -> "Session":
        if 10 < num_trying:
            return None

        try:
            sql = """
                INSERT INTO session
                    (session_id, user_id)
                VALUES (%s, %s)
                RETURNING *
            """

            session_id = Session._generate_session_id()

            with get_connection() as con:
                with con.cursor() as cur:
                    cur.execute(sql, (session_id, user_id))
                    inserted = Session(*cur.fetchone())
                    con.commit()

            return inserted

        except psycopg2.errors.UniqueViolation as e:
            Session._add_session_internal(user_id, num_trying + 1)

    @staticmethod
    def _generate_session_id() -> str:
        chars = string.ascii_letters + string.digits
        return "".join([secrets.choice(chars) for _ in range(32)])

    @staticmethod
    def get_user_and_session_by_session_id(
            session_id: str) -> Optional[Tuple[UserInfo, "Session"]]:

        sql = """
            SELECT
                session.session_id  AS session_id,
                session.user_id     AS user_id,
                session.expire_at   AS session_expire_at,
                session.created_at  AS session_created_at,
                userinfo.name       AS user_name,
                userinfo.created_at AS user_created_at
            FROM session
                INNER JOIN userinfo
                    ON session.user_id = userinfo.user_id
            WHERE session.session_id = %s AND userinfo.deleted = false
        """

        with get_connection() as con:
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (session_id,))
                row = cur.fetchone()
                con.commit()

        if row is None:
            return None

        session = Session(
            row["session_id"], row["user_id"],
            row["session_expire_at"], row["session_created_at"])

        userinfo = UserInfo(
            row["user_id"], row["user_name"],
            row["user_created_at"], "", False)

        return (userinfo, session)

    @staticmethod
    def delete_session(session_id: str) -> None:
        sql = """
            DELETE FROM session WHERE session_id = %s
        """
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (session_id,))
                con.commit()

    def is_expired(self) -> bool:
        return self.expire_at < datetime.now()


