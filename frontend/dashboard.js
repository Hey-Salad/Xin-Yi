/**
 * Xin Yi WMS - Laura-Style Dashboard
 * Real-time inventory, delivery tracking, documents, cameras, and devices
 */

// API Base URL - Auto-detect environment
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:2124/api'
    : 'https://wms.heysalad.app/api';

const MAPBOX_TOKEN = 'YOUR_MAPBOX_TOKEN_HERE'; // TODO: Add your Mapbox token

console.log('🔗 Dashboard API Backend:', API_BASE);

// Global state
let map = null;
let deliveryMarkers = [];
let currentView = 'dashboard';

// ============= INITIALIZATION =============

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMap();
    loadDashboardData();

    // Refresh data every 30 seconds
    setInterval(refreshData, 30000);
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Show corresponding view
            const page = item.dataset.page;
            showView(page);
        });
    });
}

function showView(viewName) {
    currentView = viewName;

    // Hide all views
    const views = document.querySelectorAll('.view-container');
    views.forEach(view => view.style.display = 'none');

    // Show selected view
    const targetView = document.getElementById(`${viewName}-view`);
    if (targetView) {
        targetView.style.display = 'block';
    }

    // Load view-specific data
    switch(viewName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'documents':
            loadDocuments();
            break;
        case 'deliveries':
            loadDeliveries();
            break;
        case 'cameras':
            loadCameras();
            break;
        case 'devices':
            loadDevices();
            break;
        case 'drivers':
            loadDrivers();
            break;
        case 'inventory':
            loadInventory();
            break;
    }
}

// ============= DASHBOARD DATA =============

async function loadDashboardData() {
    try {
        // Load stats
        const stats = await fetch(`${API_BASE}/wms/dashboard/stats`).then(r => r.json());
        updateStats(stats);

        // Load charts
        const categoryData = await fetch(`${API_BASE}/wms/dashboard/category-distribution`).then(r => r.json());
        renderCategoryChart(categoryData);

        const trendData = await fetch(`${API_BASE}/wms/dashboard/weekly-trend`).then(r => r.json());
        renderTrendChart(trendData);

        // Load delivery data for map
        loadDeliveryLocations();

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

function updateStats(stats) {
    document.getElementById('total-stock').textContent = stats.total_stock?.toLocaleString() || '0';
    document.getElementById('today-in').textContent = stats.today_in?.toLocaleString() || '0';
    document.getElementById('today-out').textContent = stats.today_out?.toLocaleString() || '0';
    document.getElementById('low-stock').textContent = stats.low_stock_count?.toLocaleString() || '0';

    // Update change indicators
    const inChange = stats.in_change || 0;
    const outChange = stats.out_change || 0;

    const inChangeEl = document.getElementById('in-change');
    const outChangeEl = document.getElementById('out-change');
    
    if (inChangeEl) {
        inChangeEl.textContent = `${inChange >= 0 ? '↑' : '↓'} ${Math.abs(inChange)}% from yesterday`;
        inChangeEl.className = inChange >= 0 ? 'stat-change positive' : 'stat-change negative';
    }
    
    if (outChangeEl) {
        outChangeEl.textContent = `${outChange >= 0 ? '↑' : '↓'} ${Math.abs(outChange)}% from yesterday`;
        outChangeEl.className = outChange >= 0 ? 'stat-change positive' : 'stat-change negative';
    }
}

function renderCategoryChart(data) {
    const chart = echarts.init(document.getElementById('category-chart'));

    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(24, 24, 27, 0.9)',
            borderColor: '#3f3f46',
            textStyle: { color: '#fff' }
        },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#000',
                borderWidth: 2
            },
            label: {
                show: true,
                color: '#fff',
                formatter: '{b}: {d}%'
            },
            data: data,
            color: ['#ed4c4c', '#faa09a', '#ffd0cd', '#f59e0b', '#10b981']
        }]
    };

    chart.setOption(option);
}

function renderTrendChart(data) {
    const chart = echarts.init(document.getElementById('trend-chart'));

    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(24, 24, 27, 0.9)',
            borderColor: '#3f3f46',
            textStyle: { color: '#fff' }
        },
        legend: {
            data: ['Stock In', 'Stock Out'],
            textStyle: { color: '#a1a1aa' }
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
            axisLine: { lineStyle: { color: '#3f3f46' } },
            axisLabel: { color: '#71717a' }
        },
        yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: '#3f3f46' } },
            axisLabel: { color: '#71717a' },
            splitLine: { lineStyle: { color: '#27272a' } }
        },
        series: [
            {
                name: 'Stock In',
                type: 'line',
                smooth: true,
                data: data.in_data,
                itemStyle: { color: '#10b981' },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0, y: 0, x2: 0, y2: 1,
                        colorStops: [
                            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
                            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
                        ]
                    }
                }
            },
            {
                name: 'Stock Out',
                type: 'line',
                smooth: true,
                data: data.out_data,
                itemStyle: { color: '#ed4c4c' },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0, y: 0, x2: 0, y2: 1,
                        colorStops: [
                            { offset: 0, color: 'rgba(237, 76, 76, 0.3)' },
                            { offset: 1, color: 'rgba(237, 76, 76, 0)' }
                        ]
                    }
                }
            }
        ]
    };

    chart.setOption(option);
}

// ============= MAP INTEGRATION =============

function initMap() {
    if (!MAPBOX_TOKEN || MAPBOX_TOKEN === 'YOUR_MAPBOX_TOKEN_HERE') {
        console.warn('Mapbox token not configured. Map will not load.');
        document.getElementById('map').innerHTML = '<div class="loading">Configure Mapbox token to enable map</div>';
        return;
    }

    mapboxgl.accessToken = MAPBOX_TOKEN;

    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/dark-v11', // Dark theme like Laura
        center: [121.5654, 25.0330], // Taipei, Taiwan (adjust to your location)
        zoom: 12
    });

    map.addControl(new mapboxgl.NavigationControl());
    map.addControl(new mapboxgl.FullscreenControl());
}

async function loadDeliveryLocations() {
    if (!map) return;

    try {
        // This would connect to your delivery API
        // For now, using mock data
        const mockDeliveries = [
            {
                id: 1,
                lat: 25.0330,
                lon: 121.5654,
                driver: 'Wang Li',
                status: 'in_transit',
                eta: '15 min',
                temperature: 4.2
            },
            {
                id: 2,
                lat: 25.0420,
                lon: 121.5754,
                driver: 'Chen Wei',
                status: 'delivered',
                eta: 'Delivered',
                temperature: 3.8
            }
        ];

        // Clear existing markers
        deliveryMarkers.forEach(marker => marker.remove());
        deliveryMarkers = [];

        // Add new markers
        mockDeliveries.forEach(delivery => {
            const el = document.createElement('div');
            el.className = 'delivery-marker';
            el.style.cssText = `
                width: 32px;
                height: 32px;
                background-color: ${delivery.status === 'delivered' ? '#10b981' : '#ed4c4c'};
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                cursor: pointer;
            `;

            const marker = new mapboxgl.Marker(el)
                .setLngLat([delivery.lon, delivery.lat])
                .setPopup(new mapboxgl.Popup({ offset: 25 })
                    .setHTML(`
                        <div style="color: #000; padding: 8px;">
                            <strong>${delivery.driver}</strong><br>
                            Status: <span style="color: ${delivery.status === 'delivered' ? '#10b981' : '#ed4c4c'}">${delivery.status}</span><br>
                            ETA: ${delivery.eta}<br>
                            Temp: ${delivery.temperature}°C
                        </div>
                    `))
                .addTo(map);

            deliveryMarkers.push(marker);
        });

    } catch (error) {
        console.error('Error loading deliveries:', error);
    }
}

// ============= DOCUMENT GENERATION =============

async function generateDoc(docType) {
    const docEndpoints = {
        'po-receipt': 'receiving/po-receipt',
        'receiving-report': 'receiving/receiving-report',
        'putaway-report': 'receiving/putaway-report',
        'inventory-report': 'inventory/inventory-report',
        'stock-status': 'inventory/stock-status',
        'cycle-count': 'inventory/cycle-count',
        'pick-list': 'fulfillment/pick-list',
        'packing-slip': 'fulfillment/packing-slip',
        'shipping-label': 'fulfillment/shipping-label'
    };

    const endpoint = docEndpoints[docType];
    if (!endpoint) {
        showToast('Invalid document type', 'error');
        return;
    }

    try {
        showToast('Generating document...', 'info');

        // For auto-generating documents (inventory/stock-status), use GET
        const method = docType.includes('inventory') || docType.includes('stock') ? 'GET' : 'POST';
        const url = `${API_BASE}/documents/${endpoint}`;

        let options = { method };

        // For POST requests, we'd need to collect data from a form
        // For now, using mock data
        if (method === 'POST') {
            const mockData = getMockDataForDoc(docType);
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(mockData);
        }

        const response = await fetch(url, options);

        if (!response.ok) throw new Error('Document generation failed');

        // Download the PDF
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `${docType}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);

        showToast('Document generated successfully!', 'success');

    } catch (error) {
        console.error('Error generating document:', error);
        showToast('Failed to generate document', 'error');
    }
}

function getMockDataForDoc(docType) {
    // Return mock data based on document type
    const mockData = {
        'pick-list': {
            order_number: 'ORD-' + Date.now(),
            pick_date: new Date().toISOString(),
            items: [
                {
                    sku: 'DEMO-001',
                    name: 'Demo Product',
                    quantity: 10,
                    location: 'A-01-02'
                }
            ]
        },
        'packing-slip': {
            order_number: 'ORD-' + Date.now(),
            packing_date: new Date().toISOString(),
            ship_to: {
                name: 'Demo Customer',
                address_line1: '123 Demo Street',
                city: 'Taipei',
                state: 'Taiwan',
                postal_code: '10000',
                country: 'Taiwan'
            },
            items: [
                {
                    sku: 'DEMO-001',
                    name: 'Demo Product',
                    quantity: 10
                }
            ]
        }
    };

    return mockData[docType] || {};
}

// ============= UTILITIES =============

async function refreshData() {
    showToast('Refreshing data...', 'info');

    switch(currentView) {
        case 'dashboard':
            await loadDashboardData();
            break;
        case 'deliveries':
            await loadDeliveryLocations();
            break;
        default:
            console.log('Refresh for', currentView);
    }

    showToast('Data refreshed', 'success');
}

function showToast(message, type = 'info') {
    // Simple toast notification
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };

    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: ${colors[type]};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showQuickActions() {
    alert('Quick Actions:\n\n1. Generate Inventory Report\n2. Stock In\n3. Stock Out\n4. Generate Pick List\n\nComing soon!');
}

// Stub functions for other views
function loadDocuments() {
    console.log('Loading documents...');
}

function loadDeliveries() {
    console.log('Loading deliveries...');
    loadDeliveryLocations();
}

function loadCameras() {
    console.log('Loading cameras...');
}

function loadDevices() {
    console.log('Loading devices...');
}

function loadDrivers() {
    console.log('Loading drivers...');
}

function loadInventory() {
    console.log('Loading inventory...');
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
