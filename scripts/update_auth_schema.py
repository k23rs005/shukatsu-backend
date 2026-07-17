"""
accountsテーブルの作成・更新スクリプト
- accountsテーブル作成（なければ）
- roleカラム追加
- student_id を login_id にリネーム
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg2


SCHEMA_SQL = """
-- accountsテーブル作成（なければ）
CREATE TABLE IF NOT EXISTS accounts (
    id              SERIAL PRIMARY KEY,
    login_id        VARCHAR(50) NOT NULL UNIQUE,
    nickname        VARCHAR(50) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'student',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- usersテーブルにaccount_idを追加
ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE;

-- インデックス
CREATE INDEX IF NOT EXISTS idx_accounts_login ON accounts(login_id);
CREATE INDEX IF NOT EXISTS idx_accounts_role  ON accounts(role);
CREATE INDEX IF NOT EXISTS idx_users_account  ON users(account_id);
"""


def main():
    print('=== accountsテーブル作成・更新スクリプト ===\n')
    print('Neon の Database URL を入力してください:')
    db_url = input('> ').strip()

    if not db_url.startswith('postgresql://') and not db_url.startswith('postgres://'):
        print('❌ URLの形式が正しくありません')
        return

    print('\n🔌 PostgreSQLに接続中...')
    try:
        conn = psycopg2.connect(db_url)
    except Exception as e:
        print(f'❌ 接続失敗: {e}')
        return
    print('✅ 接続成功')

    cursor = conn.cursor()
    print('\n📋 スキーマを更新中...')
    try:
        cursor.execute(SCHEMA_SQL)
        conn.commit()
        print('✅ accountsテーブル作成 & role カラム追加 完了')
        print('✅ login_id カラムで管理')
    except Exception as e:
        print(f'❌ エラー: {e}')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    print('\n🎉 完了！')


if __name__ == '__main__':
    main()