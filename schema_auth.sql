-- accountsテーブル：ログインユーザー情報
CREATE TABLE IF NOT EXISTS accounts (
    id              SERIAL PRIMARY KEY,
    student_id      VARCHAR(20) NOT NULL UNIQUE,
    nickname        VARCHAR(50) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- usersテーブルにaccount_idを追加（既存テーブルへのカラム追加）
ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE;

-- インデックス
CREATE INDEX IF NOT EXISTS idx_accounts_student ON accounts(student_id);
CREATE INDEX IF NOT EXISTS idx_users_account ON users(account_id);