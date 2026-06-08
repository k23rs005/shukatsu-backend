"""
companies.csv を MySQL の companies テーブルに投入するスクリプト

使い方:
  1. shukatsu-backend フォルダで venv を有効化
  2. python scripts/import_companies.py
"""
import os
import csv
import sys
from pathlib import Path

# 親ディレクトリの .env を読むため、パスを追加
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
import mysql.connector

load_dotenv(ROOT / '.env')


def main():
    csv_path = ROOT / 'data' / 'companies.csv'
    if not csv_path.exists():
        print(f'❌ CSVが見つかりません: {csv_path}')
        return

    # DB接続
    try:
        cnx = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'shukatsu_ai'),
            charset='utf8mb4'
        )
    except mysql.connector.Error as e:
        print(f'❌ DB接続失敗: {e}')
        return

    cursor = cnx.cursor()

    # 既存データを全削除（再投入を想定）
    cursor.execute('DELETE FROM companies')
    cursor.execute('ALTER TABLE companies AUTO_INCREMENT = 1')
    print('🗑  既存のcompaniesデータをクリア')

    # CSVを読み込んでINSERT
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

    cnx.commit()
    cursor.close()
    cnx.close()
    print(f'✅ {count}社の企業データを投入しました')


if __name__ == '__main__':
    main()
