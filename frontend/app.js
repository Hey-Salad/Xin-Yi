// API Base URL | API 基础 URL
// Production: https://wms.heysalad.app/api/wms
// Local dev: http://localhost:2124/api/wms

// API Base URL - Auto-detect environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:2124/api/wms'
    : 'https://wms.heysalad.app/api/wms';

console.log('🔗 API Backend:', API_BASE_URL);

// Fetch with timeout helper
async function fetchWithTimeout(url, timeout = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error(`Request timeout after ${timeout}ms`);
        }
        throw error;
    }
}

// 初始化图表 | Initialize charts
let trendChart, categoryChart, topStockChart;

// 全局变量 | Global variables
let allMaterials = []; // 存储所有物料数据 | Store all materials data
let updateInterval = null; // 自动更新定时器 | Auto-update timer
let countdownInterval = null; // 倒计时定时器 | Countdown timer
let countdownSeconds = 30; // 倒计时秒数 | Countdown seconds (30s to reduce flashing)

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
    console.log('🔄 Loading data from:', API_BASE_URL);
    const startTime = Date.now();
    
    // Use Promise.allSettled instead of Promise.all to handle partial failures
    const results = await Promise.allSettled([
        loadDashboardStats(),
        loadCategoryDistribution(),
        loadWeeklyTrend(),
        loadTopStock(),
        loadAllMaterials()
    ]);
    
    const loadTime = Date.now() - startTime;
    console.log(`✅ Data loaded in ${loadTime}ms`);
    
    // Check if any failed
    const failures = results.filter(r => r.status === 'rejected');
    if (failures.length > 0) {
        console.warn(`⚠️ ${failures.length} API calls failed:`, failures.map(f => f.reason));
        
        // Only show alert if ALL failed
        if (failures.length === results.length) {
            alert('Failed to load data. Please check if backend service is running.\n加载数据失败，请检查后端服务是否启动。');
        }
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
            countdownSeconds = 30;
        }
    }, 1000);
}

// 重置倒计时 | Reset countdown
function resetCountdown() {
    countdownSeconds = 30;
    document.getElementById('countdown').textContent = countdownSeconds;
}

// 加载统计数据 | Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/dashboard/stats`, 10000);
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
    } catch (error) {
        console.error('Failed to load dashboard stats:', error);
        throw error;
    }
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
                color: ['#ed4c4c', '#faa09a', '#ffd0cd', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899']
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
            data: ['Stock-In | 入库', 'Stock-Out | 出库'],
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
                name: 'Stock-In | 入库',
                type: 'line',
                smooth: true,
                data: data.in_data,
                itemStyle: {
                    color: '#10b981'
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
                                color: 'rgba(16, 185, 129, 0.3)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(16, 185, 129, 0.05)'
                            }
                        ]
                    }
                }
            },
            {
                name: 'Stock-Out | 出库',
                type: 'line',
                smooth: true,
                data: data.out_data,
                itemStyle: {
                    color: '#ed4c4c'
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
                                color: 'rgba(237, 76, 76, 0.3)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(237, 76, 76, 0.05)'
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
                return `${data.names[index]}<br/>Type | 类型: ${data.categories[index]}<br/>Stock | 库存: ${params[0].value}`;
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
                                color: '#ed4c4c'
                            },
                            {
                                offset: 1,
                                color: '#faa09a'
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
function getInitialLetter(text) {
    if (!text) return '?';
    return text.trim().charAt(0).toUpperCase();
}

function createTextCell(content, className) {
    const td = document.createElement('td');
    if (className) td.classList.add(className);
    td.textContent = content;
    return td;
}

function renderInventoryTable(data) {
    const tbody = document.getElementById('inventory-tbody');
    tbody.innerHTML = '';

    if (!data.length) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = 7;
        emptyCell.style.textAlign = 'center';
        emptyCell.style.color = '#999';
        emptyCell.textContent = 'No data available | 暂无数据';
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
        return;
    }

    data.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = 'clickable';

        // Product cell with thumbnail
        const productTd = document.createElement('td');
        productTd.className = 'product-cell';

        const infoWrapper = document.createElement('div');
        infoWrapper.className = 'material-info';

        const thumbWrapper = document.createElement('div');
        thumbWrapper.className = 'material-thumb';

        const imageUrl = item.storage_image_url || item.image_url;

        if (imageUrl) {
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = item.name;
            img.loading = 'lazy';
            img.onerror = () => {
                thumbWrapper.classList.add('placeholder');
                thumbWrapper.textContent = getInitialLetter(item.name);
                img.remove();
            };
            thumbWrapper.appendChild(img);
        } else {
            thumbWrapper.classList.add('placeholder');
            thumbWrapper.textContent = getInitialLetter(item.name);
        }

        const metaWrapper = document.createElement('div');
        metaWrapper.className = 'material-meta';

        const nameEl = document.createElement('div');
        nameEl.className = 'material-name';
        nameEl.textContent = item.name;

        const skuEl = document.createElement('div');
        skuEl.className = 'material-sku';
        skuEl.textContent = item.sku;

        metaWrapper.appendChild(nameEl);
        metaWrapper.appendChild(skuEl);

        infoWrapper.appendChild(thumbWrapper);
        infoWrapper.appendChild(metaWrapper);
        productTd.appendChild(infoWrapper);

        tr.appendChild(productTd);
        tr.appendChild(createTextCell(item.category || '-'));
        tr.appendChild(createTextCell((item.quantity ?? 0).toLocaleString(), 'numeric-cell'));
        tr.appendChild(createTextCell(item.unit || '-'));
        tr.appendChild(createTextCell((item.safe_stock ?? 0).toLocaleString(), 'numeric-cell'));

        const statusCell = document.createElement('td');
        const badge = document.createElement('span');
        badge.className = `status-badge status-${item.status}`;
        badge.textContent = item.status_text;
        statusCell.appendChild(badge);
        tr.appendChild(statusCell);

        tr.appendChild(createTextCell(item.location || '-'));

        tr.addEventListener('click', () => {
            if (imageUrl) {
                sessionStorage.setItem('material_image_url', imageUrl);
                sessionStorage.setItem('material_image_source', item.image_source_url || '');
            }
            sessionStorage.setItem('material_sku', item.sku);
            window.location.href = `product_detail.html?product=${encodeURIComponent(item.name)}`;
        });

        tbody.appendChild(tr);
    });
}
