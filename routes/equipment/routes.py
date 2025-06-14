from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG
from datetime import date

equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@equipment_bp.route('/')
def manage_equipment():
    """管理设备页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取设备列表
        cursor.execute("""
            SELECT e.*, r.room_id 
            FROM equipment e
            JOIN rooms r ON e.storage_room_id = r.room_id
        """)
        equipment_list = cursor.fetchall()
        
        # 获取所有房间
        cursor.execute("SELECT room_id FROM rooms")
        rooms = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
        equipment_list = []
        rooms = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('equipment/manage.html', 
                           equipment_list=equipment_list, 
                           rooms=rooms)

@equipment_bp.route('/create', methods=['POST'])
def create_equipment():
    """创建新设备"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    equipment_type = request.form['type']
    status = request.form['status']
    storage_room_id = request.form['storage_room_id']
    
    # 验证输入
    if not equipment_type or not storage_room_id:
        flash('设备类型和存放房间不能为空', 'error')
        return redirect(url_for('equipment.manage_equipment'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO equipment (type, status, storage_room_id) VALUES (%s, %s, %s)",
            (equipment_type, status, storage_room_id)
        )
        conn.commit()
        flash('设备添加成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('equipment.manage_equipment'))

@equipment_bp.route('/update/<int:equipment_id>', methods=['POST'])
def update_equipment(equipment_id):
    """更新设备信息"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    equipment_type = request.form['type']
    status = request.form['status']
    storage_room_id = request.form['storage_room_id']
    
    # 验证输入
    if not equipment_type or not storage_room_id:
        flash('设备类型和存放房间不能为空', 'error')
        return redirect(url_for('equipment.manage_equipment'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE equipment SET type = %s, status = %s, storage_room_id = %s WHERE equipment_id = %s",
            (equipment_type, status, storage_room_id, equipment_id)
        )
        conn.commit()
        flash('设备信息更新成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('equipment.manage_equipment'))

@equipment_bp.route('/delete/<int:equipment_id>', methods=['POST'])
def delete_equipment(equipment_id):
    """删除设备"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查设备是否有租赁记录
        cursor.execute("SELECT COUNT(*) FROM equipment_rentals WHERE equipment_id = %s", (equipment_id,))
        if cursor.fetchone()[0] > 0:
            flash('该设备存在租赁记录，无法删除', 'error')
            return redirect(url_for('equipment.manage_equipment'))
        
        # 删除设备
        cursor.execute(
            "DELETE FROM equipment WHERE equipment_id = %s",
            (equipment_id,)
        )
        conn.commit()
        flash('设备删除成功', 'success')
    except mysql.connector.Error as err:
        if err.errno == 1451:  # 外键约束错误
            flash('该设备存在关联信息，无法删除', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('equipment.manage_equipment'))