from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG
from datetime import datetime

bands_bp = Blueprint('bands', __name__, url_prefix='/bands')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@bands_bp.route('/')
def manage_bands():
    """管理乐队页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取所有乐队及其队长信息
        cursor.execute("""
            SELECT b.*, m.name AS leader_name 
            FROM bands b
            JOIN members m ON b.leader_id = m.member_id
            ORDER BY b.band_id DESC
        """)
        bands = cursor.fetchall()
        
        # 获取所有成员（用于选择队长）
        cursor.execute("SELECT member_id, name FROM members")
        members = cursor.fetchall()
        
        return render_template('bands/manage.html', bands=bands, members=members)
    
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
        return render_template('bands/manage.html', bands=[], members=[])
    
    finally:
        cursor.close()
        conn.close()
    
@bands_bp.route('/create', methods=['POST'])
def create_band():
    """创建新乐队"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # 获取表单数据
    name = request.form['name']
    genre = request.form['genre']
    founding_date = request.form['founding_date']
    leader_id = request.form['leader_id']
    description = request.form['description']
    status = request.form['status']
    
    # 验证必要字段
    if not name or not founding_date or not leader_id:
        flash('乐队名称、成立日期和队长是必填项', 'error')
        return redirect(url_for('bands.manage_bands'))
    
    # 验证日期格式
    try:
        datetime.strptime(founding_date, '%Y-%m-%d')
    except ValueError:
        flash('日期格式无效，请使用YYYY-MM-DD格式', 'error')
        return redirect(url_for('bands.manage_bands'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查队长是否存在
        cursor.execute("SELECT member_id FROM members WHERE member_id = %s", (leader_id,))
        if not cursor.fetchone():
            flash('选择的队长不存在', 'error')
            return redirect(url_for('bands.manage_bands'))
        
        # 插入新乐队
        cursor.execute(
            """
            INSERT INTO bands (name, genre, founding_date, leader_id, description, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, genre, founding_date, leader_id, description, status)
        )
        conn.commit()
        flash('乐队创建成功', 'success')
    
    except mysql.connector.Error as err:
        if err.errno == 1452:  # 外键约束错误
            flash('选择的队长不存在', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('bands.manage_bands'))

@bands_bp.route('/update/<int:band_id>', methods=['POST'])
def update_band(band_id):
    """更新乐队信息"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # 获取表单数据
    name = request.form['name']
    genre = request.form['genre']
    founding_date = request.form['founding_date']
    leader_id = request.form['leader_id']
    description = request.form['description']
    status = request.form['status']
    
    # 验证必要字段
    if not name or not founding_date or not leader_id:
        flash('乐队名称、成立日期和队长是必填项', 'error')
        return redirect(url_for('bands.manage_bands'))
    
    # 验证日期格式
    try:
        datetime.strptime(founding_date, '%Y-%m-%d')
    except ValueError:
        flash('日期格式无效，请使用YYYY-MM-DD格式', 'error')
        return redirect(url_for('bands.manage_bands'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查乐队是否存在
        cursor.execute("SELECT band_id FROM bands WHERE band_id = %s", (band_id,))
        if not cursor.fetchone():
            flash('乐队不存在', 'error')
            return redirect(url_for('bands.manage_bands'))
        
        # 检查队长是否存在
        cursor.execute("SELECT member_id FROM members WHERE member_id = %s", (leader_id,))
        if not cursor.fetchone():
            flash('选择的队长不存在', 'error')
            return redirect(url_for('bands.manage_bands'))
        
        # 更新乐队信息
        cursor.execute(
            """
            UPDATE bands 
            SET name = %s, genre = %s, founding_date = %s, 
                leader_id = %s, description = %s, status = %s
            WHERE band_id = %s
            """,
            (name, genre, founding_date, leader_id, description, status, band_id)
        )
        conn.commit()
        flash('乐队信息更新成功', 'success')
    
    except mysql.connector.Error as err:
        if err.errno == 1452:  # 外键约束错误
            flash('选择的队长不存在', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('bands.manage_bands'))

@bands_bp.route('/delete/<int:band_id>', methods=['POST'])
def delete_band(band_id):
    """删除乐队"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查乐队是否存在
        cursor.execute("SELECT band_id FROM bands WHERE band_id = %s", (band_id,))
        if not cursor.fetchone():
            flash('乐队不存在', 'error')
            return redirect(url_for('bands.manage_bands'))
        
        # 删除乐队
        cursor.execute("DELETE FROM bands WHERE band_id = %s", (band_id,))
        conn.commit()
        flash('乐队删除成功', 'success')
    
    except mysql.connector.Error as err:
        if err.errno == 1451:  # 外键约束错误
            flash('该乐队有关联的成员信息，请先解除关联', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('bands.manage_bands'))