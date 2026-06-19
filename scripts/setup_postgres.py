"""
PostgreSQL セットアップスクリプト
- テーブル作成（users / reviews / companies）
- companies.csv から50社を投入

使い方:
  1. shukatsu-backend フォルダで venv を有効化
  2. Render の PostgreSQL の External Database URL をコピー
  3. python scripts/setup_postgres.py を実行
  4. プロンプトに External Database URL を貼り付け
"""
import os
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg2


SCHEMA_SQL = """
-- usersテーブル
CREATE TABLE IF NOT EXISTS users (
    id                   SERIAL PRIMARY KEY,
    session_id           VARCHAR(64) NOT NULL UNIQUE,
    user_type            VARCHAR(20) DEFAULT 'unknown',
    progress             VARCHAR(20) DEFAULT 'unknown',
    expectation          VARCHAR(20) DEFAULT 'unknown',
    turn_count           INT DEFAULT 0,
    dify_conversation_id VARCHAR(64) DEFAULT NULL,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- reviewsテーブル
CREATE TABLE IF NOT EXISTS reviews (
    id          SERIAL PRIMARY KEY,
    nickname    VARCHAR(50) NOT NULL,
    user_type   VARCHAR(20) DEFAULT 'unknown',
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- companiesテーブル
CREATE TABLE IF NOT EXISTS companies (
    id                INT PRIMARY KEY,
    company_name      VARCHAR(100) NOT NULL,
    industry          VARCHAR(30)  NOT NULL,
    employees         INT          NOT NULL,
    location          VARCHAR(100) NOT NULL,
    starting_salary   INT          NOT NULL,
    annual_holidays   INT          NOT NULL,
    overtime_hours    INT          NOT NULL,
    remote_work       VARCHAR(10)  NOT NULL,
    transfer          VARCHAR(10)  NOT NULL,
    flextime          VARCHAR(10)  NOT NULL,
    job_types         TEXT         NOT NULL,
    arts_or_sciences  VARCHAR(10)  NOT NULL,
    culture_tags      TEXT         NOT NULL,
    description       TEXT         NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_users_session     ON users(session_id);
CREATE INDEX IF NOT EXISTS idx_users_type        ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_reviews_created   ON reviews(created_at);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_remote   ON companies(remote_work);
"""


def main():
    print('=== PostgreSQL セットアップスクリプト ===\n')

    # External Database URL を入力
    print('Render の PostgreSQL の External Database URL を入力してください:')
    print('（postgresql://user:pass@host/dbname の形式）')
    db_url = input('> ').strip()

    if not db_url.startswith('postgresql://') and not db_url.startswith('postgres://'):
        print('❌ URLの形式が正しくありません')
        return

    # CSV読み込み
    csv_path = ROOT / 'data' / 'companies.csv'
    if not csv_path.exists():
        print(f'❌ CSVが見つかりません: {csv_path}')
        return

    print('\n🔌 PostgreSQLに接続中...')
    try:
        conn = psycopg2.connect(db_url)
    except Exception as e:
        print(f'❌ 接続失敗: {e}')
        return
    print('✅ 接続成功')

    cursor = conn.cursor()

    # テーブル作成
    print('\n📋 テーブルを作成中...')
    cursor.execute(SCHEMA_SQL)
    conn.commit()
    print('✅ テーブル作成完了（users / reviews / companies）')

    # 既存の企業データを削除
    print('\n🗑  既存の企業データをクリア中...')
    cursor.execute('DELETE FROM companies')
    conn.commit()

    # 50社のデータを投入
    print('\n📥 50社のデータを投入中...')
    insert_sql = '''
        INSERT INTO companies (
            id, company_name, industry, employees, location,
            starting_salary, annual_holidays, overtime_hours,
            remote_work, transfer, flextime,
            job_types, arts_or_sciences, culture_tags, description
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s
        )
    '''

    count = 0
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(insert_sql, (
                int(row['id']),
                row['company_name'],
                row['industry'],
                int(row['employees']),
                row['location'],
                int(row['starting_salary']),
                int(row['annual_holidays']),
                int(row['overtime_hours']),
                row['remote_work'],
                row['transfer'],
                row['flextime'],
                row['job_types'],
                row['arts_or_sciences'],
                row['culture_tags'],
                row['description']
            ))
            count += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f'✅ {count}社の企業データを投入しました')
    print('\n🎉 セットアップ完了！')


if __name__ == '__main__':
    main()
