import os
from flask import g
from dotenv import load_dotenv

load_dotenv()

# 環境変数 DATABASE_URL があれば PostgreSQL、なければ MySQL を使う
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
else:
    import mysql.connector


def get_db():
    """リクエストごとのDB接続を取得（MySQL or PostgreSQL 自動切替）"""
    if 'db' not in g:
        if USE_POSTGRES:
            g.db = psycopg2.connect(DATABASE_URL)
        else:
            g.db = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DB', 'shukatsu_ai'),
                charset='utf8mb4'
            )
    return g.db


def close_db(e=None):
    """リクエスト終了時にDB接続を閉じる"""
    db = g.pop('db', None)
    if db is not None:
        try:
            if USE_POSTGRES:
                db.close()
            else:
                if db.is_connected():
                    db.close()
        except Exception:
            pass


def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """汎用クエリ実行ヘルパー（MySQL/PostgreSQL両対応）"""
    db = get_db()

    if USE_POSTGRES:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        # PostgreSQLは %s のままでOK（mysql-connectorと同じ）
        cursor.execute(sql, params or ())
    else:
        cursor = db.cursor(dictionary=True)
        cursor.execute(sql, params or ())

    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()

    if commit:
        db.commit()
        if USE_POSTGRES:
            # PostgreSQL は lastrowid がないので RETURNING を使うか、必要時に対応
            result = cursor.fetchone() if 'RETURNING' in sql.upper() else None
        else:
            result = cursor.lastrowid

    cursor.close()
    return result