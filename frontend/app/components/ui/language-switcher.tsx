'use client';

import React from 'react';
import { useI18n } from '@/app/i18n/i18n-context';

export const LanguageSwitcher: React.FC = () => {
  const { locale, setLocale } = useI18n();

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => setLocale('en')}
        className={`px-3 py-1 rounded text-sm font-medium ${
          locale === 'en'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        English
      </button>
      <button
        onClick={() => setLocale('ar')}
        className={`px-3 py-1 rounded text-sm font-medium ${
          locale === 'ar'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        العربية
      </button>
    </div>
  );
};
