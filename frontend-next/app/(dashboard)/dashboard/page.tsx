'use client';

import { useEffect, useState } from 'react';
import { Package, TrendingUp, TrendingDown, AlertTriangle, RefreshCw, Zap, BarChart3, Map } from 'lucide-react';
import StatCard from '@/components/StatCard';
import DeliveryMap from '@/components/DeliveryMap';
import { apiGet, API_ENDPOINTS } from '@/lib/api';
import type { DashboardStats, CategoryData, TrendData } from '@/lib/types';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useLanguage } from '@/lib/LanguageContext';
import { getTranslation } from '@/lib/i18n';

const COLORS = ['#ed4c4c', '#faa09a', '#ffd0cd', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899'];

// Dummy data for fallback
const DUMMY_STATS: DashboardStats = {
  total_stock: 15847,
  today_in: 342,
  today_out: 289,
  low_stock_count: 12,
  material_types: 156,
  in_change: 15.3,
  out_change: -8.2,
};

const DUMMY_CATEGORIES: CategoryData[] = [
  { name: 'Frozen Foods', value: 4250 },
  { name: 'Fresh Produce', value: 3180 },
  { name: 'Dry Goods', value: 2890 },
  { name: 'Beverages', value: 2340 },
  { name: 'Snacks', value: 1987 },
  { name: 'Condiments', value: 1200 },
];

const DUMMY_TREND: TrendData = {
  dates: ['Nov 14', 'Nov 15', 'Nov 16', 'Nov 17', 'Nov 18', 'Nov 19', 'Nov 20'],
  in_data: [320, 385, 412, 298, 445, 367, 342],
  out_data: [245, 312, 289, 356, 298, 334, 289],
};

export default function DashboardPage() {
  const { language } = useLanguage();
  const [stats, setStats] = useState<DashboardStats>(DUMMY_STATS);
  const [categoryData, setCategoryData] = useState<CategoryData[]>(DUMMY_CATEGORIES);
  const [trendData, setTrendData] = useState<TrendData>(DUMMY_TREND);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAllData();
    const interval = setInterval(loadAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadAllData() {
    try {
      const [statsData, categoryResult, trendResult] = await Promise.all([
        apiGet<DashboardStats>(API_ENDPOINTS.dashboardStats),
        apiGet<CategoryData[]>(API_ENDPOINTS.categoryDistribution),
        apiGet<TrendData>(API_ENDPOINTS.weeklyTrend)
      ]);
      
      setStats(statsData);
      setCategoryData(categoryResult);
      setTrendData(trendResult);
    } catch (error) {
      console.error('Failed to load dashboard data, using dummy data:', error);
      // Keep dummy data on error
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#ed4c4c]"></div>
      </div>
    );
  }

  // Transform trend data for recharts
  const trendChartData = trendData.dates.map((date, index) => ({
    date,
    'Stock In': trendData.in_data[index],
    'Stock Out': trendData.out_data[index]
  }));

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">{getTranslation(language, 'wmsCommandCenter')}</h1>
        <div className="flex gap-3">
          <button
            onClick={loadAllData}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-800 rounded-lg transition-colors border border-zinc-800"
          >
            <RefreshCw className="w-4 h-4" />
            {getTranslation(language, 'refresh')}
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#ed4c4c] hover:bg-[#d93d3d] rounded-lg transition-colors">
            <Zap className="w-4 h-4" />
            {getTranslation(language, 'quickActions')}
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title={getTranslation(language, 'totalStock')}
          value={stats.total_stock}
          subtitle={getTranslation(language, 'units')}
          icon={Package}
          gradient="bg-gradient-to-br from-purple-500 to-purple-700"
        />
        <StatCard
          title={getTranslation(language, 'todayStockIn')}
          value={stats.today_in}
          change={stats.in_change}
          icon={TrendingUp}
          gradient="bg-gradient-to-br from-green-500 to-emerald-600"
        />
        <StatCard
          title={getTranslation(language, 'todayStockOut')}
          value={stats.today_out}
          change={stats.out_change}
          icon={TrendingDown}
          gradient="bg-gradient-to-br from-[#ed4c4c] to-[#faa09a]"
        />
        <StatCard
          title={getTranslation(language, 'lowStockAlerts')}
          value={stats.low_stock_count}
          subtitle={getTranslation(language, 'requiresAttention')}
          icon={AlertTriangle}
          gradient="bg-gradient-to-br from-orange-500 to-yellow-500"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* 7-Day Trend Chart */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-[#ed4c4c]" />
            {getTranslation(language, 'sevenDayTrend')}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
              <XAxis 
                dataKey="date" 
                stroke="#a1a1aa"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#a1a1aa"
                style={{ fontSize: '12px' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#18181b', 
                  border: '1px solid #3f3f46',
                  borderRadius: '8px',
                  color: '#ffffff'
                }}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
              />
              <Line 
                type="monotone" 
                dataKey="Stock In" 
                stroke="#10b981" 
                strokeWidth={3}
                dot={{ fill: '#10b981', r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line 
                type="monotone" 
                dataKey="Stock Out" 
                stroke="#ed4c4c" 
                strokeWidth={3}
                dot={{ fill: '#ed4c4c', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution Pie Chart */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-[#ed4c4c]" />
            {getTranslation(language, 'categoryDistribution')}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData as any}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#18181b', 
                  border: '1px solid #3f3f46',
                  borderRadius: '8px',
                  color: '#ffffff'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">
              Material Types
            </h3>
            <Package className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-3xl font-bold">{stats.material_types}</div>
          <p className="text-sm text-gray-400 mt-2">Unique SKUs in system</p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">
              Stock Turnover
            </h3>
            <RefreshCw className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-3xl font-bold">
            {stats.today_out > 0 ? ((stats.today_out / stats.total_stock) * 100).toFixed(1) : '0.0'}%
          </div>
          <p className="text-sm text-gray-400 mt-2">Daily turnover rate</p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">
              Stock Health
            </h3>
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          </div>
          <div className="text-3xl font-bold">
            {stats.low_stock_count === 0 ? '100' : Math.max(0, 100 - (stats.low_stock_count / stats.material_types * 100)).toFixed(0)}%
          </div>
          <p className="text-sm text-gray-400 mt-2">Items at safe levels</p>
        </div>
      </div>

      {/* Bar Chart for Stock Comparison */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-[#ed4c4c]" />
          Stock Movement Comparison
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={trendChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
            <XAxis 
              dataKey="date" 
              stroke="#a1a1aa"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#a1a1aa"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#18181b', 
                border: '1px solid #3f3f46',
                borderRadius: '8px',
                color: '#ffffff'
              }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar dataKey="Stock In" fill="#10b981" radius={[8, 8, 0, 0]} />
            <Bar dataKey="Stock Out" fill="#ed4c4c" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Delivery Map */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Map className="w-5 h-5 text-[#ed4c4c]" />
          {getTranslation(language, 'deliveryTracking')}
        </h2>
        <DeliveryMap />
      </div>
    </div>
  );
}
