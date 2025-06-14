from flask import Flask, render_template
from auth.routes import auth_bp
from routes.bands.routes import bands_bp
from routes.members.routes import members_bp
from routes.relationships.routes import relationships_bp
from routes.rooms.routes import rooms_bp
from routes.rehearsals.routes import rehearsals_bp
from config import SECRET_KEY

import time
from threading import Thread
import mysql.connector
from config import DB_CONFIG
from datetime import datetime

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(bands_bp)
app.register_blueprint(members_bp)
app.register_blueprint(relationships_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(rehearsals_bp)

def get_db():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)

def update_room_availability():
    """更新所有房间的可用性状态"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    now = datetime.now()
    
    try:
        # 获取所有排练室
        cursor.execute("SELECT room_id FROM rooms WHERE type = '排练室'")
        rooms = cursor.fetchall()
        
        for room in rooms:
            room_id = room['room_id']
            
            # 检查该房间是否有正在进行的排练（已预约状态且当前时间在排练时间内）
            cursor.execute("""
                SELECT COUNT(*) AS count 
                FROM rehearsals 
                WHERE room_id = %s 
                  AND status = '已预约'
                  AND start_time <= %s 
                  AND end_time >= %s
            """, (room_id, now, now))
            result = cursor.fetchone()
            
            # 如果有排练正在进行，房间不可用；否则可用
            new_status = '否' if result['count'] > 0 else '是'
            
            # 更新房间状态
            cursor.execute("""
                UPDATE rooms 
                SET is_available = %s 
                WHERE room_id = %s
            """, (new_status, room_id))
        
        conn.commit()
    except mysql.connector.Error as err:
        print(f"更新房间状态错误: {err.msg}")
    finally:
        cursor.close()
        conn.close()

def background_scheduler():
    """后台调度器，定期更新房间状态"""
    while True:
        print("正在更新房间可用性状态...")
        try:
            update_room_availability()
        except Exception as e:
            print(f"更新房间状态失败: {e}")
        
        # 每5分钟运行一次
        time.sleep(30)

def start_background_scheduler():
    """启动后台调度器线程"""
    scheduler_thread = Thread(target=background_scheduler)
    scheduler_thread.daemon = True  # 设置为守护线程，这样当主线程退出时它会自动退出
    scheduler_thread.start()

@app.route('/')
def home():
    """系统主页"""
    return render_template('index.html')

if __name__ == '__main__':
    # 启动后台调度器
    start_background_scheduler()
    
    # 运行 Flask 应用
    app.run(debug=True)