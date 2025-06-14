from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@rooms_bp.route('/')
def manage_rooms():
    """管理房间页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM rooms ORDER BY room_id")
        rooms = cursor.fetchall()
        return render_template('rooms/manage.html', rooms=rooms)
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
        return render_template('rooms/manage.html', rooms=[])
    finally:
        cursor.close()
        conn.close()

@rooms_bp.route('/create', methods=['POST'])
def create_room():
    """创建新房间"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    room_id = request.form['room_id']
    room_type = request.form['type']
    location = request.form.get('location', '')  # 选填项
    
    # 验证输入
    if not room_id:
        flash('房间号不能为空', 'error')
        return redirect(url_for('rooms.manage_rooms'))
    
    # 仓库类型默认不可用
    is_available = '否' if room_type == '仓库' else '是'
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO rooms (room_id, type, location_description, is_available) VALUES (%s, %s, %s, %s)",
            (room_id, room_type, location, is_available)
        )
        conn.commit()
        flash('房间添加成功', 'success')
    except mysql.connector.IntegrityError:
        flash('房间号已存在', 'error')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('rooms.manage_rooms'))

@rooms_bp.route('/update/<room_id>', methods=['POST'])
def update_room(room_id):
    """更新房间信息"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    new_room_id = request.form['room_id']
    room_type = request.form['type']
    location = request.form.get('location', '')
    
    # 验证输入
    if not new_room_id:
        flash('房间号不能为空', 'error')
        return redirect(url_for('rooms.manage_rooms'))
    
    # 仓库类型默认不可用
    is_available = '否' if room_type == '仓库' else request.form.get('is_available', '是')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 更新房间信息（包括房间号）
        cursor.execute(
            "UPDATE rooms SET room_id = %s, type = %s, location_description = %s, is_available = %s WHERE room_id = %s",
            (new_room_id, room_type, location, is_available, room_id)
        )
        conn.commit()
        flash('房间信息更新成功', 'success')
    except mysql.connector.IntegrityError:
        flash('新房间号已存在', 'error')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('rooms.manage_rooms'))

@rooms_bp.route('/delete/<room_id>', methods=['POST'])
def delete_room(room_id):
    """删除房间"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查房间是否被排练预约使用
        cursor.execute("SELECT COUNT(*) FROM rehearsals WHERE room_id = %s", (room_id,))
        if cursor.fetchone()[0] > 0:
            flash('该房间已被排练预约使用，无法删除', 'error')
            return redirect(url_for('rooms.manage_rooms'))
        
        cursor.execute("DELETE FROM rooms WHERE room_id = %s", (room_id,))
        conn.commit()
        flash('房间删除成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('rooms.manage_rooms'))