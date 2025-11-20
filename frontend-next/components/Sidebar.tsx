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
  Users,
  CheckSquare
} from 'lucide-react';
import LanguageSwitcher from './LanguageSwitcher';
import { useLanguage } from '@/lib/LanguageContext';
import { getTranslation } from '@/lib/i18n';

export default function Sidebar() {
  const pathname = usePathname();
  const { language } = useLanguage();

  const navigation = [
    { name: getTranslation(language, 'dashboard'), href: '/dashboard', icon: LayoutDashboard },
    { name: getTranslation(language, 'inventory'), href: '/inventory', icon: Package },
    { name: getTranslation(language, 'deliveries'), href: '/deliveries', icon: Truck },
    { name: getTranslation(language, 'documents'), href: '/documents', icon: FileText },
    { name: getTranslation(language, 'approvals'), href: '/approvals', icon: CheckSquare },
    { name: getTranslation(language, 'cameras'), href: '/cameras', icon: Camera },
    { name: getTranslation(language, 'devices'), href: '/devices', icon: Wrench },
    { name: getTranslation(language, 'drivers'), href: '/drivers', icon: Users },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-black border-r border-zinc-800 p-6 flex flex-col">
      {/* Logo */}
      <Link href="/" className="mb-8 block">
        <img 
          src="/heysalad_white_logo.svg" 
          alt="HeySalad" 
          className="h-12 w-auto"
        />
      </Link>

      {/* Navigation */}
      <nav className="space-y-1 flex-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-[#ed4c4c] text-white'
                  : 'text-gray-400 hover:bg-zinc-900 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Language Switcher at Bottom */}
      <div className="mt-auto pt-6 border-t border-zinc-800">
        <LanguageSwitcher />
      </div>
    </aside>
  );
}
