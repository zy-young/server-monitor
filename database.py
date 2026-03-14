import sqlite3

class Database:
    def __init__(self, db_name='monitor.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                memory_used REAL,
                memory_total REAL,
                disk_percent REAL,
                disk_used REAL,
                disk_total REAL
            )
        ''')

        # 添加新字段以支持GPU监控(向后兼容)
        try:
            cursor.execute("ALTER TABLE monitor_data ADD COLUMN metric_type VARCHAR DEFAULT 'disk'")
            print("成功添加metric_type字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                pass  # 字段已存在
            else:
                print(f"添加metric_type字段失败: {e}")

        try:
            cursor.execute("ALTER TABLE monitor_data ADD COLUMN gpu_name VARCHAR")
            print("成功添加gpu_name字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                pass  # 字段已存在
            else:
                print(f"添加gpu_name字段失败: {e}")

        conn.commit()
        conn.close()

    def insert_data(self, data):
        """插入监控数据"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            metric_type = data.get('metric_type', 'disk')
            gpu_name = data.get('disk', {}).get('name') if metric_type == 'gpu' else None

            cursor.execute('''
                INSERT INTO monitor_data
                (cpu_percent, memory_percent, memory_used, memory_total,
                 disk_percent, disk_used, disk_total, metric_type, gpu_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('cpu', 0),
                data.get('memory', {}).get('percent', 0),
                data.get('memory', {}).get('used', 0),
                data.get('memory', {}).get('total', 0),
                data.get('disk', {}).get('percent', 0),
                data.get('disk', {}).get('used', 0),
                data.get('disk', {}).get('total', 0),
                metric_type,
                gpu_name
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"插入数据失败: {e}")
            import traceback
            traceback.print_exc()

    def get_history(self, hours=24):
        """获取历史数据"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, cpu_percent, memory_percent, disk_percent, metric_type
            FROM monitor_data
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp ASC
        ''', (hours,))
        rows = cursor.fetchall()
        conn.close()
        return rows
