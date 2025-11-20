import Link from 'next/link';
import { LayoutDashboard, Clock, Package, MessageSquare, FileText, Users, Github } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: LayoutDashboard,
      title: 'Real-Time Dashboard',
      description: 'Live inventory statistics, 7-day trend analysis, and interactive charts with auto-refresh every 30 seconds.',
    },
    {
      icon: Clock,
      title: 'FEFO Intelligence',
      description: 'First Expired First Out logic with lot-based tracking, expiration alerts, and spoilage monitoring.',
    },
    {
      icon: Package,
      title: 'Product Management',
      description: 'Detailed product views with images, transaction history, and real-time stock levels.',
    },
    {
      icon: MessageSquare,
      title: 'AI Integration',
      description: 'Multi-provider AI chat, natural language queries, and recipe suggestions for expiring ingredients.',
    },
    {
      icon: FileText,
      title: 'Document Generation',
      description: 'Generate PO receipts, pick lists, packing slips, and inventory reports with one click.',
    },
    {
      icon: Users,
      title: 'Multi-Language Support',
      description: 'Full bilingual support (English | 中文) throughout the interface and documentation.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-zinc-900">
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Logo Section */}
        <div className="text-center mb-16 animate-fade-in-down">
          <div className="flex items-center justify-center mb-8">
            <img 
              src="/heysalad_white_logo.svg" 
              alt="HeySalad" 
              className="h-20 w-auto"
            />
          </div>
          <h1 className="text-5xl font-bold mb-3">Xin Yi WMS</h1>
          <p className="text-xl text-gray-400">Intelligent Food Warehouse Management</p>
        </div>

        {/* Hero Section */}
        <div className="text-center mb-20 animate-fade-in-up">
          <h2 className="text-6xl font-bold mb-6 bg-gradient-to-r from-[#ed4c4c] to-[#faa09a] bg-clip-text text-transparent">
            AI-Powered Fresh Food Logistics
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12 leading-relaxed">
            Comprehensive warehouse management platform built for HeySalad's fresh food operations, 
            featuring real-time inventory tracking, FEFO intelligence, and AI-driven insights.
          </p>
          
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-3 px-8 py-4 bg-[#ed4c4c] text-white rounded-xl font-semibold hover:bg-[#d93d3d] transition-all hover:-translate-y-1 shadow-lg shadow-[#ed4c4c]/30"
            >
              <LayoutDashboard className="w-5 h-5" />
              Open Dashboard
            </Link>
            <a
              href="https://github.com/Hey-Salad/Xin-Yi"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 px-8 py-4 bg-white/10 text-white rounded-xl font-semibold hover:bg-white/15 transition-all hover:-translate-y-1 backdrop-blur-sm border border-white/20"
            >
              <Github className="w-5 h-5" />
              View on GitHub
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="glass rounded-2xl p-8 hover:-translate-y-2 transition-all hover:border-[#ed4c4c] group"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="w-16 h-16 bg-gradient-to-br from-[#ed4c4c] to-[#faa09a] rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <Icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
