# Linux问题诊断指南

如果服务器监控系统在Linux上显示空白或数据为空，请按照以下步骤进行诊断：

## 步骤1: 运行诊断脚本

在Linux服务器上运行诊断脚本：

```bash
cd /path/to/server-monitor
python3 diagnose.py
```

这个脚本会测试：
- 模块导入是否正常
- 数据采集是否工作
- 系统信息是否能获取
- 数据库是否能正常读写

## 步骤2: 检查后端日志

启动服务并查看日志：

```bash
python3 app.py
```

注意查看是否有以下错误信息：
- "GPUtil未安装,GPU监控功能不可用" - 这是正常的，如果没有GPU
- "获取监控数据失败" - 表示数据采集有问题
- "插入数据失败" - 表示数据库有问题
- "成功添加metric_type字段" - 表示数据库迁移成功

## 步骤3: 测试API端点

在另一个终端测试API：

```bash
# 测试当前数据
curl http://localhost:5000/api/current

# 测试系统信息
curl http://localhost:5000/api/system-info

# 测试历史数据
curl http://localhost:5000/api/history/1
```

如果API返回空数据或错误，说明后端有问题。

## 步骤4: 检查浏览器

打开浏览器访问 http://服务器IP:5000

按F12打开开发者工具，检查：

1. **Console标签**: 是否有JavaScript错误
2. **Network标签**:
   - 检查 `/api/current` 请求是否成功
   - 检查 `/api/stream` (SSE) 是否连接成功
   - 查看响应内容是否有数据

## 常见问题

### 问题1: 数据库字段缺失

如果看到 "no such column: metric_type" 错误：

```bash
# 删除旧数据库，让系统重新创建
rm monitor.db
python3 app.py
```

### 问题2: 权限问题

如果看到权限相关错误：

```bash
# 确保当前用户有读写权限
chmod 755 .
chmod 644 *.py
```

### 问题3: 端口被占用

如果5000端口被占用：

```bash
# 查找占用端口的进程
lsof -i :5000

# 或者修改app.py中的端口号
```

### 问题4: 防火墙阻止

如果从其他机器无法访问：

```bash
# 检查防火墙
sudo firewall-cmd --list-ports

# 开放5000端口
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

## 获取更多帮助

如果以上步骤都无法解决问题，请提供：

1. `diagnose.py` 的完整输出
2. `python3 app.py` 的日志输出
3. 浏览器控制台的错误信息
4. API端点的响应内容

这样可以更准确地定位问题。
