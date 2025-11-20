'use client';

import { useEffect, useState } from 'react';
import { Search, Package, TrendingUp, TrendingDown, AlertTriangle, Filter, X, Snowflake, Thermometer } from 'lucide-react';
import StatCard from '@/components/StatCard';
import { apiGet, API_ENDPOINTS } from '@/lib/api';
import type { Material, DashboardStats } from '@/lib/types';
import { listProducts, getCategories, getVendors, getProductBySku, type LongdanProduct } from '@/lib/supabase';
import { useLanguage } from '@/lib/LanguageContext';
import { getTranslation } from '@/lib/i18n';

export default function InventoryPage() {
  const { language } = useLanguage();
  const [materials, setMaterials] = useState<Material[]>([]);
  const [filteredMaterials, setFilteredMaterials] = useState<Material[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  
  // Longdan inventory state
  const [longdanProducts, setLongdanProducts] = useState<LongdanProduct[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [vendors, setVendors] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedVendors, setSelectedVendors] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<LongdanProduct | null>(null);
  const [longdanLoading, setLongdanLoading] = useState(false);
  const [longdanError, setLongdanError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    loadLongdanData();
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

  useEffect(() => {
    loadLongdanProducts();
  }, [selectedCategories, selectedVendors, searchQuery]);

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

  async function loadLongdanData() {
    try {
      const [cats, vends] = await Promise.all([
        getCategories(),
        getVendors(),
      ]);
      setCategories(cats);
      setVendors(vends);
    } catch (error) {
      console.error('Failed to load Longdan filters:', error);
    }
  }

  async function loadLongdanProducts() {
    setLongdanLoading(true);
    setLongdanError(null);
    try {
      const products = await listProducts({
        category: selectedCategories.length > 0 ? selectedCategories : undefined,
        vendor: selectedVendors.length > 0 ? selectedVendors : undefined,
        search: searchQuery || undefined,
        limit: 50,
      });
      setLongdanProducts(products);
    } catch (error: any) {
      setLongdanError(error.message || 'Failed to load Longdan products');
      console.error('Failed to load Longdan products:', error);
    } finally {
      setLongdanLoading(false);
    }
  }

  async function openProductDetails(sku: string) {
    try {
      const product = await getProductBySku(sku);
      setSelectedProduct(product);
    } catch (error) {
      console.error('Failed to load product details:', error);
    }
  }

  function toggleCategory(category: string) {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  }

  function toggleVendor(vendor: string) {
    setSelectedVendors((prev) =>
      prev.includes(vendor)
        ? prev.filter((v) => v !== vendor)
        : [...prev, vendor]
    );
  }

  function clearFilters() {
    setSelectedCategories([]);
    setSelectedVendors([]);
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
      <h1 className="text-3xl font-bold mb-8">{getTranslation(language, 'inventoryManagement')}</h1>

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

      {/* Asian Food Catalogue */}
      <div className="glass rounded-xl p-6 mt-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">{getTranslation(language, 'asianFoodCatalogue')}</h2>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder={getTranslation(language, 'searchProducts')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-[#ed4c4c] w-64"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
            >
              <Filter className="w-4 h-4" />
              {getTranslation(language, 'filters')}
              {(selectedCategories.length > 0 || selectedVendors.length > 0) && (
                <span className="bg-[#ed4c4c] text-white text-xs px-2 py-0.5 rounded-full">
                  {selectedCategories.length + selectedVendors.length}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="bg-zinc-800/50 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold">{getTranslation(language, 'filterProducts')}</h3>
              {(selectedCategories.length > 0 || selectedVendors.length > 0) && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-[#ed4c4c] hover:underline"
                >
                  {getTranslation(language, 'clearAll')}
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Category Filter */}
              <div>
                <h4 className="text-sm font-semibold text-gray-400 mb-2">{getTranslation(language, 'categories')}</h4>
                <div className="max-h-48 overflow-y-auto space-y-2">
                  {categories.map((category) => (
                    <label key={category} className="flex items-center gap-2 cursor-pointer hover:bg-zinc-700/50 p-2 rounded">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(category)}
                        onChange={() => toggleCategory(category)}
                        className="w-4 h-4 rounded border-zinc-600 text-[#ed4c4c] focus:ring-[#ed4c4c]"
                      />
                      <span className="text-sm">{category}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Vendor Filter */}
              <div>
                <h4 className="text-sm font-semibold text-gray-400 mb-2">{getTranslation(language, 'vendors')}</h4>
                <div className="max-h-48 overflow-y-auto space-y-2">
                  {vendors.map((vendor) => (
                    <label key={vendor} className="flex items-center gap-2 cursor-pointer hover:bg-zinc-700/50 p-2 rounded">
                      <input
                        type="checkbox"
                        checked={selectedVendors.includes(vendor)}
                        onChange={() => toggleVendor(vendor)}
                        className="w-4 h-4 rounded border-zinc-600 text-[#ed4c4c] focus:ring-[#ed4c4c]"
                      />
                      <span className="text-sm">{vendor}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {longdanLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#ed4c4c]"></div>
          </div>
        )}

        {/* Error State */}
        {longdanError && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
            <p className="text-red-500">{longdanError}</p>
          </div>
        )}

        {/* Product Grid */}
        {!longdanLoading && !longdanError && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {longdanProducts.map((product) => (
              <div
                key={product.sku}
                onClick={() => openProductDetails(product.sku)}
                className="bg-zinc-800/50 rounded-lg p-4 hover:bg-zinc-800 cursor-pointer transition-all hover:scale-105"
              >
                {/* Product Image */}
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-40 object-cover rounded-lg mb-3"
                  />
                ) : (
                  <div className="w-full h-40 bg-zinc-700 rounded-lg mb-3 flex items-center justify-center">
                    <Package className="w-12 h-12 text-zinc-500" />
                  </div>
                )}

                {/* Product Info */}
                <h3 className="font-semibold text-sm mb-2 line-clamp-2">{product.name}</h3>
                <p className="text-xs text-gray-400 mb-2">{product.sku}</p>
                <p className="text-lg font-bold text-[#ed4c4c] mb-3">
                  £{product.price.toFixed(2)}
                </p>

                {/* Badges */}
                <div className="flex flex-wrap gap-2">
                  {product.temperature_zone && (
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-500/10 text-blue-400 text-xs rounded">
                      {product.temperature_zone === 'frozen' ? (
                        <Snowflake className="w-3 h-3" />
                      ) : (
                        <Thermometer className="w-3 h-3" />
                      )}
                      {product.temperature_zone}
                    </span>
                  )}
                  {product.is_wholesale && (
                    <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs rounded">
                      Wholesale
                    </span>
                  )}
                  {product.is_ambient && (
                    <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded">
                      Ambient
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {!longdanLoading && !longdanError && longdanProducts.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            {getTranslation(language, 'noProductsFound')}
          </div>
        )}
      </div>

      {/* Product Details Drawer */}
      {selectedProduct && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedProduct(null)}
        >
          <div
            className="bg-zinc-900 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold">{selectedProduct.name}</h2>
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {selectedProduct.image_url && (
                <img
                  src={selectedProduct.image_url}
                  alt={selectedProduct.name}
                  className="w-full h-64 object-cover rounded-lg mb-6"
                />
              )}

              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-400">SKU</p>
                  <p className="font-mono">{selectedProduct.sku}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-400">Price</p>
                  <p className="text-2xl font-bold text-[#ed4c4c]">
                    £{selectedProduct.price.toFixed(2)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-400">Category</p>
                  <p>{selectedProduct.canonical_category}</p>
                </div>

                {selectedProduct.vendor && (
                  <div>
                    <p className="text-sm text-gray-400">Vendor</p>
                    <p>{selectedProduct.vendor}</p>
                  </div>
                )}

                {selectedProduct.temperature_zone && (
                  <div>
                    <p className="text-sm text-gray-400">Temperature Zone</p>
                    <p className="capitalize">{selectedProduct.temperature_zone}</p>
                  </div>
                )}

                {selectedProduct.unit && (
                  <div>
                    <p className="text-sm text-gray-400">Unit</p>
                    <p>{selectedProduct.unit}</p>
                  </div>
                )}

                {selectedProduct.description && (
                  <div>
                    <p className="text-sm text-gray-400">Description</p>
                    <p className="text-sm">{selectedProduct.description}</p>
                  </div>
                )}

                <div className="flex flex-wrap gap-2 pt-4">
                  {selectedProduct.is_wholesale && (
                    <span className="px-3 py-1 bg-purple-500/10 text-purple-400 text-sm rounded-full">
                      Wholesale
                    </span>
                  )}
                  {selectedProduct.is_ambient && (
                    <span className="px-3 py-1 bg-green-500/10 text-green-400 text-sm rounded-full">
                      Ambient
                    </span>
                  )}
                  {selectedProduct.is_frozen && (
                    <span className="px-3 py-1 bg-blue-500/10 text-blue-400 text-sm rounded-full">
                      Frozen
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
