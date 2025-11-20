'use client';

import { useEffect, useState } from 'react';
import { Package, TrendingUp, TrendingDown, AlertTriangle, RefreshCw, Zap, BarChart3, Map } from 'lucide-react';
import StatCard from '@/components/StatCard';
import { apiGet, API_ENDPOINTS } from '@/lib/api';
import type { DashboardStats, CategoryData, TrendData } from '@/lib/types';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useLanguage } from '@/lib/LanguageContext';
import { getTranslation } from '@/lib/i18n';

const COLORS = ['#ed4c4c', '#faa09a', '#ffd0cd', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899'];

export default function DashboardPage() {
  const { language } = useLanguage();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [categoryData, setCategoryData] = useState<CategoryData[]>([]);
  const [trendData, setTrendData] = useState<TrendData | null>(null);
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
      console.error('Failed to load dashboard data:', error);
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
  const trendChartData = trendData ? trendData.dates.map((date, index) => ({
    date,
    'Stock In': trendData.in_data[index],
    'Stock Out': trendData.out_data[index]
  })) : [];

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
      {stats && (
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
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* 7-Day Trend Chart */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            {getTranslation(language, 'sevenDayTrend')}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
              <XAxis dataKey="date" stroke="#a1a1aa" />
              <YAxis stroke="#a1a1aa" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#27272a', 
                  border: '1px solid #3f3f46',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="Stock In" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981' }}
              />
              <Line 
                type="monotone" 
                dataKey="Stock Out" 
                stroke="#ed4c4c" 
                strokeWidth={2}
                dot={{ fill: '#ed4c4c' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution Pie Chart */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            {getTranslation(language, 'categoryDistribution')}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#27272a', 
                  border: '1px solid #3f3f46',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Delivery Map Placeholder */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Map className="w-5 h-5" />
          {getTranslation(language, 'deliveryTracking')}
        </h2>
        <div className="h-96 bg-black rounded-lg flex items-center justify-center text-gray-500 border border-zinc-800">
          <div className="text-center">
            <Map className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>{getTranslation(language, 'mapIntegrationSoon')}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
