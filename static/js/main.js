// 初始化图表
let historyChart;
let currentMetricType = 'disk';  // 当前指标类型: disk 或 gpu

// 初始化历史图表
function initChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CPU使用率 (%)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4
                },
                {
                    label: '内存使用率 (%)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.4
                },
                {
                    label: '磁盘/GPU使用率 (%)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// 更新实时数据显示
function updateRealTimeData(data) {
    // 更新CPU
    document.getElementById('cpu-value').textContent = data.cpu.toFixed(1) + '%';
    document.getElementById('cpu-progress').style.width = data.cpu + '%';

    // 更新内存
    document.getElementById('memory-value').textContent = data.memory.percent.toFixed(1) + '%';
    document.getElementById('memory-progress').style.width = data.memory.percent + '%';
    document.getElementById('memory-detail').textContent =
        `已用: ${data.memory.used}GB / 总计: ${data.memory.total}GB`;

    // 动态更新磁盘/GPU卡片
    const metricType = data.metric_type || 'disk';
    currentMetricType = metricType;
    const metricTitle = document.getElementById('metric-title');

    if (metricType === 'gpu') {
        metricTitle.textContent = 'GPU使用率';
        document.getElementById('disk-value').textContent = data.disk.percent.toFixed(1) + '%';
        document.getElementById('disk-progress').style.width = data.disk.percent + '%';

        // 显示GPU详细信息
        let detailText = `显存: ${data.disk.used}GB / ${data.disk.total}GB`;
        if (data.disk.name) {
            detailText += ` | ${data.disk.name}`;
        }
        if (data.disk.temperature !== undefined && data.disk.temperature !== null) {
            detailText += ` | 温度: ${data.disk.temperature}°C`;
        }
        document.getElementById('disk-detail').textContent = detailText;
    } else {
        metricTitle.textContent = '磁盘使用率';
        document.getElementById('disk-value').textContent = data.disk.percent.toFixed(1) + '%';
        document.getElementById('disk-progress').style.width = data.disk.percent + '%';
        document.getElementById('disk-detail').textContent =
            `已用: ${data.disk.used}GB / 总计: ${data.disk.total}GB`;
    }

    // 更新网络
    if (data.network) {
        const uploadSpeed = data.network.upload_speed;
        const downloadSpeed = data.network.download_speed;

        // 格式化速度显示
        document.getElementById('upload-speed').textContent =
            uploadSpeed >= 1024 ? `${(uploadSpeed / 1024).toFixed(2)} MB/s` : `${uploadSpeed.toFixed(2)} KB/s`;
        document.getElementById('download-speed').textContent =
            downloadSpeed >= 1024 ? `${(downloadSpeed / 1024).toFixed(2)} MB/s` : `${downloadSpeed.toFixed(2)} KB/s`;
        document.getElementById('network-detail').textContent =
            `总发送: ${data.network.total_sent}GB / 总接收: ${data.network.total_recv}GB`;
    }

    // 更新最后更新时间
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { hour12: false });
    document.getElementById('update-time').textContent = timeString;

    // 更新服务器状态
    updateServerStatus(data.cpu, data.memory.percent);
}

// 更新服务器状态指示器
function updateServerStatus(cpuPercent, memoryPercent) {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');

    // 移除所有状态类
    statusDot.classList.remove('warning', 'danger');

    if (cpuPercent > 90 && memoryPercent > 90) {
        // 红色：CPU和内存都超过90%
        statusDot.classList.add('danger');
        statusText.textContent = '不健康';
        statusText.style.color = '#ef4444';
    } else if (cpuPercent > 90 || memoryPercent > 90) {
        // 黄色：CPU或内存任一超过90%
        statusDot.classList.add('warning');
        statusText.textContent = '警告';
        statusText.style.color = '#f59e0b';
    } else {
        // 绿色：正常
        statusText.textContent = '正常';
        statusText.style.color = '#10b981';
    }
}

// 连接SSE实时数据流
function connectSSE() {
    const eventSource = new EventSource('/api/stream');

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateRealTimeData(data);
    };

    eventSource.onerror = function(error) {
        console.error('SSE连接错误:', error);
        eventSource.close();
        setTimeout(connectSSE, 5000);
    };
}

// 加载历史数据
async function loadHistoryData() {
    try {
        const response = await fetch('/api/history/0.167');  // 10分钟 = 0.167小时
        const data = await response.json();

        const labels = [];
        const cpuData = [];
        const memoryData = [];
        const diskData = [];

        data.forEach(item => {
            // SQLite 默认使用 UTC 时间，这里按 UTC 解析再转换为浏览器本地时间
            const date = new Date(item.timestamp + 'Z');
            labels.push(date.toLocaleTimeString('zh-CN'));
            cpuData.push(item.cpu);
            memoryData.push(item.memory);
            diskData.push(item.disk);
        });

        // 动态更新图表标签
        const metricLabel = currentMetricType === 'gpu' ? 'GPU使用率 (%)' : '磁盘使用率 (%)';
        historyChart.data.datasets[2].label = metricLabel;

        historyChart.data.labels = labels;
        historyChart.data.datasets[0].data = cpuData;
        historyChart.data.datasets[1].data = memoryData;
        historyChart.data.datasets[2].data = diskData;
        historyChart.update();
    } catch (error) {
        console.error('加载历史数据失败:', error);
    }
}

// 加载系统信息
async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system-info');
        const data = await response.json();

        document.getElementById('hostname').textContent = data.hostname;
        document.getElementById('system-version').textContent =
            `${data.system} ${data.release}`;
        document.getElementById('cpu-cores').textContent =
            `${data.cpu_count}核心 / ${data.cpu_count_logical}线程`;
        document.getElementById('memory-total').textContent =
            `${data.memory_total} GB`;
        document.getElementById('uptime').textContent = data.uptime;
        document.getElementById('boot-time').textContent = data.boot_time;

        // 记录GPU信息
        if (data.has_gpu && data.metric_type === 'gpu') {
            currentMetricType = 'gpu';
            console.log('检测到GPU:', data.gpu_name);
        }
    } catch (error) {
        console.error('加载系统信息失败:', error);
    }
}

// 加载磁盘信息
async function loadDiskInfo() {
    try {
        const response = await fetch('/api/disks');
        const disks = await response.json();

        const tbody = document.getElementById('disk-table-body');
        tbody.innerHTML = '';

        disks.forEach(disk => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${disk.mountpoint}</td>
                <td>${disk.device}</td>
                <td>${disk.fstype}</td>
                <td>${disk.total} GB</td>
                <td>${disk.used} GB</td>
                <td>${disk.free} GB</td>
                <td>
                    <div class="usage-cell">
                        <div class="usage-bar">
                            <div class="usage-fill" style="width: ${disk.percent}%"></div>
                        </div>
                        <span class="usage-text">${disk.percent.toFixed(1)}%</span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('加载磁盘信息失败:', error);
    }
}

// 加载进程信息
async function loadProcessInfo() {
    try {
        const response = await fetch('/api/processes');
        const data = await response.json();

        // 更新CPU进程表
        const cpuBody = document.getElementById('cpu-process-body');
        cpuBody.innerHTML = '';
        data.cpu_top.forEach(proc => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${proc.pid}</td>
                <td>${proc.name}</td>
                <td>${proc.cpu_percent.toFixed(1)}%</td>
            `;
            cpuBody.appendChild(row);
        });

        // 更新内存进程表
        const memBody = document.getElementById('memory-process-body');
        memBody.innerHTML = '';
        data.memory_top.forEach(proc => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${proc.pid}</td>
                <td>${proc.name}</td>
                <td>${proc.memory_percent.toFixed(1)}%</td>
            `;
            memBody.appendChild(row);
        });
    } catch (error) {
        console.error('加载进程信息失败:', error);
    }
}

// 页面初始化
window.onload = function() {
    initChart();
    loadSystemInfo();
    loadDiskInfo();
    loadProcessInfo();
    connectSSE();
    loadHistoryData();
    setInterval(loadHistoryData, 30000);
    setInterval(loadDiskInfo, 10000);
    setInterval(loadProcessInfo, 5000);

    // 初始化主题切换功能
    initThemeToggle();
};

// 主题切换功能
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('.theme-icon');

    // 从localStorage读取保存的主题
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        themeIcon.textContent = '☀️';
    }

    // 点击切换主题
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('light-theme');

        if (document.body.classList.contains('light-theme')) {
            themeIcon.textContent = '☀️';
            localStorage.setItem('theme', 'light');
        } else {
            themeIcon.textContent = '🌙';
            localStorage.setItem('theme', 'dark');
        }
    });
}
