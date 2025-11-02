'use client';

import React, { createContext, useContext, useState } from 'react';
import en from './locales/en.json';
import ar from './locales/ar.json';

type Locale = 'en' | 'ar';
type Translations = typeof en;

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

const translations: Record<Locale, Translations> = {
  en,
  ar,
};

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>('en');

  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = translations[locale];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    return value || key;
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      <div dir={locale === 'ar' ? 'rtl' : 'ltr'}>
        {children}
      </div>
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
}
