from flask import Flask
from auth.routes import auth_bp
from routes.bands.routes import bands_bp
from routes.members.routes import members_bp
from routes.relationships.routes import relationships_bp
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(bands_bp)
app.register_blueprint(members_bp)
app.register_blueprint(relationships_bp)

@app.route('/')
def home():
    return "欢迎使用乐队管理系统 <a href='/bands'>管理乐队</a> | <a href='/members'>管理成员</a> | <a href='/relationships'>管理关系</a>"

if __name__ == '__main__':
    app.run(debug=True)