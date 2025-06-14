from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG
from datetime import datetime as dt, timedelta
import time

rehearsals_bp = Blueprint('rehearsals', __name__, url_prefix='/rehearsals')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@rehearsals_bp.route('/')
def manage_rehearsals():
    """管理排练安排页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取所有排练安排
        cursor.execute("""
            SELECT r.schedule_id, r.band_id, r.room_id, 
                   r.start_time, r.end_time, r.purpose, r.status,
                   b.name AS band_name,
                   rm.type AS room_type
            FROM rehearsals r
            JOIN bands b ON r.band_id = b.band_id
            JOIN rooms rm ON r.room_id = rm.room_id
            ORDER BY r.start_time DESC
        """)
        rehearsals = cursor.fetchall()
        
        # 获取所有乐队和排练室
        cursor.execute("SELECT band_id, name FROM bands ORDER BY name")
        bands = cursor.fetchall()
        
        cursor.execute("SELECT room_id, type FROM rooms WHERE type = '排练室'")
        rooms = cursor.fetchall()
        
        # 获取当前时间，用于设置默认值
        default_start = dt.now().strftime('%Y-%m-%dT%H:%M')
        default_end = (dt.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        
        # 计算当前时间
        now = dt.now()
        
        return render_template('rehearsals/manage.html', 
                              rehearsals=rehearsals, 
                              bands=bands, 
                              rooms=rooms,
                              default_start=default_start,
                              default_end=default_end,
                              now=now)
    
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
        # 异常情况下也传入当前时间
        now = dt.now()
        return render_template('rehearsals/manage.html', 
                              rehearsals=[], 
                              bands=[], 
                              rooms=[],
                              default_start=default_start,
                              default_end=default_end,
                              now=now)
    finally:
        cursor.close()
        conn.close()

@rehearsals_bp.route('/create', methods=['POST'])
def create_rehearsal():
    """创建新排练安排"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    band_id = request.form['band_id']
    room_id = request.form['room_id']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    purpose = request.form.get('purpose', '')
    
    # 验证输入
    if not band_id or not room_id or not start_time or not end_time:
        flash('乐队、房间、开始时间和结束时间不能为空', 'error')
        return redirect(url_for('rehearsals.manage_rehearsals'))
    
    try:
        # 转换时间格式
        start_dt = dt.strptime(start_time, '%Y-%m-%dT%H:%M')
        end_dt = dt.strptime(end_time, '%Y-%m-%dT%H:%M')
        
        # 验证时间合理性
        if end_dt <= start_dt:
            flash('结束时间必须晚于开始时间', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
    except ValueError:
        flash('时间格式无效', 'error')
        return redirect(url_for('rehearsals.manage_rehearsals'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 检查房间是否为排练室
        cursor.execute("""
            SELECT type 
            FROM rooms 
            WHERE room_id = %s
        """, (room_id,))
        room = cursor.fetchone()
        
        if not room:
            flash('选择的房间不存在', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
        
        if room['type'] != '排练室':
            flash('该房间不是排练室，无法预约', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
        
        # 检查时间冲突（只考虑已预约状态）
        cursor.execute("""
            SELECT schedule_id 
            FROM rehearsals 
            WHERE room_id = %s 
              AND status = '已预约'
              AND schedule_id != %s
              AND NOT (end_time <= %s OR start_time >= %s)
        """, (room_id, 0, start_dt, end_dt))
        
        if cursor.fetchone():
            flash('该房间在此时间段已被预约', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
        
        # 创建新排练安排
        cursor.execute(
            """
            INSERT INTO rehearsals 
            (band_id, room_id, start_time, end_time, purpose, status)
            VALUES (%s, %s, %s, %s, %s, '已预约')
            """,
            (band_id, room_id, start_dt, end_dt, purpose)
        )
        
        conn.commit()
        flash('排练安排添加成功', 'success')
        
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('rehearsals.manage_rehearsals'))

@rehearsals_bp.route('/update/<int:schedule_id>', methods=['POST'])
def update_rehearsal(schedule_id):
    """更新排练安排"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    band_id = request.form['band_id']
    room_id = request.form['room_id']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    purpose = request.form.get('purpose', '')
    status = request.form['status']
    
    # 验证输入
    if not band_id or not room_id or not start_time or not end_time:
        flash('乐队、房间、开始时间和结束时间不能为空', 'error')
        return redirect(url_for('rehearsals.manage_rehearsals'))
    
    try:
        # 转换时间格式
        start_dt = dt.strptime(start_time, '%Y-%m-%dT%H:%M')
        end_dt = dt.strptime(end_time, '%Y-%m-%dT%H:%M')
        
        # 验证时间合理性
        if end_dt <= start_dt:
            flash('结束时间必须晚于开始时间', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
    except ValueError:
        flash('时间格式无效', 'error')
        return redirect(url_for('rehearsals.manage_rehearsals'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取原始数据
        cursor.execute("SELECT * FROM rehearsals WHERE schedule_id = %s", (schedule_id,))
        rehearsal = cursor.fetchone()
        
        if not rehearsal:
            flash('排练安排不存在', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
        
        # 检查新房间是否为排练室
        cursor.execute("""
            SELECT type 
            FROM rooms 
            WHERE room_id = %s
        """, (room_id,))
        room = cursor.fetchone()
        
        if not room:
            flash('选择的房间不存在', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
        
        if room['type'] != '排练室':
            flash('该房间不是排练室，无法预约', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
        
        # 检查时间冲突（排除自身）
        cursor.execute("""
            SELECT schedule_id 
            FROM rehearsals 
            WHERE room_id = %s 
              AND schedule_id != %s
              AND status = '已预约'
              AND NOT (end_time <= %s OR start_time >= %s)
        """, (room_id, schedule_id, start_dt, end_dt))
        
        if cursor.fetchone():
            flash('该房间在此时间段已被预约', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
        
        # 如果排练状态改为"取消"，且当前时间在排练时间段内，立即更新房间状态
        if status == '取消' and rehearsal['status'] == '已预约':
            now = dt.now()
            if rehearsal['start_time'] <= now and now <= rehearsal['end_time']:
                # 该排练正在进行中，取消后立即释放房间
                cursor.execute("""
                    UPDATE rooms 
                    SET is_available = '是' 
                    WHERE room_id = %s
                """, (rehearsal['room_id'],))
        
        # 更新排练安排
        cursor.execute(
            """
            UPDATE rehearsals 
            SET band_id = %s, room_id = %s, start_time = %s, 
                end_time = %s, purpose = %s, status = %s
            WHERE schedule_id = %s
            """,
            (band_id, room_id, start_dt, end_dt, purpose, status, schedule_id)
        )
        
        conn.commit()
        flash('排练安排更新成功', 'success')
        
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('rehearsals.manage_rehearsals'))

@rehearsals_bp.route('/delete/<int:schedule_id>', methods=['POST'])
def delete_rehearsal(schedule_id):
    """删除排练安排"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取排练信息
        cursor.execute("SELECT room_id FROM rehearsals WHERE schedule_id = %s", (schedule_id,))
        result = cursor.fetchone()
        if not result:
            flash('排练安排不存在', 'error')
            return redirect(url_for('rehearsals.manage_rehearsals'))
            
        room_id = result['room_id']
        
        # 如果排练正在进行中，立即释放房间
        now = dt.now()
        cursor.execute("""
            SELECT COUNT(*) AS count 
            FROM rehearsals 
            WHERE schedule_id = %s 
              AND status = '已预约'
              AND start_time <= %s 
              AND end_time >= %s
        """, (schedule_id, now, now))
        is_active = cursor.fetchone()['count'] > 0
        
        if is_active:
            cursor.execute("""
                UPDATE rooms 
                SET is_available = '是' 
                WHERE room_id = %s
            """, (room_id,))
        
        # 删除排练安排
        cursor.execute("DELETE FROM rehearsals WHERE schedule_id = %s", (schedule_id,))
        
        conn.commit()
        flash('排练安排删除成功', 'success')
        
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('rehearsals.manage_rehearsals'))