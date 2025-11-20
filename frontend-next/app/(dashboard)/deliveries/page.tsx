'use client';

import { useState, useEffect } from 'react';
import { Package, Truck, MapPin, Clock, Search, Filter, ExternalLink } from 'lucide-react';
import DeliveryMap from '@/components/DeliveryMap';
import { useLanguage } from '@/lib/LanguageContext';
import { getTranslation } from '@/lib/i18n';

interface Delivery {
  id: string;
  trackingNumber: string;
  carrier: string;
  status: 'in-transit' | 'delivered' | 'pending' | 'out-for-delivery';
  origin: string;
  destination: string;
  customer: string;
  estimatedDelivery: string;
  actualDelivery?: string;
  location: [number, number]; // [lng, lat]
  items: number;
  weight: string;
}

// UK Shipping Providers
const UK_CARRIERS = [
  'Royal Mail',
  'DPD',
  'Hermes (Evri)',
  'Yodel',
  'DHL',
  'UPS',
  'FedEx',
  'Parcelforce',
  'Amazon Logistics',
  'DX',
];

// Dummy delivery data with UK carriers
const DUMMY_DELIVERIES: Delivery[] = [
  {
    id: 'DEL-001',
    trackingNumber: 'RM123456789GB',
    carrier: 'Royal Mail',
    status: 'in-transit',
    origin: 'London Warehouse',
    destination: 'Shoreditch, London E1 6AN',
    customer: 'Wong\'s Asian Market',
    estimatedDelivery: '2025-11-20 14:00',
    location: [-0.1276, 51.5074],
    items: 24,
    weight: '15.5 kg',
  },
  {
    id: 'DEL-002',
    trackingNumber: 'DPD987654321UK',
    carrier: 'DPD',
    status: 'delivered',
    origin: 'London Warehouse',
    destination: 'Stratford, London E15 2GW',
    customer: 'East London Foods',
    estimatedDelivery: '2025-11-20 10:00',
    actualDelivery: '2025-11-20 09:45',
    location: [-0.0759, 51.5155],
    items: 18,
    weight: '12.3 kg',
  },
  {
    id: 'DEL-003',
    trackingNumber: 'EVRI456789123UK',
    carrier: 'Hermes (Evri)',
    status: 'out-for-delivery',
    origin: 'London Warehouse',
    destination: 'Camden Town, London NW1 8NH',
    customer: 'Camden Asian Grocers',
    estimatedDelivery: '2025-11-20 16:00',
    location: [-0.1406, 51.5290],
    items: 32,
    weight: '21.8 kg',
  },
  {
    id: 'DEL-004',
    trackingNumber: 'YDL789456123UK',
    carrier: 'Yodel',
    status: 'pending',
    origin: 'London Warehouse',
    destination: 'Chelsea, London SW3 5BD',
    customer: 'Chelsea Oriental Store',
    estimatedDelivery: '2025-11-20 18:00',
    location: [-0.1950, 51.4893],
    items: 15,
    weight: '9.2 kg',
  },
  {
    id: 'DEL-005',
    trackingNumber: 'DHL321654987UK',
    carrier: 'DHL',
    status: 'in-transit',
    origin: 'London Warehouse',
    destination: 'Hackney, London E8 1DU',
    customer: 'Hackney Food Hub',
    estimatedDelivery: '2025-11-20 15:30',
    location: [-0.0877, 51.5152],
    items: 28,
    weight: '18.7 kg',
  },
  {
    id: 'DEL-006',
    trackingNumber: 'UPS654987321UK',
    carrier: 'UPS',
    status: 'in-transit',
    origin: 'London Warehouse',
    destination: 'Greenwich, London SE10 9GB',
    customer: 'Greenwich Market Foods',
    estimatedDelivery: '2025-11-20 17:00',
    location: [-0.0077, 51.4826],
    items: 20,
    weight: '14.1 kg',
  },
  {
    id: 'DEL-007',
    trackingNumber: 'FEDEX147258369UK',
    carrier: 'FedEx',
    status: 'delivered',
    origin: 'London Warehouse',
    destination: 'Brixton, London SW9 8PS',
    customer: 'Brixton Village Market',
    estimatedDelivery: '2025-11-20 11:00',
    actualDelivery: '2025-11-20 10:30',
    location: [-0.1149, 51.4613],
    items: 35,
    weight: '23.5 kg',
  },
  {
    id: 'DEL-008',
    trackingNumber: 'PF369258147UK',
    carrier: 'Parcelforce',
    status: 'out-for-delivery',
    origin: 'London Warehouse',
    destination: 'Wimbledon, London SW19 1DD',
    customer: 'Wimbledon Asian Supermarket',
    estimatedDelivery: '2025-11-20 13:00',
    location: [-0.2058, 51.4214],
    items: 22,
    weight: '16.9 kg',
  },
];

export default function DeliveriesPage() {
  const { language } = useLanguage();
  const [deliveries, setDeliveries] = useState<Delivery[]>(DUMMY_DELIVERIES);
  const [filteredDeliveries, setFilteredDeliveries] = useState<Delivery[]>(DUMMY_DELIVERIES);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCarrier, setSelectedCarrier] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    let filtered = deliveries;

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(
        (d) =>
          d.trackingNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.customer.toLowerCase().includes(searchQuery.toLowerCase()) ||
          d.destination.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by carrier
    if (selectedCarrier !== 'all') {
      filtered = filtered.filter((d) => d.carrier === selectedCarrier);
    }

    // Filter by status
    if (selectedStatus !== 'all') {
      filtered = filtered.filter((d) => d.status === selectedStatus);
    }

    setFilteredDeliveries(filtered);
  }, [searchQuery, selectedCarrier, selectedStatus, deliveries]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'delivered':
        return 'bg-green-500/10 text-green-500';
      case 'in-transit':
        return 'bg-[#ed4c4c]/10 text-[#ed4c4c]';
      case 'out-for-delivery':
        return 'bg-blue-500/10 text-blue-500';
      case 'pending':
        return 'bg-yellow-500/10 text-yellow-500';
      default:
        return 'bg-gray-500/10 text-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  const stats = {
    total: deliveries.length,
    inTransit: deliveries.filter((d) => d.status === 'in-transit').length,
    delivered: deliveries.filter((d) => d.status === 'delivered').length,
    pending: deliveries.filter((d) => d.status === 'pending').length,
    outForDelivery: deliveries.filter((d) => d.status === 'out-for-delivery').length,
  };

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">{getTranslation(language, 'deliveryTrackingTitle')}</h1>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-800 rounded-lg transition-colors border border-zinc-800">
            <Package className="w-4 h-4" />
            {getTranslation(language, 'newDelivery')}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <div className="text-2xl font-bold">{stats.total}</div>
          <div className="text-sm text-gray-400">{getTranslation(language, 'totalDeliveries')}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-[#ed4c4c]">{stats.inTransit}</div>
          <div className="text-sm text-gray-400">{getTranslation(language, 'inTransit')}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-blue-500">{stats.outForDelivery}</div>
          <div className="text-sm text-gray-400">{getTranslation(language, 'outForDelivery')}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-green-500">{stats.delivered}</div>
          <div className="text-sm text-gray-400">{getTranslation(language, 'delivered')}</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <div className="text-2xl font-bold text-yellow-500">{stats.pending}</div>
          <div className="text-sm text-gray-400">{getTranslation(language, 'pending')}</div>
        </div>
      </div>

      {/* Map */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-[#ed4c4c]" />
          {getTranslation(language, 'liveDeliveryMap')}
        </h2>
        <DeliveryMap />
      </div>

      {/* Deliveries Table */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold">{getTranslation(language, 'allDeliveries')}</h2>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder={getTranslation(language, 'searchTracking')}
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
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-zinc-800/50 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-400 mb-2">{getTranslation(language, 'carrier')}</label>
                <select
                  value={selectedCarrier}
                  onChange={(e) => setSelectedCarrier(e.target.value)}
                  className="w-full px-4 py-2 bg-zinc-900 border border-zinc-700 rounded-lg focus:outline-none focus:border-[#ed4c4c]"
                >
                  <option value="all">{getTranslation(language, 'allCarriers')}</option>
                  {UK_CARRIERS.map((carrier) => (
                    <option key={carrier} value={carrier}>
                      {carrier}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-400 mb-2">{getTranslation(language, 'status')}</label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="w-full px-4 py-2 bg-zinc-900 border border-zinc-700 rounded-lg focus:outline-none focus:border-[#ed4c4c]"
                >
                  <option value="all">{getTranslation(language, 'allStatuses')}</option>
                  <option value="pending">{getTranslation(language, 'pending')}</option>
                  <option value="in-transit">{getTranslation(language, 'inTransit')}</option>
                  <option value="out-for-delivery">{getTranslation(language, 'outForDelivery')}</option>
                  <option value="delivered">{getTranslation(language, 'delivered')}</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'trackingNumber')}</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'carrier')}</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'customer')}</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'destination')}</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'items')}</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'status')}</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'eta')}</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400">{getTranslation(language, 'actions')}</th>
              </tr>
            </thead>
            <tbody>
              {filteredDeliveries.map((delivery) => (
                <tr
                  key={delivery.id}
                  className="border-b border-zinc-800 hover:bg-zinc-800/50 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div className="font-mono text-sm">{delivery.trackingNumber}</div>
                    <div className="text-xs text-gray-500">{delivery.id}</div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2">
                      <Truck className="w-4 h-4 text-[#ed4c4c]" />
                      <span className="font-medium">{delivery.carrier}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="font-medium">{delivery.customer}</div>
                    <div className="text-xs text-gray-500">{delivery.items} items • {delivery.weight}</div>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-start gap-2">
                      <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                      <div className="text-sm">{delivery.destination}</div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="font-semibold">{delivery.items}</span>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(delivery.status)}`}>
                      {getStatusText(delivery.status)}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <div>
                        {delivery.actualDelivery ? (
                          <div className="text-green-500">
                            {new Date(delivery.actualDelivery).toLocaleString('en-GB', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </div>
                        ) : (
                          <div>
                            {new Date(delivery.estimatedDelivery).toLocaleString('en-GB', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <button className="p-2 hover:bg-zinc-700 rounded-lg transition-colors">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredDeliveries.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            {getTranslation(language, 'noDeliveriesFound')}
          </div>
        )}
      </div>
    </div>
  );
}
