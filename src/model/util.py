
import psycopg2
from datetime import datetime


def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="testrole",
        password="hogehoge",
        dbname="bbsdb")

