from flask import Blueprint, request, jsonify
from database import query

user_bp = Blueprint('user', __name__)


def get_or_create_user(session_id):
    """session_idからユーザーを取得、なければ作成"""
    user = query('SELECT * FROM users WHERE session_id = %s', (session_id,), fetchone=True)
    if not user:
        uid = query('INSERT INTO users (session_id) VALUES (%s)', (session_id,), commit=True)
        user = query('SELECT * FROM users WHERE id = %s', (uid,), fetchone=True)
    return user


@user_bp.route('/api/onboarding', methods=['POST'])
def save_onboarding():
    """オンボーディング結果（型・進捗・期待）を保存"""
    from flask import session as flask_session
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_idが必要です'}), 400

    user = get_or_create_user(session_id)

    # ログイン中のaccount_idを取得して紐付け
    account_id = flask_session.get('account_id')

    query(
        '''UPDATE users
           SET user_type = %s, progress = %s, expectation = %s,
               account_id = COALESCE(account_id, %s)
           WHERE id = %s''',
        (
            data.get('user_type', 'unknown'),
            data.get('progress', 'unknown'),
            data.get('expectation', 'unknown'),
            account_id,
            user['id']
        ),
        commit=True
    )
    return jsonify({'status': 'ok', 'user_type': data.get('user_type')})

@user_bp.route('/api/turn', methods=['POST'])
def record_turn():
    """会話の1往復を記録（往復数+1・Difyの会話IDを保存）"""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_idが必要です'}), 400

    user = get_or_create_user(session_id)
    query(
        '''UPDATE users
           SET turn_count = turn_count + 1,
               dify_conversation_id = %s
           WHERE id = %s''',
        (data.get('dify_conversation_id'), user['id']),
        commit=True
    )
    return jsonify({'status': 'ok'})
@user_bp.route('/api/turn/tags', methods=['POST'])
def update_tags():
    """トピックタグを更新する"""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    new_tags = data.get('tags', [])

    if not session_id or not new_tags:
        return jsonify({'status': 'ok'})

    user = get_or_create_user(session_id)

    # 既存タグと新しいタグをマージ（重複なし）
    existing = query(
        'SELECT topic_tags FROM users WHERE id = %s',
        (user['id'],), fetchone=True
    )
    existing_tags = set(
        t.strip() for t in (existing.get('topic_tags') or '').split(',') if t.strip()
    )
    merged = existing_tags | set(new_tags)

    query(
        'UPDATE users SET topic_tags = %s WHERE id = %s',
        (','.join(merged), user['id']),
        commit=True
    )
    return jsonify({'status': 'ok'})