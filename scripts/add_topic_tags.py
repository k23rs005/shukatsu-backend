import psycopg2

print('=== topic_tagsカラム追加 ===\n')
print('Neon の Database URL を入力してください:')
url = input('> ').strip()

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS topic_tags TEXT DEFAULT '';")
    conn.commit()
    cur.close()
    conn.close()
    print('✅ topic_tags カラム追加完了')
except Exception as e:
    print(f'❌ エラー: {e}')