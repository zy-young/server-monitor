#!/bin/bash
# Linux诊断脚本

echo "=== 测试1: 检查Python模块导入 ==="
python3 -c "from monitor import SystemMonitor; print('monitor模块导入成功')"

echo -e "\n=== 测试2: 测试数据采集 ==="
python3 -c "from monitor import SystemMonitor; import json; data = SystemMonitor.get_all_data(); print(json.dumps(data, indent=2))"

echo -e "\n=== 测试3: 测试系统信息 ==="
python3 -c "from monitor import SystemMonitor; import json; info = SystemMonitor.get_system_info(); print(json.dumps(info, indent=2))"

echo -e "\n=== 测试4: 检查数据库 ==="
python3 -c "from database import Database; db = Database(); print('数据库初始化成功')"

echo -e "\n=== 测试5: 测试API端点（需要先启动服务） ==="
echo "请在另一个终端运行: python3 app.py"
echo "然后运行: curl http://localhost:5000/api/current"
