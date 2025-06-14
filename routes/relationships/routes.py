from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG

relationships_bp = Blueprint('relationships', __name__, url_prefix='/relationships')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@relationships_bp.route('/')
def manage_relationships():
    """管理关系页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取所有关系
        cursor.execute("""
            SELECT mb.*, 
                   m.name AS member_name, 
                   b.name AS band_name
            FROM member_band mb
            JOIN members m ON mb.member_id = m.member_id
            JOIN bands b ON mb.band_id = b.band_id
            ORDER BY band_id, member_id
        """)
        relationships = cursor.fetchall()
        
        # 获取所有乐队和成员
        cursor.execute("SELECT band_id, name FROM bands")
        bands = cursor.fetchall()
        
        cursor.execute("SELECT member_id, name FROM members")
        members = cursor.fetchall()
        
        return render_template('relationships/manage.html', 
                              relationships=relationships, 
                              bands=bands, 
                              members=members)
    
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
        return render_template('relationships/manage.html', 
                              relationships=[], 
                              bands=[], 
                              members=[])
    
    finally:
        cursor.close()
        conn.close()

@relationships_bp.route('/create', methods=['POST'])
def create_relationship():
    """创建新关系"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    band_id = request.form['band_id']
    member_id = request.form['member_id']
    role = request.form['role']
    
    # 验证输入
    if not band_id or not member_id or not role:
        flash('乐队、成员和角色不能为空', 'error')
        return redirect(url_for('relationships.manage_relationships'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查关系是否已存在
        cursor.execute(
            "SELECT * FROM member_band WHERE band_id = %s AND member_id = %s",
            (band_id, member_id)
        )
        if cursor.fetchone():
            flash('该成员已在乐队中，无法重复添加', 'error')
            return redirect(url_for('relationships.manage_relationships'))
        
        # 检查乐队和成员是否存在
        cursor.execute("SELECT band_id FROM bands WHERE band_id = %s", (band_id,))
        if not cursor.fetchone():
            flash('选择的乐队不存在', 'error')
            return redirect(url_for('relationships.manage_relationships'))
        
        cursor.execute("SELECT member_id FROM members WHERE member_id = %s", (member_id,))
        if not cursor.fetchone():
            flash('选择的成员不存在', 'error')
            return redirect(url_for('relationships.manage_relationships'))
        
        # 创建新关系
        cursor.execute(
            "INSERT INTO member_band (band_id, member_id, role) VALUES (%s, %s, %s)",
            (band_id, member_id, role)
        )
        conn.commit()
        flash('关系添加成功', 'success')
    
    except mysql.connector.Error as err:
        if err.errno == 1452:  # 外键约束错误
            flash('乐队或成员不存在', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('relationships.manage_relationships'))

@relationships_bp.route('/update', methods=['POST'])
def update_relationship():
    """更新关系信息"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    band_id = request.form['band_id']
    member_id = request.form['member_id']
    role = request.form['role']
    
    # 验证输入
    if not band_id or not member_id or not role:
        flash('乐队、成员和角色不能为空', 'error')
        return redirect(url_for('relationships.manage_relationships'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查关系是否存在
        cursor.execute(
            "SELECT * FROM member_band WHERE band_id = %s AND member_id = %s",
            (band_id, member_id)
        )
        if not cursor.fetchone():
            flash('关系不存在，无法更新', 'error')
            return redirect(url_for('relationships.manage_relationships'))
        
        # 更新关系
        cursor.execute(
            "UPDATE member_band SET role = %s WHERE band_id = %s AND member_id = %s",
            (role, band_id, member_id)
        )
        conn.commit()
        flash('关系信息更新成功', 'success')
    
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('relationships.manage_relationships'))

@relationships_bp.route('/delete', methods=['POST'])
def delete_relationship():
    """删除关系"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    band_id = request.form['band_id']
    member_id = request.form['member_id']
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查关系是否存在
        cursor.execute(
            "SELECT * FROM member_band WHERE band_id = %s AND member_id = %s",
            (band_id, member_id)
        )
        if not cursor.fetchone():
            flash('关系不存在，无法删除', 'error')
            return redirect(url_for('relationships.manage_relationships'))
        
        # 删除关系
        cursor.execute(
            "DELETE FROM member_band WHERE band_id = %s AND member_id = %s",
            (band_id, member_id)
        )
        conn.commit()
        flash('关系删除成功', 'success')
    
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('relationships.manage_relationships'))