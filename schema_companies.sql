-- 既存DBに企業テーブルを追加する場合のSQL
USE shukatsu_ai;

-- 企業テーブル
CREATE TABLE IF NOT EXISTS companies (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    company_name      VARCHAR(100) NOT NULL,
    industry          VARCHAR(30)  NOT NULL,
    employees         INT          NOT NULL,
    location          VARCHAR(100) NOT NULL,
    starting_salary   INT          NOT NULL COMMENT '初任給・基本給（万円）',
    annual_holidays   INT          NOT NULL COMMENT '年間休日数',
    overtime_hours    INT          NOT NULL COMMENT '月平均残業時間',
    remote_work       ENUM('full', 'partial', 'none') NOT NULL,
    transfer          ENUM('あり', 'なし') NOT NULL,
    flextime          ENUM('あり', 'なし') NOT NULL,
    job_types         TEXT         NOT NULL COMMENT '募集職種・カンマ区切り',
    arts_or_sciences  ENUM('不問', '理系', '文系') NOT NULL,
    culture_tags      TEXT         NOT NULL COMMENT '社風タグ・カンマ区切り',
    description       TEXT         NOT NULL COMMENT 'AI会話用の一言紹介',
    created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_remote   ON companies(remote_work);
