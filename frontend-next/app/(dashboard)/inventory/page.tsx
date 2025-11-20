'use client';

import { useEffect, useState } from 'react';
import { Search, Package, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import StatCard from '@/components/StatCard';
import { apiGet, API_ENDPOINTS } from '@/lib/api';
import type { Material, DashboardStats } from '@/lib/types';

export default function InventoryPage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [filteredMaterials, setFilteredMaterials] = useState<Material[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = materials.filter(
        (m) =>
          m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          m.sku.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredMaterials(filtered);
    } else {
      setFilteredMaterials(materials);
    }
  }, [searchQuery, materials]);

  async function loadData() {
    try {
      const [materialsData, statsData] = await Promise.all([
        apiGet<Material[]>(API_ENDPOINTS.allMaterials),
        apiGet<DashboardStats>(API_ENDPOINTS.dashboardStats),
      ]);
      setMaterials(materialsData);
      setFilteredMaterials(materialsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load inventory:', error);
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
      <h1 className="text-3xl font-bold mb-8">Inventory Management</h1>

      {/* Stats */}
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

      {/* Search and Table */}
      <div className="glass rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Inventory List</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-[#ed4c4c] w-64"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Product</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Category</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Stock</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Unit</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Safe Stock</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Location</th>
              </tr>
            </thead>
            <tbody>
              {filteredMaterials.map((material) => (
                <tr
                  key={material.id}
                  className="border-b border-zinc-800 hover:bg-zinc-800/50 cursor-pointer transition-colors"
                  onClick={() => window.location.href = `/product/${encodeURIComponent(material.name)}`}
                >
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-3">
                      {material.storage_image_url || material.image_url ? (
                        <img
                          src={material.storage_image_url || material.image_url}
                          alt={material.name}
                          className="w-10 h-10 rounded-lg object-cover"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-zinc-700 flex items-center justify-center text-sm font-semibold">
                          {material.name.charAt(0).toUpperCase()}
                        </div>
                      )}
                      <div>
                        <div className="font-medium">{material.name}</div>
                        <div className="text-xs text-gray-500">{material.sku}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-gray-400">{material.category}</td>
                  <td className="py-4 px-4 text-right font-semibold">{material.quantity.toLocaleString()}</td>
                  <td className="py-4 px-4 text-gray-400">{material.unit}</td>
                  <td className="py-4 px-4 text-right text-gray-400">{material.safe_stock.toLocaleString()}</td>
                  <td className="py-4 px-4 text-center">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                        material.status === 'normal'
                          ? 'bg-green-500/10 text-green-500'
                          : material.status === 'warning'
                          ? 'bg-yellow-500/10 text-yellow-500'
                          : 'bg-red-500/10 text-red-500'
                      }`}
                    >
                      {material.status_text}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-gray-400">{material.location}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
