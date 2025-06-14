from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime, date
from config import DB_CONFIG

rentals_bp = Blueprint('equipment_rentals', __name__, url_prefix='/equipment_rentals')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@rentals_bp.route('/')
def manage_rentals():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT er.*, e.type AS equipment_type, 
                m.name AS member_name
            FROM equipment_rentals er
            JOIN equipment e ON er.equipment_id = e.equipment_id
            JOIN members m ON er.borrower_id = m.member_id
            ORDER BY er.due_date
        """)
        rentals = cursor.fetchall()
        
        cursor.execute("SELECT member_id, name FROM members")
        members = cursor.fetchall()
        
        # 修复：使用IN条件兼容不同状态表示法
        cursor.execute("SELECT equipment_id, type FROM equipment WHERE status IN ('可用', 'available')")
        available_equipment = cursor.fetchall()  # 变量名修改
        
        today = date.today()
        
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
        rentals = []
        members = []
        available_equipment = []  # 变量名修改
        today = date.today()
    finally:
        cursor.close()
        conn.close()
    
    # 修复：传递正确的变量名
    return render_template('equipment_rentals/manage.html',
                           rentals=rentals,
                           members=members,
                           available_equipment=available_equipment,
                           today=today)

@rentals_bp.route('/create', methods=['POST'])
def create_rental():
    """创建新租赁记录"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    equipment_id = request.form['equipment_id']
    borrower_id = request.form['borrower_id']
    rent_date = request.form['rent_date']
    due_date = request.form['due_date']
    
    # 验证输入
    if not equipment_id or not borrower_id or not rent_date or not due_date:
        flash('所有字段都必须填写', 'error')
        return redirect(url_for('equipment_rentals.manage_rentals'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 创建租赁记录
        cursor.execute(
            "INSERT INTO equipment_rentals (equipment_id, borrower_id, rent_date, due_date) VALUES (%s, %s, %s, %s)",
            (equipment_id, borrower_id, rent_date, due_date)
        )
        
        # 更新设备状态为借出
        cursor.execute(
            "UPDATE equipment SET status = '借出' WHERE equipment_id = %s",
            (equipment_id,)
        )
        
        conn.commit()
        flash('设备租赁记录添加成功', 'success')
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('equipment_rentals.manage_rentals'))

@rentals_bp.route('/update/<int:rental_id>', methods=['POST'])
def update_rental(rental_id):
    """更新租赁记录"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return_date = request.form.get('return_date', None)  # 可能为空
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取当前租赁记录
        cursor.execute(
            "SELECT equipment_id, return_date FROM equipment_rentals WHERE rental_id = %s",
            (rental_id,)
        )
        rental = cursor.fetchone()
        
        if not rental:
            flash('租赁记录不存在', 'error')
            return redirect(url_for('equipment_rentals.manage_rentals'))
        
        old_return_date = rental['return_date']
        equipment_id = rental['equipment_id']
        
        # 更新租赁记录
        cursor.execute(
            "UPDATE equipment_rentals SET return_date = %s WHERE rental_id = %s",
            (return_date, rental_id)
        )
        
        # 如果归还日期被设置或修改，更新设备状态
        if return_date and not old_return_date:
            # 新设置归还日期，设备变为可用
            cursor.execute(
                "UPDATE equipment SET status = '可用' WHERE equipment_id = %s",
                (equipment_id,)
            )
        elif not return_date and old_return_date:
            # 移除了归还日期（设为空），设备应重新变为借出
            cursor.execute(
                "UPDATE equipment SET status = '借出' WHERE equipment_id = %s",
                (equipment_id,)
            )
        
        conn.commit()
        flash('租赁记录更新成功', 'success')
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('equipment_rentals.manage_rentals'))

@rentals_bp.route('/delete/<int:rental_id>', methods=['POST'])
def delete_rental(rental_id):
    """删除租赁记录"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取租赁记录详情
        cursor.execute(
            "SELECT equipment_id, return_date FROM equipment_rentals WHERE rental_id = %s",
            (rental_id,)
        )
        rental = cursor.fetchone()
        
        if not rental:
            flash('租赁记录不存在', 'error')
            return redirect(url_for('equipment_rentals.manage_rentals'))
        
        equipment_id = rental['equipment_id']
        return_date = rental['return_date']
        
        # 删除租赁记录
        cursor.execute(
            "DELETE FROM equipment_rentals WHERE rental_id = %s",
            (rental_id,)
        )
        
        # 如果设备尚未归还，将其状态重置为可用
        if not return_date:
            cursor.execute(
                "UPDATE equipment SET status = '可用' WHERE equipment_id = %s",
                (equipment_id,)
            )
        
        conn.commit()
        flash('租赁记录删除成功', 'success')
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == 1451:  # 外键约束错误
            flash('该记录存在关联信息，无法删除', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('equipment_rentals.manage_rentals'))