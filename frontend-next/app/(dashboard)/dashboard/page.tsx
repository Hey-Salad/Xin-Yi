'use client';

import { useEffect, useState } from 'react';
import { Package, TrendingUp, TrendingDown, AlertTriangle, RefreshCw, Zap } from 'lucide-react';
import StatCard from '@/components/StatCard';
import { apiGet, API_ENDPOINTS } from '@/lib/api';
import type { DashboardStats, CategoryData, TrendData } from '@/lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  async function loadDashboardData() {
    try {
      const data = await apiGet<DashboardStats>(API_ENDPOINTS.dashboardStats);
      setStats(data);
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

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">WMS Command Center</h1>
        <div className="flex gap-3">
          <button
            onClick={loadDashboardData}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#ed4c4c] hover:bg-[#d93d3d] rounded-lg transition-colors">
            <Zap className="w-4 h-4" />
            Quick Actions
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Stock"
            value={stats.total_stock}
            subtitle="units"
            icon={Package}
            gradient="bg-gradient-to-br from-purple-500 to-purple-700"
          />
          <StatCard
            title="Today's Stock In"
            value={stats.today_in}
            change={stats.in_change}
            icon={TrendingUp}
            gradient="bg-gradient-to-br from-pink-500 to-red-500"
          />
          <StatCard
            title="Today's Stock Out"
            value={stats.today_out}
            change={stats.out_change}
            icon={TrendingDown}
            gradient="bg-gradient-to-br from-blue-500 to-cyan-500"
          />
          <StatCard
            title="Low Stock Alerts"
            value={stats.low_stock_count}
            subtitle="items"
            icon={AlertTriangle}
            gradient="bg-gradient-to-br from-orange-500 to-yellow-500"
          />
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="glass rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            7-Day Trend
          </h2>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Chart will be rendered here with Recharts
          </div>
        </div>

        <div className="glass rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Package className="w-5 h-5" />
            Category Distribution
          </h2>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Pie chart will be rendered here
          </div>
        </div>
      </div>

      {/* Delivery Map Placeholder */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Delivery Tracking</h2>
        <div className="h-96 bg-zinc-800 rounded-lg flex items-center justify-center text-gray-500">
          Map integration coming soon
        </div>
      </div>
    </div>
  );
}
