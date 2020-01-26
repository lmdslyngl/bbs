
import psycopg2
from psycopg2.extras import DictCursor
from .util import get_connection
from .session import Session


class CSRFToken:
    def __init__(
            self,
            session_id: str,
            token: str) -> None:

        self.session_id = session_id
        self.token = token

    @staticmethod
    def add_token(session_id: str) -> "CSRFToken":
        sql = "INSERT INTO csrftoken VALUES (%s, %s) RETURNING *"
        token = Session._generate_session_id()

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (session_id, token))
                row = cur.fetchone()
                con.commit()

        return CSRFToken(*row)

    @staticmethod
    def get_token_by_session_id(session_id: str) -> "CSRFToken":
        sql = "SELECT * FROM csrftoken WHERE session_id = %s"

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (session_id,))
                row = cur.fetchone()
                con.commit()

        return CSRFToken(*row)

    @staticmethod
    def delete_token(session_id: str) -> None:
        sql = "DELETE FROM csrftoken WHERE session_id = %s"

        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(sql, (session_id,))
                con.commit()
