from flask import Blueprint, request, jsonify
from database import query

company_bp = Blueprint('company', __name__)


@company_bp.route('/api/companies/search', methods=['GET'])
def search_companies():
    """
    企業検索API（シンプル絞り込み版）

    クエリパラメータ（すべて任意）:
      industry         業界（完全一致）
      min_holidays     年間休日の下限
      max_overtime     残業時間の上限
      remote_work      full / partial / none
      transfer         あり / なし
      arts_or_sciences 不問 / 理系 / 文系
      culture          社風タグ（部分一致）
      job_type         職種（部分一致）
      min_salary       初任給の下限
      limit            最大返却件数（デフォルト5、最大50）
    """
    args = request.args

    # WHERE 句と値を組み立てる
    conditions = []
    params = []

    if args.get('industry'):
        conditions.append('industry = %s')
        params.append(args['industry'])

    if args.get('min_holidays'):
        try:
            conditions.append('annual_holidays >= %s')
            params.append(int(args['min_holidays']))
        except ValueError:
            return jsonify({'error': 'min_holidays は整数で指定してください'}), 400

    if args.get('max_overtime'):
        try:
            conditions.append('overtime_hours <= %s')
            params.append(int(args['max_overtime']))
        except ValueError:
            return jsonify({'error': 'max_overtime は整数で指定してください'}), 400

    if args.get('remote_work'):
        if args['remote_work'] not in ('full', 'partial', 'none'):
            return jsonify({'error': 'remote_work は full/partial/none のいずれか'}), 400
        conditions.append('remote_work = %s')
        params.append(args['remote_work'])

    if args.get('transfer'):
        if args['transfer'] not in ('あり', 'なし'):
            return jsonify({'error': 'transfer は あり/なし のいずれか'}), 400
        conditions.append('transfer = %s')
        params.append(args['transfer'])

    if args.get('arts_or_sciences'):
        if args['arts_or_sciences'] not in ('不問', '理系', '文系'):
            return jsonify({'error': 'arts_or_sciences は 不問/理系/文系 のいずれか'}), 400
        # 「不問」は完全一致、それ以外は「不問」も含めて検索
        if args['arts_or_sciences'] == '不問':
            conditions.append('arts_or_sciences = %s')
            params.append('不問')
        else:
            conditions.append('arts_or_sciences IN (%s, %s)')
            params.append(args['arts_or_sciences'])
            params.append('不問')

    if args.get('culture'):
        conditions.append('culture_tags LIKE %s')
        params.append(f"%{args['culture']}%")

    if args.get('job_type'):
        conditions.append('job_types LIKE %s')
        params.append(f"%{args['job_type']}%")

    if args.get('min_salary'):
        try:
            conditions.append('starting_salary >= %s')
            params.append(int(args['min_salary']))
        except ValueError:
            return jsonify({'error': 'min_salary は整数で指定してください'}), 400

    # limit
    try:
        limit = int(args.get('limit', 5))
        limit = max(1, min(limit, 50))  # 1〜50に収める
    except ValueError:
        limit = 5

    # SQL組み立て
    sql = 'SELECT * FROM companies'
    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)
    sql += f' ORDER BY id ASC LIMIT {limit}'

    results = query(sql, tuple(params), fetchall=True) or []

    return jsonify({
        'count': len(results),
        'companies': results
    })


@company_bp.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """企業1件の詳細を取得"""
    company = query('SELECT * FROM companies WHERE id = %s', (company_id,), fetchone=True)
    if not company:
        return jsonify({'error': '企業が見つかりません'}), 404
    return jsonify(company)


@company_bp.route('/api/companies/search_by_conditions', methods=['POST'])
def search_by_conditions():
    """
    JSON条件で企業検索（Dify連携用）
    リクエストbody例:
      {
        "industry": "IT",
        "max_overtime": 25,
        "culture": "おだやか"
      }
    """
    data = request.get_json() or {}

    conditions = []
    params = []

    if data.get('industry'):
        conditions.append('industry = %s')
        params.append(data['industry'])

    if data.get('min_holidays') is not None:
        try:
            conditions.append('annual_holidays >= %s')
            params.append(int(data['min_holidays']))
        except (ValueError, TypeError):
            pass

    if data.get('max_overtime') is not None:
        try:
            conditions.append('overtime_hours <= %s')
            params.append(int(data['max_overtime']))
        except (ValueError, TypeError):
            pass

    if data.get('remote_work') in ('full', 'partial', 'none'):
        conditions.append('remote_work = %s')
        params.append(data['remote_work'])

    if data.get('transfer') in ('あり', 'なし'):
        conditions.append('transfer = %s')
        params.append(data['transfer'])

    if data.get('arts_or_sciences') in ('不問', '理系', '文系'):
        # 「不問」は完全一致、それ以外は「不問」も含めて検索
        if data['arts_or_sciences'] == '不問':
            conditions.append('arts_or_sciences = %s')
            params.append('不問')
        else:
            conditions.append('arts_or_sciences IN (%s, %s)')
            params.append(data['arts_or_sciences'])
            params.append('不問')

    if data.get('culture'):
        conditions.append('culture_tags LIKE %s')
        params.append(f"%{data['culture']}%")

    if data.get('job_type'):
        conditions.append('job_types LIKE %s')
        params.append(f"%{data['job_type']}%")

    if data.get('min_salary') is not None:
        try:
            conditions.append('starting_salary >= %s')
            params.append(int(data['min_salary']))
        except (ValueError, TypeError):
            pass

    # limit（デフォルト3件・最大5件）
    try:
        limit = int(data.get('limit', 3))
        limit = max(1, min(limit, 5))
    except (ValueError, TypeError):
        limit = 3

    sql = 'SELECT id, company_name, industry, location, description, ' \
          'starting_salary, annual_holidays, overtime_hours, remote_work, ' \
          'culture_tags, job_types FROM companies'
    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)
    sql += f' ORDER BY id ASC LIMIT {limit}'

    results = query(sql, tuple(params), fetchall=True) or []

    return jsonify({
        'count': len(results),
        'companies': results
    })