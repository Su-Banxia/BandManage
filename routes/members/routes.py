from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG

members_bp = Blueprint('members', __name__, url_prefix='/members')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@members_bp.route('/')
def manage_members():
    """管理成员页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('members/manage.html', members=members)

@members_bp.route('/create', methods=['POST'])
def create_member():
    """创建新成员"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    name = request.form['name']
    phone = request.form['phone']
    
    # 验证输入
    if not name or not phone:
        flash('姓名和电话不能为空', 'error')
        return redirect(url_for('members.manage_members'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO members (name, phone) VALUES (%s, %s)",
            (name, phone)
        )
        conn.commit()
        flash('成员添加成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('members.manage_members'))

@members_bp.route('/update/<int:member_id>', methods=['POST'])
def update_member(member_id):
    """更新成员信息"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    name = request.form['name']
    phone = request.form['phone']
    
    # 验证输入
    if not name or not phone:
        flash('姓名和电话不能为空', 'error')
        return redirect(url_for('members.manage_members'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE members SET name = %s, phone = %s WHERE member_id = %s",
            (name, phone, member_id)
        )
        conn.commit()
        flash('成员信息更新成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('members.manage_members'))

@members_bp.route('/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    """删除成员"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查成员是否作为乐队队长
        cursor.execute("SELECT COUNT(*) FROM bands WHERE leader_id = %s", (member_id,))
        if cursor.fetchone()[0] > 0:
            flash('该成员是乐队队长，无法删除', 'error')
            return redirect(url_for('members.manage_members'))
        
        # 删除成员
        cursor.execute(
            "DELETE FROM members WHERE member_id = %s",
            (member_id,)
        )
        conn.commit()
        flash('成员删除成功', 'success')
    except mysql.connector.Error as err:
        if err.errno == 1451:  # 外键约束错误
            flash('该成员有关联的乐队信息，无法删除', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('members.manage_members'))