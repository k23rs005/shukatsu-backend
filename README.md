# 就活AI バックエンド（構成1・API専用）

JS版フロントエンドはそのまま使い、データ保存だけをこのFlask + MySQLが担当します。
画面（HTML）は返さず、APIのみを提供します。

## 役割分担
```
[ブラウザ JS版フロント]
   ├─ チャット応答     → Dify API（変更なし）
   └─ データの保存・取得 → このFlaskバックエンドAPI → MySQL
```

---

## セットアップ手順

### 1. 仮想環境を作成・有効化
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. パッケージをインストール
```bash
pip install -r requirements.txt
```

### 3. MySQLにスキーマを適用
```bash
mysql -u root -p < schema.sql
```

### 4. 環境変数を設定
```bash
cp .env.example .env
```
`.env` を開いてMySQLパスワード等を記入。

### 5. 起動
```bash
python app.py
```
`http://localhost:5000` にアクセスして `{"status":"ok"...}` が出れば成功。

---

## APIエンドポイント一覧

| メソッド | URL | 用途 |
|---|---|---|
| POST | /api/onboarding | 型・進捗・期待を保存 |
| POST | /api/turn | 会話1往復を記録（往復数+1） |
| POST | /api/reviews | 感想を投稿 |
| GET  | /api/reviews | 承認済み感想を取得（LP用） |
| GET  | /api/admin/stats | 統計情報（ダッシュボード用） |
| GET  | /api/admin/reviews | 全感想を取得（管理者用） |
| POST | /api/admin/reviews/:id/approve | 感想を承認 |
| DELETE | /api/admin/reviews/:id | 感想を削除 |

---

## 保存するデータ（軽量版）
- **会話本文は保存しません**（Difyが管理）
- users：型・進捗・期待・往復数・DifyのconversationID
- reviews：感想投稿（承認制）

---

## フロント（JS版）からの呼び出し例
```javascript
// オンボーディング結果を保存
fetch('http://localhost:5000/api/onboarding', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: localStorage.getItem('sessionId'),
    user_type: 'avoid',
    progress: 'start',
    expectation: 'listen'
  })
});
```
