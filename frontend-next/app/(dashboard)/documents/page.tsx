'use client';

import { useState } from 'react';
import { FileText, Download, Package, Truck, CheckCircle } from 'lucide-react';
import { useLanguage } from '@/lib/LanguageContext';
import { getTranslation } from '@/lib/i18n';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2124/api';

export default function DocumentsPage() {
  const { language } = useLanguage();
  const [generating, setGenerating] = useState<string | null>(null);

  const generateDocument = async (type: string, endpoint: string) => {
    setGenerating(type);
    try {
      // Use GET for simpler document generation
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server error:', errorText);
        throw new Error(`Failed to generate document: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error generating document:', error);
      alert(`Failed to generate document: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setGenerating(null);
    }
  };

  const documentCategories = [
    {
      title: getTranslation(language, 'receiving'),
      icon: CheckCircle,
      color: 'from-pink-500 to-red-500',
      documents: [
        { name: getTranslation(language, 'poReceipt'), endpoint: '/documents/receiving/po-receipt', type: 'po-receipt' },
        { name: getTranslation(language, 'receivingReport'), endpoint: '/documents/receiving/receiving-report', type: 'receiving-report' },
        { name: getTranslation(language, 'putawayReport'), endpoint: '/documents/receiving/putaway-report', type: 'putaway-report' },
      ],
    },
    {
      title: language === 'en' ? 'Inventory' : '库存文档',
      icon: Package,
      color: 'from-purple-500 to-indigo-500',
      documents: [
        { name: getTranslation(language, 'inventoryReport'), endpoint: '/documents/inventory/inventory-report', type: 'inventory-report' },
        { name: getTranslation(language, 'stockStatus'), endpoint: '/documents/inventory/stock-status', type: 'stock-status' },
        { name: getTranslation(language, 'cycleCount'), endpoint: '/documents/inventory/cycle-count', type: 'cycle-count' },
      ],
    },
    {
      title: getTranslation(language, 'fulfillment'),
      icon: Truck,
      color: 'from-blue-500 to-cyan-500',
      documents: [
        { name: getTranslation(language, 'pickList'), endpoint: '/documents/fulfillment/pick-list', type: 'pick-list' },
        { name: getTranslation(language, 'packingSlip'), endpoint: '/documents/fulfillment/packing-slip', type: 'packing-slip' },
        { name: getTranslation(language, 'shippingLabel'), endpoint: '/documents/fulfillment/shipping-label', type: 'shipping-label' },
      ],
    },
  ];

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <FileText className="w-8 h-8" />
          {getTranslation(language, 'documentCenter')}
        </h1>
      </div>

      {/* Document Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {documentCategories.map((category, idx) => {
          const Icon = category.icon;
          return (
            <div key={idx} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className={`w-12 h-12 bg-gradient-to-br ${category.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-xl font-semibold">{category.title}</h2>
              </div>

              <div className="space-y-3">
                {category.documents.map((doc) => (
                  <button
                    key={doc.type}
                    onClick={() => generateDocument(doc.type, doc.endpoint)}
                    disabled={generating === doc.type}
                    className="w-full flex items-center justify-between px-4 py-3 bg-black hover:bg-zinc-800 rounded-lg transition-colors border border-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="text-sm font-medium">{doc.name}</span>
                    {generating === doc.type ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-[#ed4c4c]"></div>
                    ) : (
                      <Download className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Info Section */}
      <div className="mt-8 bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-3">
          {language === 'en' ? 'About Document Generation' : '关于文档生成'}
        </h3>
        <p className="text-gray-400 text-sm leading-relaxed mb-3">
          {language === 'en'
            ? 'All documents are generated as professional PDF files with unique document IDs for verification and tracking. Each document includes:'
            : '所有文档均生成为专业PDF文件，带有唯一文档ID用于验证和跟踪。每个文档包含：'}
        </p>
        <ul className="text-gray-400 text-sm space-y-2 ml-4">
          <li className="flex items-start gap-2">
            <span className="text-[#ed4c4c] mt-1">•</span>
            <span>{language === 'en' ? 'Real-time data from your warehouse management system' : '来自您的仓库管理系统的实时数据'}</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-[#ed4c4c] mt-1">•</span>
            <span>{language === 'en' ? 'Unique SHA-256 document hash for verification' : '用于验证的唯一SHA-256文档哈希'}</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-[#ed4c4c] mt-1">•</span>
            <span>{language === 'en' ? 'Company registration details for legal compliance' : '公司注册详情以符合法律要求'}</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-[#ed4c4c] mt-1">•</span>
            <span>{language === 'en' ? 'Professional formatting ready for printing and sharing' : '专业格式，可直接打印和分享'}</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
