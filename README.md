# 服务器监控系统

一个基于Python Flask的实时服务器监控工具，可以监控CPU、内存、磁盘使用率，并提供Web界面实时展示和历史数据存储。

## 功能特性

- ✅ 实时监控CPU、内存、磁盘使用率
- ✅ 自动检测GPU并监控显存使用率（支持NVIDIA GPU）
- ✅ Web界面可视化展示
- ✅ 历史数据存储（SQLite）
- ✅ 实时数据推送（Server-Sent Events）
- ✅ 响应式设计，支持移动端
- ✅ 可选配置文件支持高级定制
- ✅ 跨平台支持（Windows、Linux）

## Windows快速开始

### 方法1: 一键启动（推荐）

直接双击运行 `start.bat`，脚本会自动：
- 创建Python虚拟环境（如果不存在）
- 安装所有依赖
- 启动应用

然后访问 `http://localhost:5000`

### 方法2: 手动安装

1. 创建虚拟环境：
```bash
python -m venv venv
```

2. 激活虚拟环境：
```bash
venv\Scripts\activate.bat
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
python app.py
```

5. 访问 `http://localhost:5000`

### Windows常见问题

**问题1: "GPUtil未安装,GPU监控功能不可用"**

原因：
- 未在虚拟环境中运行
- 使用了错误的Python解释器（Windows可能有多个Python安装）

解决方案：
1. 使用 `start.bat` 启动（推荐）
2. 或确保在虚拟环境中运行：`venv\Scripts\activate.bat`
3. 运行诊断脚本检查环境：`python diagnose.py`

**问题2: 多个Python版本冲突**

Windows常见多个Python安装（Microsoft Store版、官方版、Anaconda等），导致环境混乱。

解决方案：
- 使用虚拟环境隔离依赖（推荐使用 `start.bat`）
- 或在命令中指定完整Python路径：`C:\Python39\python.exe app.py`

**问题3: 磁盘路径配置**

Windows磁盘路径需要转义反斜杠，在 `config.json` 中设置：
```json
{
  "disk_path": "C:\\\\"
}
```

## Linux安装步骤

### 1. 安装Python依赖

```bash
cd /g/Projects/server-monitor
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 访问Web界面

打开浏览器访问：`http://localhost:5000`

如果需要从其他机器访问，使用：`http://服务器IP:5000`

## 项目结构

```
server-monitor/
├── app.py              # Flask主应用
├── monitor.py          # 监控数据采集模块
├── database.py         # 数据库操作
├── config.py           # 配置管理模块
├── requirements.txt    # Python依赖
├── config.json.example # 配置文件示例
├── monitor.db          # SQLite数据库（运行后自动生成）
├── static/
│   ├── css/
│   │   └── style.css   # 样式文件
│   └── js/
│       └── main.js     # 前端JavaScript
└── templates/
    └── index.html      # 前端页面
```

## 部署到Linux服务器

### 使用systemd服务（推荐）

1. 创建服务文件：

```bash
sudo nano /etc/systemd/system/server-monitor.service
```

2. 添加以下内容：

```ini
[Unit]
Description=Server Monitor Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/server-monitor
ExecStart=/usr/bin/python3 /path/to/server-monitor/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start server-monitor
sudo systemctl enable server-monitor
```

## 故障排查

### 运行诊断脚本

如果遇到问题，首先运行诊断脚本：

```bash
python diagnose.py
```

诊断脚本会检查：
- Python环境和版本
- 虚拟环境状态
- GPUtil安装和GPU检测
- 所有依赖版本
- 模块导入
- 数据采集功能
- 系统信息获取
- 数据库操作

### GPUtil相关问题

**症状**: 运行时提示"GPUtil未安装,GPU监控功能不可用"，但已经安装了GPUtil

**根本原因**: Python环境不一致
- 在一个Python环境中安装了GPUtil
- 但运行 `python app.py` 时使用的是另一个Python解释器

**解决方案**:
1. **使用虚拟环境（强烈推荐）**:
   - Windows: 运行 `start.bat`
   - Linux: 创建并激活venv，然后安装依赖

2. **检查当前Python环境**:
   ```bash
   python diagnose.py
   ```
   查看"Python环境检查"部分，确认Python路径和虚拟环境状态

3. **手动验证GPUtil**:
   ```bash
   python -c "import GPUtil; print(GPUtil.__version__)"
   ```
   如果报错，说明当前环境确实没有GPUtil

4. **重新安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

### 没有GPU也能正常使用

如果您的系统没有NVIDIA GPU，或者GPUtil安装失败：
- 系统会自动降级到磁盘监控模式
- 所有其他功能正常工作
- 不影响CPU、内存、网络监控

## 技术栈

- **后端**: Python + Flask
- **监控**: psutil (系统监控) + GPUtil (GPU监控)
- **数据库**: SQLite
- **前端**: HTML + CSS + JavaScript
- **图表**: Chart.js
- **实时通信**: Server-Sent Events (SSE)

## 注意事项

- 默认监控间隔为2秒
- 历史数据默认保存24小时
- 数据库文件会自动创建在项目根目录
- 确保服务器防火墙开放5000端口

## GPU监控功能

### 自动检测

系统会自动检测是否有NVIDIA GPU：
- **有GPU**: 自动显示GPU使用率（显存使用情况），替换磁盘使用率卡片
- **无GPU**: 继续显示磁盘使用率
- **检测失败**: 自动降级到磁盘监控，不影响系统运行

### 配置文件（可选）

如需自定义行为，可创建 `config.json` 文件（参考 `config.json.example`）：

```json
{
  "force_mode": "auto",
  "gpu_index": 0,
  "disk_path": "/"
}
```

**配置项说明：**
- `force_mode`: 强制模式
  - `"auto"` (默认): 自动检测GPU
  - `"gpu"`: 强制显示GPU监控
  - `"disk"`: 强制显示磁盘监控
- `gpu_index`: GPU索引（多GPU系统时使用，默认0）
- `disk_path`: 磁盘监控路径（默认 `/`，Windows可设置为 `"C:\\"`）

### 依赖说明

- GPUtil需要NVIDIA驱动，但不需要CUDA工具包
- 如果GPUtil安装失败，系统仍可正常运行（自动使用磁盘监控）
- 支持的GPU: NVIDIA系列（通过nvidia-smi）

## 自定义配置

### 通过配置文件（推荐）

创建 `config.json` 文件进行配置（参见上方"GPU监控功能"章节）

### 通过代码修改

可以在 `app.py` 中修改：
- 端口号（默认5000）
- 监控间隔（默认2秒）
