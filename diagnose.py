#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断脚本 - 用于诊断服务器监控系统的问题（支持Windows和Linux）
"""

import sys
import json
import os

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8')

def test_environment():
    """测试Python环境"""
    print("=" * 60)
    print("测试1: Python环境检查")
    print("=" * 60)

    # Python版本和路径
    print(f"✓ Python版本: {sys.version}")
    print(f"✓ Python路径: {sys.executable}")

    # 虚拟环境检查
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print(f"✓ 运行在虚拟环境中: {sys.prefix}")
    else:
        print("⚠ 未在虚拟环境中运行（建议使用虚拟环境）")

    # 检查venv目录是否存在
    venv_exists = os.path.exists('venv')
    if venv_exists:
        print("✓ 项目中存在venv目录")
    else:
        print("⚠ 项目中不存在venv目录（建议创建虚拟环境）")

    print()
    return True

def test_gputil():
    """专门测试GPUtil"""
    print("=" * 60)
    print("测试2: GPUtil专项检查")
    print("=" * 60)

    try:
        import GPUtil
        print("✓ GPUtil导入成功")
        print(f"  - GPUtil版本: {GPUtil.__version__ if hasattr(GPUtil, '__version__') else '未知'}")

        # 尝试获取GPU列表
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                print(f"✓ 检测到 {len(gpus)} 个GPU:")
                for i, gpu in enumerate(gpus):
                    print(f"  - GPU {i}: {gpu.name}")
            else:
                print("⚠ 未检测到GPU（这是正常的，如果您的系统没有NVIDIA GPU）")
        except Exception as e:
            print(f"⚠ GPU检测失败: {e}")
            print("  这可能是因为:")
            print("  1. 系统没有NVIDIA GPU")
            print("  2. NVIDIA驱动未安装")
            print("  3. nvidia-smi不可用")

        return True
    except ImportError as e:
        print(f"✗ GPUtil导入失败: {e}")
        print()
        print("解决方案:")
        print("1. 确保在虚拟环境中运行:")
        print("   Windows: venv\\Scripts\\activate.bat")
        print("   Linux: source venv/bin/activate")
        print("2. 安装GPUtil:")
        print("   pip install GPUtil")
        print("3. 或使用start.bat自动设置环境（Windows）")
        return False

def test_dependencies():
    """测试依赖版本"""
    print("=" * 60)
    print("测试3: 依赖版本检查")
    print("=" * 60)

    dependencies = ['psutil', 'flask', 'GPUtil', 'flask_cors']

    for dep in dependencies:
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', '未知')
            print(f"✓ {dep}: {version}")
        except ImportError:
            print(f"✗ {dep}: 未安装")

    print()
    return True

def test_imports():
    """测试模块导入"""
    print("=" * 60)
    print("测试4: 检查项目模块导入")
    print("=" * 60)

    try:
        import psutil
        print("✓ psutil导入成功")
    except ImportError as e:
        print(f"✗ psutil导入失败: {e}")
        return False

    try:
        import flask
        print("✓ Flask导入成功")
    except ImportError as e:
        print(f"✗ Flask导入失败: {e}")
        return False

    try:
        from config import Config
        print("✓ config模块导入成功")
    except ImportError as e:
        print(f"✗ config模块导入失败: {e}")
        return False

    try:
        from monitor import SystemMonitor
        print("✓ monitor模块导入成功")
    except ImportError as e:
        print(f"✗ monitor模块导入失败: {e}")
        return False

    try:
        from database import Database
        print("✓ database模块导入成功")
    except ImportError as e:
        print(f"✗ database模块导入失败: {e}")
        return False

    return True

def test_data_collection():
    """测试数据采集"""
    print("\n" + "=" * 60)
    print("测试5: 测试数据采集")
    print("=" * 60)

    try:
        from monitor import SystemMonitor

        # 测试CPU
        cpu = SystemMonitor.get_cpu_usage()
        print(f"✓ CPU使用率: {cpu}%")

        # 测试内存
        memory = SystemMonitor.get_memory_usage()
        print(f"✓ 内存使用率: {memory['percent']}% ({memory['used']}GB / {memory['total']}GB)")

        # 测试磁盘
        disk = SystemMonitor.get_disk_usage('/')
        print(f"✓ 磁盘使用率: {disk['percent']}% ({disk['used']}GB / {disk['total']}GB)")

        # 测试网络
        network = SystemMonitor.get_network_usage()
        print(f"✓ 网络: 上传 {network['upload_speed']}KB/s, 下载 {network['download_speed']}KB/s")

        # 测试完整数据
        data = SystemMonitor.get_all_data()
        print(f"✓ 完整数据采集成功")
        print(f"  - metric_type: {data.get('metric_type', 'N/A')}")
        print(f"  - timestamp: {data.get('timestamp', 'N/A')}")

        return True
    except Exception as e:
        print(f"✗ 数据采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_info():
    """测试系统信息"""
    print("\n" + "=" * 60)
    print("测试6: 测试系统信息")
    print("=" * 60)

    try:
        from monitor import SystemMonitor
        info = SystemMonitor.get_system_info()

        print(f"✓ 主机名: {info.get('hostname', 'N/A')}")
        print(f"✓ 系统: {info.get('system', 'N/A')} {info.get('release', 'N/A')}")
        print(f"✓ CPU核心: {info.get('cpu_count', 'N/A')}核心 / {info.get('cpu_count_logical', 'N/A')}线程")
        print(f"✓ 内存总量: {info.get('memory_total', 'N/A')}GB")
        print(f"✓ 运行时间: {info.get('uptime', 'N/A')}")
        print(f"✓ GPU检测: has_gpu={info.get('has_gpu', 'N/A')}, gpu_name={info.get('gpu_name', 'N/A')}")
        print(f"✓ metric_type: {info.get('metric_type', 'N/A')}")

        return True
    except Exception as e:
        print(f"✗ 系统信息获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库"""
    print("\n" + "=" * 60)
    print("测试7: 测试数据库")
    print("=" * 60)

    try:
        from database import Database
        from monitor import SystemMonitor

        db = Database('test_monitor.db')
        print("✓ 数据库初始化成功")

        # 测试插入数据
        data = SystemMonitor.get_all_data()
        db.insert_data(data)
        print("✓ 数据插入成功")

        # 测试查询数据
        history = db.get_history(1)
        print(f"✓ 历史数据查询成功，共 {len(history)} 条记录")

        if history:
            print(f"  - 最新记录: {history[-1]}")

        # 清理测试数据库
        import os
        if os.path.exists('test_monitor.db'):
            os.remove('test_monitor.db')
            print("✓ 测试数据库已清理")

        return True
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api():
    """测试API（需要服务运行）"""
    print("\n" + "=" * 60)
    print("测试8: 测试API端点")
    print("=" * 60)
    print("注意: 此测试需要服务正在运行")
    print("请在另一个终端运行: python3 app.py")
    print("然后运行以下命令测试API:")
    print("  curl http://localhost:5000/api/current")
    print("  curl http://localhost:5000/api/system-info")
    print("  curl http://localhost:5000/api/history/1")

def main():
    """主函数"""
    print("服务器监控系统 - 诊断工具")
    print("=" * 60)

    results = []

    # 运行所有测试
    test_environment()  # 环境检查不计入结果
    results.append(("GPUtil检查", test_gputil()))
    test_dependencies()  # 依赖检查不计入结果
    results.append(("模块导入", test_imports()))
    results.append(("数据采集", test_data_collection()))
    results.append(("系统信息", test_system_info()))
    results.append(("数据库", test_database()))

    # 显示API测试说明
    test_api()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n所有测试通过！如果Web界面仍然显示空白，请检查:")
        print("1. 浏览器控制台是否有JavaScript错误")
        print("2. 网络请求是否成功（F12 -> Network标签）")
        print("3. 防火墙是否阻止了5000端口")
    else:
        print("\n部分测试失败，请根据上述错误信息进行修复")

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
