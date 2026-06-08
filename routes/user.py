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
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_idが必要です'}), 400

    user = get_or_create_user(session_id)
    query(
        '''UPDATE users
           SET user_type = %s, progress = %s, expectation = %s
           WHERE id = %s''',
        (
            data.get('user_type', 'unknown'),
            data.get('progress', 'unknown'),
            data.get('expectation', 'unknown'),
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
