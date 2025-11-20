'use client';

import Sidebar from '@/components/Sidebar';
import { LanguageProvider } from '@/lib/LanguageContext';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <LanguageProvider>
      <div className="flex min-h-screen bg-black">
        <Sidebar />
        <main className="flex-1 ml-60 p-8 bg-zinc-950">
          {children}
        </main>
      </div>
    </LanguageProvider>
  );
}
