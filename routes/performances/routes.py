from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG

performances_bp = Blueprint('performances', __name__, url_prefix='/performances')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@performances_bp.route('/')
def manage_performances():
    """管理表演页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM performances ORDER BY start_time DESC")
    performances = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('performances/manage.html', performances=performances)

@performances_bp.route('/create', methods=['POST'])
def create_performance():
    """创建新表演"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    name = request.form['name']
    start_time = request.form['start_time']
    duration = request.form['duration']
    location = request.form['location']
    description = request.form.get('description', '')
    
    # 验证输入
    if not name or not start_time or not duration or not location:
        flash('所有必填字段不能为空', 'error')
        return redirect(url_for('performances.manage_performances'))
    
    try:
        duration = int(duration)
    except ValueError:
        flash('持续时间必须是整数', 'error')
        return redirect(url_for('performances.manage_performances'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO performances (name, start_time, duration, location, description) "
            "VALUES (%s, %s, %s, %s, %s)",
            (name, start_time, duration, location, description)
        )
        conn.commit()
        flash('表演添加成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('performances.manage_performances'))

@performances_bp.route('/update/<int:performance_id>', methods=['POST'])
def update_performance(performance_id):
    """更新表演信息"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    name = request.form['name']
    start_time = request.form['start_time']
    duration = request.form['duration']
    location = request.form['location']
    description = request.form.get('description', '')
    
    # 验证输入
    if not name or not start_time or not duration or not location:
        flash('所有必填字段不能为空', 'error')
        return redirect(url_for('performances.manage_performances'))
    
    try:
        duration = int(duration)
    except ValueError:
        flash('持续时间必须是整数', 'error')
        return redirect(url_for('performances.manage_performances'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE performances SET name = %s, start_time = %s, duration = %s, "
            "location = %s, description = %s WHERE performance_id = %s",
            (name, start_time, duration, location, description, performance_id)
        )
        conn.commit()
        flash('表演信息更新成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('performances.manage_performances'))

@performances_bp.route('/delete/<int:performance_id>', methods=['POST'])
def delete_performance(performance_id):
    """删除表演"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM performances WHERE performance_id = %s",
            (performance_id,)
        )
        conn.commit()
        flash('表演删除成功', 'success')
    except mysql.connector.Error as err:
        if err.errno == 1451:  # 外键约束错误
            flash('该表演有关联的曲目信息，请先删除相关曲目', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('performances.manage_performances'))