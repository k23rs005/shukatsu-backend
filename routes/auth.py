from flask import Blueprint, request, jsonify, session
from database import query
import bcrypt

auth_bp = Blueprint('auth', __name__)


# ===== ユーザー登録 =====

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """新規アカウント作成（学生のみ）"""
    data = request.get_json() or {}
    login_id = (data.get('login_id') or '').strip()
    nickname  = (data.get('nickname') or '').strip()
    password  = data.get('password') or ''

    if not login_id or not nickname or not password:
        return jsonify({'error': 'ID・ニックネーム・パスワードを全て入力してください'}), 400
    if len(password) < 6:
        return jsonify({'error': 'パスワードは6文字以上にしてください'}), 400
    if len(login_id) > 50:
        return jsonify({'error': 'IDは50文字以内で入力してください'}), 400
    if len(nickname) > 50:
        return jsonify({'error': 'ニックネームは50文字以内で入力してください'}), 400

    # 既存ユーザーチェック
    existing = query('SELECT id FROM accounts WHERE login_id = %s', (login_id,), fetchone=True)
    if existing:
        return jsonify({'error': 'このIDは既に登録されています'}), 409

    # パスワードハッシュ化
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 登録（学生固定）
    query(
        '''INSERT INTO accounts (login_id, nickname, password_hash, role)
           VALUES (%s, %s, %s, 'student') RETURNING id''',
        (login_id, nickname, password_hash),
        commit=True
    )

    # 登録直後にログイン状態にする
    new_account = query(
        'SELECT id, login_id, nickname, role FROM accounts WHERE login_id = %s',
        (login_id,), fetchone=True
    )
    session['account_id'] = new_account['id']
    session['role'] = new_account['role']

    return jsonify({
        'status': 'ok',
        'message': 'アカウントを作成しました',
        'account': {
            'id':       new_account['id'],
            'login_id': new_account['login_id'],
            'nickname': new_account['nickname'],
            'role':     new_account['role']
        }
    })


# ===== ログイン =====

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """ログイン（学生・キャリセン共通）"""
    data = request.get_json() or {}
    login_id = (data.get('login_id') or '').strip()
    password  = data.get('password') or ''

    if not login_id or not password:
        return jsonify({'error': 'IDとパスワードを入力してください'}), 400

    # アカウント取得
    account = query(
        'SELECT id, login_id, nickname, password_hash, role FROM accounts WHERE login_id = %s',
        (login_id,), fetchone=True
    )
    if not account:
        return jsonify({'error': 'IDまたはパスワードが間違っています'}), 401

    # パスワード照合
    if not bcrypt.checkpw(password.encode('utf-8'), account['password_hash'].encode('utf-8')):
        return jsonify({'error': 'IDまたはパスワードが間違っています'}), 401

    # セッションに保存
    session['account_id'] = account['id']
    session['role']       = account['role']

    return jsonify({
        'status': 'ok',
        'message': 'ログインしました',
        'account': {
            'id':       account['id'],
            'login_id': account['login_id'],
            'nickname': account['nickname'],
            'role':     account['role']
        }
    })


# ===== ログアウト =====

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """ログアウト"""
    session.pop('account_id', None)
    session.pop('role', None)
    return jsonify({'status': 'ok', 'message': 'ログアウトしました'})


# ===== 現在のログインユーザー =====

@auth_bp.route('/api/auth/me', methods=['GET'])
def me():
    """現在ログイン中のユーザー情報を返す"""
    account_id = session.get('account_id')
    if not account_id:
        return jsonify({'logged_in': False}), 200

    account = query(
        'SELECT id, login_id, nickname, role FROM accounts WHERE id = %s',
        (account_id,), fetchone=True
    )
    if not account:
        session.pop('account_id', None)
        session.pop('role', None)
        return jsonify({'logged_in': False}), 200

    return jsonify({
        'logged_in': True,
        'account': {
            'id':       account['id'],
            'login_id': account['login_id'],
            'nickname': account['nickname'],
            'role':     account['role']
        }
    })