from flask import Blueprint, request, jsonify, session
from database import query, USE_POSTGRES

profile_bp = Blueprint('profile', __name__)

FIELDS = ('school_year', 'interests', 'desired_role', 'desired_location', 'strengths', 'experience', 'work_values')
LIMITS = {'school_year': 30, 'interests': 300, 'desired_role': 120, 'desired_location': 120,
          'strengths': 500, 'experience': 1200, 'work_values': 500}


def ensure_profile_table():
    text_type = 'TEXT' if USE_POSTGRES else 'TEXT'
    account_id_type = 'BIGINT' if USE_POSTGRES else 'BIGINT UNSIGNED'
    query(f'''CREATE TABLE IF NOT EXISTS student_profiles (
        account_id {account_id_type} PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
        school_year VARCHAR(30) NOT NULL DEFAULT '',
        interests VARCHAR(300) NOT NULL DEFAULT '',
        desired_role VARCHAR(120) NOT NULL DEFAULT '',
        desired_location VARCHAR(120) NOT NULL DEFAULT '',
        strengths VARCHAR(500) NOT NULL DEFAULT '',
        experience {text_type} NOT NULL,
        work_values VARCHAR(500) NOT NULL DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''', commit=True)


def require_account():
    account_id = session.get('account_id')
    if not account_id:
        return None
    account = query('SELECT id FROM accounts WHERE id = %s', (account_id,), fetchone=True)
    return account['id'] if account else None


@profile_bp.route('/api/profile', methods=['GET', 'PUT'])
def profile():
    account_id = require_account()
    if not account_id:
        return jsonify({'error': 'ログインしてください'}), 401
    ensure_profile_table()

    if request.method == 'GET':
        row = query('''SELECT school_year, interests, desired_role, desired_location,
                       strengths, experience, work_values, updated_at
                       FROM student_profiles WHERE account_id = %s''', (account_id,), fetchone=True)
        return jsonify({'profile': row or {key: '' for key in FIELDS}})

    data = request.get_json() or {}
    values = {}
    for field in FIELDS:
        value = data.get(field, '')
        if not isinstance(value, str):
            return jsonify({'error': 'プロフィールの入力形式が正しくありません'}), 400
        value = value.strip()
        if len(value) > LIMITS[field]:
            return jsonify({'error': f'{field}は{LIMITS[field]}文字以内で入力してください'}), 400
        values[field] = value

    if USE_POSTGRES:
        sql = '''INSERT INTO student_profiles
                 (account_id, school_year, interests, desired_role, desired_location, strengths, experience, work_values, updated_at)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)
                 ON CONFLICT (account_id) DO UPDATE SET school_year=EXCLUDED.school_year, interests=EXCLUDED.interests,
                 desired_role=EXCLUDED.desired_role, desired_location=EXCLUDED.desired_location, strengths=EXCLUDED.strengths,
                 experience=EXCLUDED.experience, work_values=EXCLUDED.work_values, updated_at=CURRENT_TIMESTAMP'''
    else:
        sql = '''INSERT INTO student_profiles
                 (account_id, school_year, interests, desired_role, desired_location, strengths, experience, work_values, updated_at)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)
                 ON DUPLICATE KEY UPDATE school_year=VALUES(school_year), interests=VALUES(interests),
                 desired_role=VALUES(desired_role), desired_location=VALUES(desired_location), strengths=VALUES(strengths),
                 experience=VALUES(experience), work_values=VALUES(work_values), updated_at=CURRENT_TIMESTAMP'''
    query(sql, (account_id, *(values[field] for field in FIELDS)), commit=True)
    return jsonify({'status': 'ok', 'profile': values})