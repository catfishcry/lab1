from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
import bcrypt
from datetime import datetime, timedelta
from markupsafe import escape
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_for_test")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 用户数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# JWT鉴权中间件，保护接口
def token_required(func):
    def wrapper(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"message":"Token missing! Authentication required"}),401
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(id=payload["user_id"]).first()
        except Exception as e:
            return jsonify({"message":"Invalid or expired token"}),401
        return func(current_user, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ========== 1. 【自定义接口】POST /auth/register 用户注册 ==========
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "username and password required"}), 400

    username = escape(data.get("username"))
    raw_password = data.get("password")

    # 判断用户名是否已经存在
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "username already exists"}), 409

    # bcrypt哈希密码，不存明文
    password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(username=username, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "register success"}), 201

# ========== 2. POST /auth/login 用户登录，获取JWT令牌 ==========
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password_raw = data.get("password")
    user = User.query.filter_by(username=escape(username)).first()
    if not user:
        return jsonify({"message":"Bad username or password"}),401
    if bcrypt.checkpw(password_raw.encode("utf-8"), user.password_hash):
        token = jwt.encode({
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }, app.config["SECRET_KEY"], algorithm="HS256")
        return jsonify({"access_token": token})
    else:
        return jsonify({"message":"Bad username or password"}),401

# ==========3. GET /api/data 受保护接口，返回全部用户列表 ==========
@app.route("/api/data", methods=["GET"])
@token_required
def get_data(current_user):
    user_list = []
    for u in User.query.all():
        user_list.append({
            "id": escape(u.id),
            "username": escape(u.username)
        })
    return jsonify({"users": user_list})

# 初始化数据库，预先创建测试账号 admin / password123
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        hash_pw = bcrypt.hashpw(b"password123", bcrypt.gensalt())
        new_user = User(username="admin", password_hash=hash_pw)
        db.session.add(new_user)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=False)
