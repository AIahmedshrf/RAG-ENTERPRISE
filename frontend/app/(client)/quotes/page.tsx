'use client';

import React, { useState } from 'react';
import Image from 'next/image';

interface Quote {
  text: string;
  author: string;
  category: string;
}

interface QuoteTemplate {
  name: string;
  platform: 'whatsapp' | 'facebook' | 'instagram' | 'twitter';
  width: number;
  height: number;
  icon: string;
}

const platforms: QuoteTemplate[] = [
  { name: 'WhatsApp', platform: 'whatsapp', width: 1080, height: 1920, icon: '💚' },
  { name: 'Facebook', platform: 'facebook', width: 1200, height: 628, icon: '💙' },
  { name: 'Instagram', platform: 'instagram', width: 1080, height: 1080, icon: '📷' },
  { name: 'Twitter (X)', platform: 'twitter', width: 1024, height: 576, icon: '🐦' },
];

const backgroundStyles = [
  { name: 'Gradient Blue', bg: 'bg-gradient-to-br from-blue-600 to-indigo-900' },
  { name: 'Gradient Purple', bg: 'bg-gradient-to-br from-purple-600 to-pink-600' },
  { name: 'Gradient Green', bg: 'bg-gradient-to-br from-green-600 to-teal-600' },
  { name: 'Gradient Dark', bg: 'bg-gradient-to-br from-gray-800 to-black' },
  { name: 'Gradient Sunset', bg: 'bg-gradient-to-br from-orange-500 to-red-600' },
];

const categories = ['Motivation', 'Wisdom', 'Success', 'Life', 'Business', 'Custom'];

export default function QuotesPage() {
  const [selectedPlatform, setSelectedPlatform] = useState<'whatsapp' | 'facebook' | 'instagram' | 'twitter'>('instagram');
  const [quoteText, setQuoteText] = useState('Your success is not final, your failure is not fatal.');
  const [author, setAuthor] = useState('Winston Churchill');
  const [selectedBg, setSelectedBg] = useState(0);
  const [textColor, setTextColor] = useState('white');
  const [fontSize, setFontSize] = useState(48);
  const [category, setCategory] = useState('Motivation');

  const platformConfig = platforms.find(p => p.platform === selectedPlatform)!;

  const handleExport = (format: 'image' | 'svg' | 'copy') => {
    if (format === 'copy') {
      navigator.clipboard.writeText(`"${quoteText}"\n— ${author}`);
      alert('Quote copied to clipboard!');
    } else {
      alert(`Export as ${format} for ${selectedPlatform} (${platformConfig.width}x${platformConfig.height})`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Quote Builder 🎨</h1>
        <p className="text-gray-600 mt-2">Create beautiful, customizable quotes for social media</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Editor */}
        <div className="lg:col-span-2 space-y-6">
          {/* Platform Selection */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Platform</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {platforms.map(platform => (
                <button
                  key={platform.platform}
                  onClick={() => setSelectedPlatform(platform.platform)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedPlatform === platform.platform
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-2">{platform.icon}</div>
                  <div className="font-medium text-sm">{platform.name}</div>
                  <div className="text-xs text-gray-500">{platform.width}x{platform.height}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Quote Text Editor */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quote Text</h2>
            <textarea
              value={quoteText}
              onChange={(e) => setQuoteText(e.target.value)}
              placeholder="Enter your quote..."
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
            />
          </div>

          {/* Author */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Author</h2>
            <input
              type="text"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder="Author name..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Styling Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Background */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Background</h3>
              <div className="space-y-2">
                {backgroundStyles.map((style, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedBg(idx)}
                    className={`w-full p-3 rounded-lg border-2 transition-all text-left font-medium ${
                      selectedBg === idx ? 'border-blue-500' : 'border-gray-200'
                    }`}
                  >
                    <div className={`${style.bg} h-8 rounded mb-2`}></div>
                    {style.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Text Settings */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Font Size</label>
                <input
                  type="range"
                  min="24"
                  max="72"
                  value={fontSize}
                  onChange={(e) => setFontSize(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="text-sm text-gray-600 mt-1">{fontSize}px</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Text Color</label>
                <div className="flex gap-2">
                  {['white', '#FFD700', '#FF6B6B'].map(color => (
                    <button
                      key={color}
                      onClick={() => setTextColor(color)}
                      className={`w-12 h-12 rounded border-2 ${
                        textColor === color ? 'border-blue-500' : 'border-gray-300'
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Export Buttons */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Export</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <button
                onClick={() => handleExport('image')}
                className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                📥 Download PNG
              </button>
              <button
                onClick={() => handleExport('svg')}
                className="px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
              >
                🎨 Export SVG
              </button>
              <button
                onClick={() => handleExport('copy')}
                className="px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
              >
                📋 Copy Text
              </button>
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="lg:col-span-1">
          <div className="sticky top-24 bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Preview</h2>
            <div
              className={`${backgroundStyles[selectedBg].bg} rounded-lg p-8 flex flex-col justify-center items-center text-center min-h-96 overflow-hidden`}
              style={{
                aspectRatio: `${platformConfig.width} / ${platformConfig.height}`,
                maxHeight: '400px',
              }}
            >
              <div
                style={{
                  color: textColor,
                  fontSize: `${Math.min(fontSize, 32)}px`,
                  lineHeight: '1.5',
                }}
                className="font-bold mb-4 px-4"
              >
                "{quoteText}"
              </div>
              <div
                style={{ color: textColor, fontSize: '16px' }}
                className="font-semibold opacity-90"
              >
                — {author}
              </div>
              <div
                style={{ color: textColor }}
                className="text-xs mt-4 opacity-75"
              >
                #{category}
              </div>
            </div>

            {/* Platform Info */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600">
                <strong>Platform:</strong> {selectedPlatform.toUpperCase()} ({platformConfig.width}x{platformConfig.height}px)
              </p>
              <p className="text-xs text-gray-600 mt-2">
                <strong>Word Count:</strong> {quoteText.split(' ').length}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
