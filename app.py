from flask import Flask, render_template, jsonify, Response
from flask_cors import CORS
import json
import time
from monitor import SystemMonitor
from database import Database

app = Flask(__name__)
CORS(app)

db = Database()
monitor = SystemMonitor()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/current')
def get_current_data():
    """获取当前监控数据"""
    try:
        data = monitor.get_all_data()
        db.insert_data(data)
        return jsonify(data)
    except Exception as e:
        print(f"获取当前数据失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<float:hours>')
def get_history_data(hours):
    """获取历史数据"""
    history = db.get_history(hours)
    result = []
    for row in history:
        result.append({
            'timestamp': row[0],
            'cpu': row[1],
            'memory': row[2],
            'disk': row[3],
            'metric_type': row[4] if len(row) > 4 else 'disk'
        })
    return jsonify(result)

@app.route('/api/stream')
def stream():
    """SSE实时数据流"""
    def generate():
        while True:
            try:
                data = monitor.get_all_data()
                db.insert_data(data)
                yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                print(f"SSE数据生成失败: {e}")
                import traceback
                traceback.print_exc()
            time.sleep(2)  # 每2秒更新一次

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/system-info')
def get_system_info():
    """获取系统信息"""
    return jsonify(monitor.get_system_info())

@app.route('/api/disks')
def get_disks():
    """获取所有磁盘信息"""
    return jsonify(monitor.get_all_disks())

@app.route('/api/processes')
def get_processes():
    """获取进程信息"""
    return jsonify(monitor.get_top_processes())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
