from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DB_CONFIG

songs_bp = Blueprint('performance_songs', __name__, url_prefix='/performance_songs')

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

@songs_bp.route('/')
def manage_songs():
    """管理表演曲目页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    performance_id = request.args.get('performance_id')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # 获取表演信息
    if performance_id:
        cursor.execute("SELECT * FROM performances WHERE performance_id = %s", (performance_id,))
        performance = cursor.fetchone()
    else:
        performance = None
    
    # 获取表演曲目
    if performance_id:
        cursor.execute(
            "SELECT ps.*, b.name AS band_name "
            "FROM performance_songs ps "
            "JOIN bands b ON ps.band_id = b.band_id "
            "WHERE ps.performance_id = %s "
            "ORDER BY ps.song_order", 
            (performance_id,)
        )
        songs = cursor.fetchall()
        
        # 获取当前表演的最大顺序值
        cursor.execute(
            "SELECT MAX(song_order) AS max_order FROM performance_songs WHERE performance_id = %s",
            (performance_id,)
        )
        max_order_result = cursor.fetchone()
        max_order = max_order_result['max_order'] if max_order_result['max_order'] else 0
    else:
        songs = []
        max_order = 0
    
    # 获取所有乐队
    cursor.execute("SELECT band_id, name FROM bands")
    bands = cursor.fetchall()
    
    # 获取所有表演
    cursor.execute("SELECT performance_id, name FROM performances")
    performances = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        'performance_songs/manage.html', 
        songs=songs,
        bands=bands,
        performances=performances,
        current_performance=performance,
        max_order=max_order  # 传递最大顺序值给模板
    )

@songs_bp.route('/create', methods=['POST'])
def create_song():
    """创建新曲目"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    performance_id = request.form['performance_id']
    band_id = request.form['band_id']
    song_name = request.form['song_name']
    song_order = request.form.get('song_order', 1)
    
    # 验证输入
    errors = []
    if not performance_id:
        errors.append('请选择表演')
    if not band_id:
        errors.append('请选择乐队')
    if not song_name:
        errors.append('曲目名称不能为空')
    
    try:
        song_order = int(song_order) if song_order else 1
    except ValueError:
        errors.append('曲目顺序必须是数字')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('performance_songs.manage_songs', performance_id=performance_id))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 检查顺序是否已被使用
        cursor.execute(
            "SELECT COUNT(*) AS count FROM performance_songs "
            "WHERE performance_id = %s AND song_order = %s",
            (performance_id, song_order)
        )
        result = cursor.fetchone()
        if result['count'] > 0:
            flash(f'表演顺序 {song_order} 已被使用，请选择其他顺序', 'error')
            return redirect(url_for('performance_songs.manage_songs', performance_id=performance_id))
        
        # 插入新曲目
        cursor.execute(
            "INSERT INTO performance_songs (performance_id, band_id, song_name, song_order) "
            "VALUES (%s, %s, %s, %s)",
            (performance_id, band_id, song_name, song_order)
        )
        conn.commit()
        flash('曲目添加成功', 'success')
    except mysql.connector.Error as err:
        # 检查是否是唯一约束错误
        if err.errno == 1062:  # MySQL 唯一约束错误码
            flash('该表演顺序已被使用，请选择其他顺序', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('performance_songs.manage_songs', performance_id=performance_id))

@songs_bp.route('/update/<int:song_id>', methods=['POST'])
def update_song(song_id):
    """更新曲目信息"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    performance_id = request.form['performance_id']
    band_id = request.form['band_id']
    song_name = request.form['song_name']
    song_order = request.form['song_order']
    
    # 验证输入
    errors = []
    if not band_id:
        errors.append('请选择乐队')
    if not song_name:
        errors.append('曲目名称不能为空')
    try:
        song_order = int(song_order)
    except ValueError:
        errors.append('曲目顺序必须是数字')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('performance_songs.manage_songs', performance_id=performance_id))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 检查顺序是否已被其他曲目使用
        cursor.execute(
            "SELECT COUNT(*) AS count FROM performance_songs "
            "WHERE performance_id = %s AND song_order = %s AND song_id != %s",
            (performance_id, song_order, song_id)
        )
        result = cursor.fetchone()
        if result['count'] > 0:
            flash(f'表演顺序 {song_order} 已被其他曲目使用，请选择其他顺序', 'error')
            return redirect(url_for('performance_songs.manage_songs', performance_id=performance_id))
        
        # 更新曲目
        cursor.execute(
            "UPDATE performance_songs SET band_id = %s, song_name = %s, song_order = %s "
            "WHERE song_id = %s",
            (band_id, song_name, song_order, song_id)
        )
        conn.commit()
        flash('曲目信息更新成功', 'success')
    except mysql.connector.Error as err:
        # 检查是否是唯一约束错误
        if err.errno == 1062:  # MySQL 唯一约束错误码
            flash('该表演顺序已被使用，请选择其他顺序', 'error')
        else:
            flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('performance_songs.manage_songs', performance_id=performance_id))

@songs_bp.route('/delete/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    """删除曲目"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    performance_id = request.form.get('performance_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM performance_songs WHERE song_id = %s",
            (song_id,)
        )
        conn.commit()
        flash('曲目删除成功', 'success')
    except mysql.connector.Error as err:
        flash(f'数据库错误: {err.msg}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    if performance_id:
        return redirect(url_for('performance_songs.manage_songs', performance_id=performance_id))
    return redirect(url_for('performance_songs.manage_songs'))