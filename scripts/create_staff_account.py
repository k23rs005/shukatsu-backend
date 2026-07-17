"""
キャリセン職員アカウントを作成するスクリプト
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg2
import bcrypt

print('=== キャリセン職員アカウント作成 ===\n')
print('Neon の Database URL を入力してください:')
url = input('> ').strip()

print('\nログインID（例：csc-staff）:')
login_id = input('> ').strip()

print('ニックネーム（例：キャリセン職員）:')
nickname = input('> ').strip()

print('パスワード（6文字以上）:')
password = input('> ').strip()

if len(password) < 6:
    print('❌ パスワードは6文字以上にしてください')
    sys.exit(1)

password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO accounts (login_id, nickname, password_hash, role)
           VALUES (%s, %s, %s, 'career_staff')
           ON CONFLICT (login_id) DO NOTHING''',
        (login_id, nickname, password_hash)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f'\n✅ キャリセンアカウント作成完了')
    print(f'   ID: {login_id}')
    print(f'   ニックネーム: {nickname}')
    print(f'   role: career_staff')
except Exception as e:
    print(f'❌ エラー: {e}')