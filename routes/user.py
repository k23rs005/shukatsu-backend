from flask import Blueprint, request, jsonify, session as flask_session
from database import query, USE_POSTGRES

user_bp = Blueprint('user', __name__)


def get_or_create_user(session_id):
    """session_idからユーザーを取得、なければ作成"""
    account_id = flask_session.get('account_id')
    user = query('SELECT * FROM users WHERE session_id = %s', (session_id,), fetchone=True)
    if not user:
        returning_id = ' RETURNING id' if USE_POSTGRES else ''
        if account_id:
            uid = query(
                f'INSERT INTO users (session_id, account_id) VALUES (%s, %s){returning_id}',
                (session_id, account_id), commit=True
            )
        else:
            uid = query(
                f'INSERT INTO users (session_id) VALUES (%s){returning_id}',
                (session_id,), commit=True
            )
        if isinstance(uid, dict):
            uid = uid['id']
        user = query('SELECT * FROM users WHERE id = %s', (uid,), fetchone=True)
    elif account_id and not user.get('account_id'):
        query(
            'UPDATE users SET account_id = %s WHERE id = %s AND account_id IS NULL',
            (account_id, user['id']), commit=True
        )
        user = query('SELECT * FROM users WHERE id = %s', (user['id'],), fetchone=True)
    return user


@user_bp.route('/api/onboarding', methods=['POST'])
def save_onboarding():
    """オンボーディング結果（型・進捗・期待）を保存"""
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
    user_type = data.get('user_type')
    allowed_types = {'avoid', 'comm', 'lost'}
    if user_type not in allowed_types:
        user_type = None

    if user_type:
        query(
            '''UPDATE users
               SET turn_count = turn_count + 1,
                   dify_conversation_id = %s,
                   user_type = %s
               WHERE id = %s''',
            (data.get('dify_conversation_id'), user_type, user['id']),
            commit=True
        )
    else:
        query(
            '''UPDATE users
               SET turn_count = turn_count + 1,
                   dify_conversation_id = %s
               WHERE id = %s''',
            (data.get('dify_conversation_id'), user['id']),
            commit=True
        )
    return jsonify({'status': 'ok', 'user_type': user_type})
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

@user_bp.route('/api/messages', methods=['POST'])
def save_message():
    """1件のメッセージ（ユーザー発言 or AI返答）を保存する"""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    role       = data.get('role')
    content    = (data.get('content') or '').strip()

    if not session_id or role not in ('user', 'ai') or not content:
        return jsonify({'error': 'session_id, role, contentが必要です'}), 400

    user = get_or_create_user(session_id)
    query(
        'INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)',
        (user['id'], role, content),
        commit=True
    )
    return jsonify({'status': 'ok'})


@user_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """指定セッションの会話履歴を古い順に返す"""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_idが必要です'}), 400

    user = query('SELECT id FROM users WHERE session_id = %s', (session_id,), fetchone=True)
    if not user:
        return jsonify({'messages': []})

    rows = query(
        '''SELECT role, content, created_at
           FROM messages WHERE user_id = %s
           ORDER BY created_at ASC, id ASC''',
        (user['id'],),
        fetchall=True
    )
    return jsonify({'messages': rows or []})
