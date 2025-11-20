'use client';

import { useLanguage } from '@/lib/LanguageContext';
import { Languages } from 'lucide-react';

export default function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex items-center gap-2 bg-zinc-900 rounded-lg p-1">
      <button
        onClick={() => setLanguage('en')}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
          language === 'en'
            ? 'bg-[#ed4c4c] text-white'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => setLanguage('zh')}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
          language === 'zh'
            ? 'bg-[#ed4c4c] text-white'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        中文
      </button>
    </div>
  );
}
