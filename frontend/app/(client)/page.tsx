// Client Home Page
'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/app/components/ui/button';

export default function HomePage() {
  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Chat',
      description: 'Intelligent conversations with advanced RAG technology',
      href: '/chat',
      color: 'blue'
    },
    {
      icon: '��',
      title: 'Document Analysis',
      description: 'Upload and analyze documents with AI insights',
      href: '/documents',
      color: 'green'
    },
    {
      icon: '💰',
      title: 'Financial Intelligence',
      description: 'Market analysis and investment recommendations',
      href: '/financial',
      color: 'purple'
    },
    {
      icon: '📊',
      title: 'Smart Analytics',
      description: 'Comprehensive data analysis and reporting',
      href: '/analytics',
      color: 'orange'
    }
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Welcome to <span className="text-blue-600">RAG-ENTERPRISE</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Your intelligent AI platform for document processing, financial analysis, 
          and advanced conversational AI
        </p>
        <div className="flex justify-center gap-4">
          <Link href="/chat">
            <Button size="lg">
              Start Chatting 💬
            </Button>
          </Link>
          <Link href="/documents">
            <Button variant="secondary" size="lg">
              Upload Documents 📄
            </Button>
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature) => (
          <Link
            key={feature.title}
            href={feature.href}
            className="group"
          >
            <div className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-xl transition-all duration-300 h-full">
              <div className={`text-5xl mb-4 transform group-hover:scale-110 transition-transform`}>
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-600">
                {feature.description}
              </p>
            </div>
          </Link>
        ))}
      </div>

      {/* Stats Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold text-blue-600">10K+</div>
            <div className="text-sm text-gray-600 mt-2">Documents Processed</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-green-600">500+</div>
            <div className="text-sm text-gray-600 mt-2">Active Users</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-purple-600">99.9%</div>
            <div className="text-sm text-gray-600 mt-2">Uptime</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-orange-600">24/7</div>
            <div className="text-sm text-gray-600 mt-2">Support</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">Ready to get started?</h2>
            <p className="text-blue-100">Start your AI journey today with RAG-ENTERPRISE</p>
          </div>
          <Link href="/chat">
            <Button size="lg" variant="secondary">
              Launch Chat Now →
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
