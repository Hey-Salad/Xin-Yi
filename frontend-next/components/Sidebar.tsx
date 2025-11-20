'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Package, 
  Truck, 
  FileText, 
  Camera, 
  Wrench, 
  Users 
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Inventory', href: '/inventory', icon: Package },
  { name: 'Deliveries', href: '/deliveries', icon: Truck },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Cameras', href: '/cameras', icon: Camera },
  { name: 'Devices', href: '/devices', icon: Wrench },
  { name: 'Drivers', href: '/drivers', icon: Users },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-zinc-900 border-r border-zinc-800 p-6">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 bg-[#ed4c4c] rounded-lg flex items-center justify-center text-white font-bold text-xl">
          馨
        </div>
        <span className="text-xl font-bold text-white">Xin Yi</span>
      </Link>

      {/* Navigation */}
      <nav className="space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-[#ed4c4c] text-white'
                  : 'text-gray-400 hover:bg-zinc-800 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
