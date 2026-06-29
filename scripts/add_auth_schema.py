"""
本番DBにaccountsテーブルとaccount_idカラムを追加する

使い方:
  1. shukatsu-backend フォルダで venv を有効化
  2. Render の PostgreSQL の External Database URL をコピー
  3. python scripts/add_auth_schema.py を実行
  4. プロンプトに External Database URL を貼り付け
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg2


SCHEMA_SQL = """
-- accountsテーブル
CREATE TABLE IF NOT EXISTS accounts (
    id              SERIAL PRIMARY KEY,
    student_id      VARCHAR(20) NOT NULL UNIQUE,
    nickname        VARCHAR(50) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- usersテーブルにaccount_idを追加
ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE;

-- インデックス
CREATE INDEX IF NOT EXISTS idx_accounts_student ON accounts(student_id);
CREATE INDEX IF NOT EXISTS idx_users_account ON users(account_id);
"""


def main():
    print('=== 認証スキーマ追加スクリプト ===\n')
    print('Render の PostgreSQL の External Database URL を入力してください:')
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
    print('\n📋 スキーマを追加中...')
    cursor.execute(SCHEMA_SQL)
    conn.commit()
    cursor.close()
    conn.close()

    print('✅ accountsテーブル作成 & account_idカラム追加 完了')
    print('\n🎉 セットアップ完了！')


if __name__ == '__main__':
    main()