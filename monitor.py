import psutil
import time
import platform
import socket
from datetime import timedelta
from config import Config

# GPU库导入
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError as e:
    GPU_AVAILABLE = False
    print("=" * 60)
    print("警告: GPUtil未安装,GPU监控功能不可用")
    print("=" * 60)
    print("可能原因:")
    print("1. 未在虚拟环境中运行")
    print("2. 依赖未正确安装")
    print("3. 使用了错误的Python解释器")
    print()
    print("解决方案:")
    print("- Windows用户: 运行 start.bat 自动设置环境")
    print("- Linux用户: 激活虚拟环境后运行 pip install -r requirements.txt")
    print("- 诊断问题: python diagnose.py")
    print()
    print("注意: 系统将自动使用磁盘监控模式，其他功能不受影响")
    print("=" * 60)
    print()

class SystemMonitor:
    # 用于存储上一次的网络统计数据
    _last_net_io = None
    _last_net_time = None

    # 配置和GPU检测
    _config = None
    _has_gpu = None
    _gpu_name = None

    @classmethod
    def _init_config(cls):
        """初始化配置"""
        if cls._config is None:
            cls._config = Config()
        return cls._config

    @classmethod
    def _detect_gpu(cls):
        """检测GPU是否可用"""
        if cls._has_gpu is not None:
            return cls._has_gpu

        config = cls._init_config()
        force_mode = config.get('force_mode', 'auto')

        # 强制模式
        if force_mode == 'disk':
            cls._has_gpu = False
            return False
        elif force_mode == 'gpu':
            cls._has_gpu = True
            return True

        # 自动检测
        if not GPU_AVAILABLE:
            cls._has_gpu = False
            return False

        try:
            gpus = GPUtil.getGPUs()
            if gpus and len(gpus) > 0:
                cls._has_gpu = True
                cls._gpu_name = gpus[0].name
                return True
        except Exception as e:
            print(f"GPU检测失败: {e}")

        cls._has_gpu = False
        return False

    @staticmethod
    def get_cpu_usage():
        """获取CPU使用率"""
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_memory_usage():
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            'percent': memory.percent,
            'used': round(memory.used / (1024**3), 2),  # GB
            'total': round(memory.total / (1024**3), 2),  # GB
            'available': round(memory.available / (1024**3), 2)  # GB
        }

    @staticmethod
    def get_disk_usage(path='/'):
        """获取磁盘使用情况"""
        disk = psutil.disk_usage(path)
        return {
            'percent': disk.percent,
            'used': round(disk.used / (1024**3), 2),  # GB
            'total': round(disk.total / (1024**3), 2),  # GB
            'free': round(disk.free / (1024**3), 2)  # GB
        }

    @staticmethod
    def get_gpu_usage(gpu_index=0):
        """获取GPU使用情况"""
        if not GPU_AVAILABLE:
            return None
        try:
            gpus = GPUtil.getGPUs()
            if not gpus or gpu_index >= len(gpus):
                return None

            gpu = gpus[gpu_index]
            return {
                'percent': round(gpu.load * 100, 2),
                'used': round(gpu.memoryUsed / 1024, 2),  # GB
                'total': round(gpu.memoryTotal / 1024, 2),  # GB
                'free': round(gpu.memoryFree / 1024, 2),  # GB
                'name': gpu.name,
                'temperature': gpu.temperature
            }
        except Exception as e:
            print(f"GPU数据采集失败: {e}")
            return None

    @classmethod
    def get_all_data(cls):
        """获取所有监控数据"""
        try:
            config = cls._init_config()
            has_gpu = cls._detect_gpu()

            # 根据GPU检测结果选择数据源
            if has_gpu:
                gpu_index = config.get('gpu_index', 0)
                metric_data = cls.get_gpu_usage(gpu_index)
                metric_type = 'gpu'
                if metric_data is None:
                    # GPU数据获取失败,降级到磁盘监控
                    print("GPU数据获取失败，降级到磁盘监控")
                    disk_path = config.get('disk_path', '/')
                    metric_data = cls.get_disk_usage(disk_path)
                    metric_type = 'disk'
            else:
                disk_path = config.get('disk_path', '/')
                metric_data = cls.get_disk_usage(disk_path)
                metric_type = 'disk'

            return {
                'cpu': cls.get_cpu_usage(),
                'memory': cls.get_memory_usage(),
                'disk': metric_data,  # 复用disk字段存储GPU或磁盘数据
                'network': cls.get_network_usage(),
                'timestamp': time.time(),
                'metric_type': metric_type
            }
        except Exception as e:
            print(f"获取监控数据失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回默认数据避免程序崩溃
            return {
                'cpu': 0,
                'memory': {'percent': 0, 'used': 0, 'total': 0, 'available': 0},
                'disk': {'percent': 0, 'used': 0, 'total': 0, 'free': 0},
                'network': {'upload_speed': 0, 'download_speed': 0, 'total_sent': 0, 'total_recv': 0},
                'timestamp': time.time(),
                'metric_type': 'disk'
            }

    @classmethod
    def get_system_info(cls):
        """获取系统信息"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime = str(timedelta(seconds=int(uptime_seconds)))

        has_gpu = cls._detect_gpu()
        gpu_name = cls._gpu_name if has_gpu else None

        return {
            'hostname': socket.gethostname(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),
            'uptime': uptime,
            'boot_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time)),
            'has_gpu': has_gpu,
            'gpu_name': gpu_name,
            'metric_type': 'gpu' if has_gpu else 'disk'
        }

    @staticmethod
    def get_all_disks():
        """获取所有磁盘分区信息"""
        disks = []
        partitions = psutil.disk_partitions()

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': round(usage.total / (1024**3), 2),
                    'used': round(usage.used / (1024**3), 2),
                    'free': round(usage.free / (1024**3), 2),
                    'percent': usage.percent
                })
            except PermissionError:
                continue

        return disks

    @staticmethod
    def get_network_usage():
        """获取网络使用情况"""
        net_io = psutil.net_io_counters()
        current_time = time.time()

        # 如果是第一次调用，初始化数据
        if SystemMonitor._last_net_io is None:
            SystemMonitor._last_net_io = net_io
            SystemMonitor._last_net_time = current_time
            return {
                'upload_speed': 0,
                'download_speed': 0,
                'total_sent': round(net_io.bytes_sent / (1024**3), 2),
                'total_recv': round(net_io.bytes_recv / (1024**3), 2)
            }

        # 计算时间差
        time_delta = current_time - SystemMonitor._last_net_time

        # 计算速度 (字节/秒)
        upload_speed = (net_io.bytes_sent - SystemMonitor._last_net_io.bytes_sent) / time_delta
        download_speed = (net_io.bytes_recv - SystemMonitor._last_net_io.bytes_recv) / time_delta

        # 更新上一次的数据
        SystemMonitor._last_net_io = net_io
        SystemMonitor._last_net_time = current_time

        return {
            'upload_speed': round(upload_speed / 1024, 2),  # KB/s
            'download_speed': round(download_speed / 1024, 2),  # KB/s
            'total_sent': round(net_io.bytes_sent / (1024**3), 2),  # GB
            'total_recv': round(net_io.bytes_recv / (1024**3), 2)  # GB
        }

    @staticmethod
    def get_top_processes(limit=10):
        """获取CPU和内存占用最高的进程"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 获取进程信息
                pinfo = proc.info
                # 跳过空闲进程，避免与总CPU使用率产生直观冲突（特别是Windows上的 System Idle Process）
                if pinfo['name'] in ('System Idle Process', 'Idle'):
                    continue
                # 单独调用cpu_percent和memory_percent方法
                cpu_percent = proc.cpu_percent(interval=0) / psutil.cpu_count()  # 除以CPU核心数，得到实际百分比
                memory_percent = proc.memory_percent()

                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # 按CPU使用率排序
        cpu_top = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
        # 按内存使用率排序
        mem_top = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]

        return {
            'cpu_top': cpu_top,
            'memory_top': mem_top
        }
