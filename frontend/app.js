// API Base URL | API 基础 URL
// For production: https://api.heysalad.app/api/wms
// For local dev: http://localhost:2124/api/wms
// For RPi: http://YOUR_RPI_IP:2124/api/wms
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:2124/api/wms'
    : `http://${window.location.hostname}:2124/api/wms`;

// 初始化图表 | Initialize charts
let trendChart, categoryChart, topStockChart;

// 全局变量 | Global variables
let allMaterials = []; // 存储所有物料数据 | Store all materials data
let updateInterval = null; // 自动更新定时器 | Auto-update timer
let countdownInterval = null; // 倒计时定时器 | Countdown timer
let countdownSeconds = 3; // 倒计时秒数 | Countdown seconds

// 页面加载完成后初始化 | Initialize after page load
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadAllData();
    initSearchFilter();
    startAutoUpdate();
});

// 初始化图表 | Initialize charts
function initCharts() {
    trendChart = echarts.init(document.getElementById('trend-chart'));
    categoryChart = echarts.init(document.getElementById('category-chart'));
    topStockChart = echarts.init(document.getElementById('top-stock-chart'));

    // 响应式 | Responsive
    window.addEventListener('resize', function() {
        trendChart.resize();
        categoryChart.resize();
        topStockChart.resize();
    });
}

// 加载所有数据 | Load all data
async function loadAllData() {
    try {
        await Promise.all([
            loadDashboardStats(),
            loadCategoryDistribution(),
            loadWeeklyTrend(),
            loadTopStock(),
            loadAllMaterials()
        ]);
    } catch (error) {
        console.error('加载数据失败:', error);  // Failed to load data
        alert('加载数据失败，请检查后端服务是否启动');  // Failed to load data, please check if backend service is running
    }
}

// 刷新数据 | Refresh data
function refreshData() {
    loadAllData();
    resetCountdown();
}

// 初始化搜索过滤 | Initialize search filter
function initSearchFilter() {
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function(e) {
        const keyword = e.target.value.toLowerCase().trim();
        filterMaterials(keyword);
    });
}

// 过滤物料 | Filter materials
function filterMaterials(keyword) {
    if (!keyword) {
        renderInventoryTable(allMaterials);
        return;
    }

    const filtered = allMaterials.filter(item =>
        item.name.toLowerCase().includes(keyword) ||
        item.sku.toLowerCase().includes(keyword)
    );
    renderInventoryTable(filtered);
}

// 启动自动更新 | Start auto-update
function startAutoUpdate() {
    // 清除旧的定时器 | Clear old timers
    if (updateInterval) clearInterval(updateInterval);
    if (countdownInterval) clearInterval(countdownInterval);

    // 倒计时 | Countdown
    countdownInterval = setInterval(function() {
        countdownSeconds--;
        document.getElementById('countdown').textContent = countdownSeconds;

        if (countdownSeconds <= 0) {
            // 更新所有数据 | Update all data
            loadAllData();
            countdownSeconds = 3;
        }
    }, 1000);
}

// 重置倒计时 | Reset countdown
function resetCountdown() {
    countdownSeconds = 3;
    document.getElementById('countdown').textContent = countdownSeconds;
}

// 加载统计数据 | Load dashboard statistics
async function loadDashboardStats() {
    const response = await fetch(`${API_BASE_URL}/dashboard/stats`);
    const data = await response.json();

    document.getElementById('total-stock').textContent = data.total_stock.toLocaleString();
    document.getElementById('today-in').textContent = data.today_in.toLocaleString();
    document.getElementById('today-out').textContent = data.today_out.toLocaleString();
    document.getElementById('low-stock-count').textContent = data.low_stock_count;

    // 更新变化百分比 | Update percentage change
    const inChange = document.getElementById('in-change');
    inChange.textContent = (data.in_change >= 0 ? '+' : '') + data.in_change + '%';
    inChange.className = data.in_change >= 0 ? 'stat-change positive' : 'stat-change negative';

    const outChange = document.getElementById('out-change');
    outChange.textContent = (data.out_change >= 0 ? '+' : '') + data.out_change + '%';
    outChange.className = data.out_change >= 0 ? 'stat-change positive' : 'stat-change negative';
}

// 加载类型分布 | Load category distribution
async function loadCategoryDistribution() {
    const response = await fetch(`${API_BASE_URL}/dashboard/category-distribution`);
    const data = await response.json();

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            right: 10,
            top: 'center',
            textStyle: {
                fontSize: 12
            }
        },
        series: [
            {
                name: '库存分布',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 14,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: data,
                color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
            }
        ]
    };

    categoryChart.setOption(option);
}

// 加载近7天趋势 | Load 7-day trend
async function loadWeeklyTrend() {
    const response = await fetch(`${API_BASE_URL}/dashboard/weekly-trend`);
    const data = await response.json();

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data: ['入库', '出库'],
            textStyle: {
                fontSize: 12
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: data.dates,
            axisLine: {
                lineStyle: {
                    color: '#ccc'
                }
            },
            axisLabel: {
                color: '#666'
            }
        },
        yAxis: {
            type: 'value',
            axisLine: {
                lineStyle: {
                    color: '#ccc'
                }
            },
            axisLabel: {
                color: '#666'
            },
            splitLine: {
                lineStyle: {
                    color: '#eee'
                }
            }
        },
        series: [
            {
                name: '入库',
                type: 'line',
                smooth: true,
                data: data.in_data,
                itemStyle: {
                    color: '#5470c6'
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0,
                                color: 'rgba(84, 112, 198, 0.3)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(84, 112, 198, 0.05)'
                            }
                        ]
                    }
                }
            },
            {
                name: '出库',
                type: 'line',
                smooth: true,
                data: data.out_data,
                itemStyle: {
                    color: '#ee6666'
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0,
                                color: 'rgba(238, 102, 102, 0.3)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(238, 102, 102, 0.05)'
                            }
                        ]
                    }
                }
            }
        ]
    };

    trendChart.setOption(option);
}

// 加载库存TOP10 | Load top 10 stock
async function loadTopStock() {
    const response = await fetch(`${API_BASE_URL}/dashboard/top-stock`);
    const data = await response.json();

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            },
            formatter: function(params) {
                const index = params[0].dataIndex;
                return `${data.names[index]}<br/>类型: ${data.categories[index]}<br/>库存: ${params[0].value}`;
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            axisLine: {
                lineStyle: {
                    color: '#ccc'
                }
            },
            axisLabel: {
                color: '#666'
            },
            splitLine: {
                lineStyle: {
                    color: '#eee'
                }
            }
        },
        yAxis: {
            type: 'category',
            data: data.names.map(name => name.length > 12 ? name.substring(0, 12) + '...' : name),
            axisLine: {
                lineStyle: {
                    color: '#ccc'
                }
            },
            axisLabel: {
                color: '#666'
            }
        },
        series: [
            {
                type: 'bar',
                data: data.quantities,
                itemStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 1,
                        y2: 0,
                        colorStops: [
                            {
                                offset: 0,
                                color: '#667eea'
                            },
                            {
                                offset: 1,
                                color: '#764ba2'
                            }
                        ]
                    },
                    borderRadius: [0, 4, 4, 0]
                },
                barWidth: '60%'
            }
        ]
    };

    topStockChart.setOption(option);
}

// 加载所有物料 | Load all materials
async function loadAllMaterials() {
    const response = await fetch(`${API_BASE_URL}/materials/all`);
    const data = await response.json();

    allMaterials = data;

    // 应用当前搜索条件 | Apply current search criteria
    const searchInput = document.getElementById('search-input');
    const keyword = searchInput ? searchInput.value.toLowerCase().trim() : '';

    if (keyword) {
        filterMaterials(keyword);
    } else {
        renderInventoryTable(data);
    }
}

// 渲染库存表格 | Render inventory table
function renderInventoryTable(data) {
    const tbody = document.getElementById('inventory-tbody');
    tbody.innerHTML = '';

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">暂无数据</td></tr>';  // No data
        return;
    }

    data.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = 'clickable';

        let statusBadge = '';
        if (item.status === 'normal') {
            statusBadge = `<span class="status-badge status-normal">${item.status_text}</span>`;
        } else if (item.status === 'warning') {
            statusBadge = `<span class="status-badge status-warning">${item.status_text}</span>`;
        } else {
            statusBadge = `<span class="status-badge status-danger">${item.status_text}</span>`;
        }

        tr.innerHTML = `
            <td>${item.name}</td>
            <td>${item.sku}</td>
            <td>${item.category}</td>
            <td><strong>${item.quantity}</strong></td>
            <td>${item.unit}</td>
            <td>${item.safe_stock}</td>
            <td>${statusBadge}</td>
            <td>${item.location}</td>
        `;

        // 添加点击事件，跳转到产品详情页 | Add click event to navigate to product detail page
        tr.addEventListener('click', function() {
            window.location.href = `product_detail.html?product=${encodeURIComponent(item.name)}`;
        });

        tbody.appendChild(tr);
    });
}
