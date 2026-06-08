-- データベース作成
CREATE DATABASE IF NOT EXISTS shukatsu_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shukatsu_ai;

-- ===== ユーザーテーブル（型・往復数・統計） =====
CREATE TABLE IF NOT EXISTS users (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    session_id           VARCHAR(64)  NOT NULL UNIQUE,
    user_type            ENUM('avoid', 'comm', 'lost', 'unknown') DEFAULT 'unknown',
    progress             ENUM('none', 'start', 'active', 'unknown') DEFAULT 'unknown',
    expectation          ENUM('listen', 'todo', 'career', 'unknown') DEFAULT 'unknown',
    turn_count           INT          DEFAULT 0,
    dify_conversation_id VARCHAR(64)  DEFAULT NULL,
    created_at           DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at           DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ===== 感想・投稿テーブル =====
CREATE TABLE IF NOT EXISTS reviews (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nickname    VARCHAR(50)  NOT NULL,
    user_type   ENUM('avoid', 'comm', 'lost', 'unknown') DEFAULT 'unknown',
    content     TEXT         NOT NULL,
    is_approved TINYINT(1)   DEFAULT 0,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ===== インデックス =====
CREATE INDEX idx_users_session  ON users(session_id);
CREATE INDEX idx_users_type     ON users(user_type);
CREATE INDEX idx_reviews_approved ON reviews(is_approved);
