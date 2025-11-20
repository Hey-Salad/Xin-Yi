'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';

const MAPBOX_TOKEN = 'pk.eyJ1IjoiY2hpbHVtYmFwbSIsImEiOiJjbWdraTY1amswdWk3MmlxeXNhaGwyYzNjIn0.-Yv4ZPYvyxqYV_SBV9aJSA';
mapboxgl.accessToken = MAPBOX_TOKEN;

interface Delivery {
  id: string;
  location: [number, number]; // [lng, lat]
  status: 'in-transit' | 'delivered' | 'pending';
  driver: string;
  destination: string;
}

// Dummy delivery data for London area
const DUMMY_DELIVERIES: Delivery[] = [
  {
    id: 'DEL-001',
    location: [-0.1276, 51.5074], // London
    status: 'in-transit',
    driver: 'John Smith',
    destination: 'Shoreditch',
  },
  {
    id: 'DEL-002',
    location: [-0.0759, 51.5155], // Stratford
    status: 'delivered',
    driver: 'Sarah Chen',
    destination: 'Stratford',
  },
  {
    id: 'DEL-003',
    location: [-0.1406, 51.5290], // Camden
    status: 'in-transit',
    driver: 'Mike Johnson',
    destination: 'Camden Town',
  },
  {
    id: 'DEL-004',
    location: [-0.1950, 51.4893], // Chelsea
    status: 'pending',
    driver: 'Emma Wilson',
    destination: 'Chelsea',
  },
  {
    id: 'DEL-005',
    location: [-0.0877, 51.5152], // Hackney
    status: 'in-transit',
    driver: 'David Lee',
    destination: 'Hackney',
  },
];

export default function DeliveryMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [deliveries] = useState<Delivery[]>(DUMMY_DELIVERIES);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    try {
      // Initialize map
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [-0.1276, 51.5074], // London
        zoom: 11,
        attributionControl: false,
      });
    } catch (error) {
      console.error('Error initializing map:', error);
      return;
    }

    const currentMap = map.current;

    // Wait for map to load before adding controls and markers
    currentMap.on('load', () => {
      // Add navigation controls
      currentMap.addControl(new mapboxgl.NavigationControl(), 'top-right');

      // Add markers for deliveries
      deliveries.forEach((delivery) => {
        try {
          const el = document.createElement('div');
          el.className = 'delivery-marker';
          el.style.width = '30px';
          el.style.height = '30px';
          el.style.borderRadius = '50%';
          el.style.cursor = 'pointer';
          el.style.border = '3px solid white';
          el.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
          
          // Color based on status
          if (delivery.status === 'in-transit') {
            el.style.backgroundColor = '#ed4c4c';
          } else if (delivery.status === 'delivered') {
            el.style.backgroundColor = '#10b981';
          } else {
            el.style.backgroundColor = '#f59e0b';
          }

          // Create popup
          const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
            <div style="padding: 8px; color: #000;">
              <h3 style="margin: 0 0 8px 0; font-weight: 600; font-size: 14px;">${delivery.id}</h3>
              <p style="margin: 4px 0; font-size: 12px;"><strong>Driver:</strong> ${delivery.driver}</p>
              <p style="margin: 4px 0; font-size: 12px;"><strong>Destination:</strong> ${delivery.destination}</p>
              <p style="margin: 4px 0; font-size: 12px;">
                <strong>Status:</strong> 
                <span style="
                  display: inline-block;
                  padding: 2px 8px;
                  border-radius: 12px;
                  font-size: 11px;
                  font-weight: 600;
                  background: ${delivery.status === 'in-transit' ? '#fef2f2' : delivery.status === 'delivered' ? '#f0fdf4' : '#fef3c7'};
                  color: ${delivery.status === 'in-transit' ? '#dc2626' : delivery.status === 'delivered' ? '#16a34a' : '#d97706'};
                ">
                  ${delivery.status}
                </span>
              </p>
            </div>
          `);

          // Add marker to map
          new mapboxgl.Marker(el)
            .setLngLat(delivery.location)
            .setPopup(popup)
            .addTo(currentMap);
        } catch (error) {
          console.error('Error adding marker:', error);
        }
      });
    });

    // Cleanup
    return () => {
      currentMap?.remove();
      map.current = null;
    };
  }, [deliveries]);

  return (
    <div className="relative w-full">
      <div ref={mapContainer} className="w-full h-96 rounded-lg" style={{ minHeight: '384px' }} />
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-zinc-900/90 backdrop-blur-sm border border-zinc-800 rounded-lg p-4">
        <h4 className="text-sm font-semibold mb-3">Delivery Status</h4>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#ed4c4c] border-2 border-white"></div>
            <span className="text-xs">In Transit ({deliveries.filter(d => d.status === 'in-transit').length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500 border-2 border-white"></div>
            <span className="text-xs">Delivered ({deliveries.filter(d => d.status === 'delivered').length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500 border-2 border-white"></div>
            <span className="text-xs">Pending ({deliveries.filter(d => d.status === 'pending').length})</span>
          </div>
        </div>
      </div>
    </div>
  );
}
