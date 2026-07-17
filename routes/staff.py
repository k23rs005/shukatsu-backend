from flask import Blueprint, request, jsonify, session
from database import query

staff_bp = Blueprint('staff', __name__)


def require_staff(f):
    """キャリセン職員のみアクセス可能なデコレータ"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'career_staff':
            return jsonify({'error': 'アクセス権限がありません'}), 403
        return f(*args, **kwargs)
    return decorated


@staff_bp.route('/api/staff/students', methods=['GET'])
@require_staff
def get_students():
    """学生一覧を取得（キャリセン用）"""
    students = query(
        '''SELECT
            a.id,
            a.login_id,
            a.nickname,
            u.user_type,
            u.turn_count,
            u.topic_tags,
            u.updated_at
           FROM accounts a
           LEFT JOIN users u ON u.account_id = a.id
           WHERE a.role = 'student'
           ORDER BY u.updated_at DESC NULLS LAST''',
        fetchall=True
    ) or []

    return jsonify({'students': students})


@staff_bp.route('/api/staff/students/<int:account_id>', methods=['GET'])
@require_staff
def get_student_detail(account_id):
    """個別学生のメタ情報を取得（キャリセン用）"""
    account = query(
        'SELECT id, login_id, nickname FROM accounts WHERE id = %s AND role = %s',
        (account_id, 'student'), fetchone=True
    )
    if not account:
        return jsonify({'error': '学生が見つかりません'}), 404

    user = query(
        '''SELECT user_type, progress, expectation,
                  turn_count, topic_tags, updated_at, created_at
           FROM users WHERE account_id = %s''',
        (account_id,), fetchone=True
    )

    return jsonify({
        'account': account,
        'user':    user or {}
    })