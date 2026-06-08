from flask import Blueprint, request, jsonify
from database import query

admin_bp = Blueprint('admin', __name__)


# ===== 感想投稿（一般ユーザー） =====

@admin_bp.route('/api/reviews', methods=['POST'])
def post_review():
    """感想を投稿する（未承認状態で保存）"""
    data = request.get_json() or {}
    nickname = (data.get('nickname') or '').strip()
    content  = (data.get('content') or '').strip()

    if not nickname or not content:
        return jsonify({'error': 'ニックネームと感想を入力してください'}), 400
    if len(content) > 500:
        return jsonify({'error': '感想は500文字以内で入力してください'}), 400

    query(
        '''INSERT INTO reviews (nickname, user_type, content, is_approved)
           VALUES (%s, %s, %s, 0)''',
        (nickname, data.get('user_type', 'unknown'), content),
        commit=True
    )
    return jsonify({'status': 'ok', 'message': '感想を受け付けました。確認後に公開されます。'})


@admin_bp.route('/api/reviews', methods=['GET'])
def get_approved_reviews():
    """承認済み感想を取得（LP表示用）"""
    reviews = query(
        '''SELECT nickname, user_type, content, created_at
           FROM reviews
           WHERE is_approved = 1
           ORDER BY created_at DESC
           LIMIT 10''',
        fetchall=True
    )
    return jsonify({'reviews': reviews or []})


# ===== 管理者API =====

@admin_bp.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """ダッシュボード用の統計情報"""
    total_users = query('SELECT COUNT(*) AS cnt FROM users', fetchone=True)['cnt']
    total_turns = query('SELECT COALESCE(SUM(turn_count), 0) AS cnt FROM users', fetchone=True)['cnt']
    avg_turns   = query('SELECT COALESCE(AVG(turn_count), 0) AS avg FROM users WHERE turn_count > 0', fetchone=True)['avg']

    type_dist = query(
        '''SELECT user_type, COUNT(*) AS cnt
           FROM users
           GROUP BY user_type''',
        fetchall=True
    )

    recent = query(
        '''SELECT session_id, user_type, turn_count, created_at, updated_at
           FROM users
           ORDER BY updated_at DESC
           LIMIT 20''',
        fetchall=True
    )

    return jsonify({
        'total_users':         total_users,
        'total_conversations': total_turns,
        'avg_turns':           round(float(avg_turns), 1),
        'type_distribution':   type_dist or [],
        'recent_users':        recent or []
    })


@admin_bp.route('/api/admin/reviews', methods=['GET'])
def admin_get_reviews():
    """全感想を取得（管理者用）"""
    reviews = query(
        '''SELECT id, nickname, user_type, content, is_approved, created_at
           FROM reviews
           ORDER BY created_at DESC''',
        fetchall=True
    )
    return jsonify({'reviews': reviews or []})


@admin_bp.route('/api/admin/reviews/<int:review_id>/approve', methods=['POST'])
def approve_review(review_id):
    """感想を承認する"""
    query('UPDATE reviews SET is_approved = 1 WHERE id = %s', (review_id,), commit=True)
    return jsonify({'status': 'ok'})


@admin_bp.route('/api/admin/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """感想を削除する"""
    query('DELETE FROM reviews WHERE id = %s', (review_id,), commit=True)
    return jsonify({'status': 'ok'})
