import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import close_db
from routes.user import user_bp
from routes.admin import admin_bp
from routes.company import company_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# JS版フロントからのアクセスを許可（構成1）
frontend_origin = os.getenv('FRONTEND_ORIGIN', 'http://127.0.0.1:5500')
CORS(app, resources={r'/api/*': {'origins': [frontend_origin, 'http://localhost:5500']}})

# DBクリーンアップ
app.teardown_appcontext(close_db)

# Blueprint登録
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)


@app.route('/')
def health():
    """疎通確認用"""
    return jsonify({'status': 'ok', 'message': '就活AI バックエンド稼働中'})


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development', port=5000)
