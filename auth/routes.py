from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from config import DB_CONFIG

auth_bp = Blueprint('auth', __name__)

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册路由"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 验证输入是否为空
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('auth/register.html')
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # 检查用户名是否已存在
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('用户名已存在，请选择其他用户名', 'error')
                return render_template('auth/register.html')
            
            # 创建新用户
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            flash('注册成功！请登录', 'success')
            return redirect(url_for('auth.login'))
        except mysql.connector.Error as err:
            flash(f'数据库错误: {err.msg}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录路由"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 验证输入是否为空
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('auth/login.html')
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)  # 使用字典游标
        
        try:
            # 查询用户
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']  
                session['username'] = user['username']
                flash('登录成功！', 'success')
                return redirect(url_for('home'))
            
            flash('无效的用户名或密码', 'error')
        except mysql.connector.Error as err:
            flash(f'数据库错误: {err.msg}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """用户登出路由"""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('您已成功登出', 'success')
    return redirect(url_for('auth.login'))