from flask import Blueprint, request, jsonify, session
from database import query
import bcrypt

auth_bp = Blueprint('auth', __name__)


# ===== ユーザー登録 =====

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """新規アカウント作成"""
    data = request.get_json() or {}
    student_id = (data.get('student_id') or '').strip()
    nickname   = (data.get('nickname') or '').strip()
    password   = data.get('password') or ''

    # バリデーション
    if not student_id or not nickname or not password:
        return jsonify({'error': '学籍番号・ニックネーム・パスワードを全て入力してください'}), 400
    if len(password) < 6:
        return jsonify({'error': 'パスワードは6文字以上にしてください'}), 400
    if len(student_id) > 20:
        return jsonify({'error': '学籍番号は20文字以内で入力してください'}), 400
    if len(nickname) > 50:
        return jsonify({'error': 'ニックネームは50文字以内で入力してください'}), 400

    # 既存ユーザーチェック
    existing = query('SELECT id FROM accounts WHERE student_id = %s', (student_id,), fetchone=True)
    if existing:
        return jsonify({'error': 'この学籍番号は既に登録されています'}), 409

    # パスワードハッシュ化
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 登録
    query(
        '''INSERT INTO accounts (student_id, nickname, password_hash)
           VALUES (%s, %s, %s) RETURNING id''',
        (student_id, nickname, password_hash),
        commit=True
    )

    # 登録直後にログイン状態にする
    new_account = query('SELECT id, student_id, nickname FROM accounts WHERE student_id = %s', (student_id,), fetchone=True)
    session['account_id'] = new_account['id']

    return jsonify({
        'status': 'ok',
        'message': 'アカウントを作成しました',
        'account': {
            'id': new_account['id'],
            'student_id': new_account['student_id'],
            'nickname': new_account['nickname']
        }
    })


# ===== ログイン =====

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """ログイン"""
    data = request.get_json() or {}
    student_id = (data.get('student_id') or '').strip()
    password   = data.get('password') or ''

    if not student_id or not password:
        return jsonify({'error': '学籍番号とパスワードを入力してください'}), 400

    # アカウント取得
    account = query(
        'SELECT id, student_id, nickname, password_hash FROM accounts WHERE student_id = %s',
        (student_id,),
        fetchone=True
    )
    if not account:
        return jsonify({'error': '学籍番号またはパスワードが間違っています'}), 401

    # パスワード照合
    if not bcrypt.checkpw(password.encode('utf-8'), account['password_hash'].encode('utf-8')):
        return jsonify({'error': '学籍番号またはパスワードが間違っています'}), 401

    # セッションにログイン情報を保存
    session['account_id'] = account['id']

    return jsonify({
        'status': 'ok',
        'message': 'ログインしました',
        'account': {
            'id': account['id'],
            'student_id': account['student_id'],
            'nickname': account['nickname']
        }
    })


# ===== ログアウト =====

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """ログアウト"""
    session.pop('account_id', None)
    return jsonify({'status': 'ok', 'message': 'ログアウトしました'})


# ===== 現在のログインユーザー =====

@auth_bp.route('/api/auth/me', methods=['GET'])
def me():
    """現在ログイン中のユーザー情報を返す"""
    account_id = session.get('account_id')
    if not account_id:
        return jsonify({'logged_in': False}), 200

    account = query(
        'SELECT id, student_id, nickname FROM accounts WHERE id = %s',
        (account_id,),
        fetchone=True
    )
    if not account:
        # アカウントが削除された等
        session.pop('account_id', None)
        return jsonify({'logged_in': False}), 200

    return jsonify({
        'logged_in': True,
        'account': {
            'id': account['id'],
            'student_id': account['student_id'],
            'nickname': account['nickname']
        }
    })