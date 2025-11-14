'use client';

import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  bgColor?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  onClick?: () => void;
}

export default function StatCard({
  label,
  value,
  icon,
  bgColor = 'bg-blue-50',
  trend,
  onClick,
}: StatCardProps) {
  return (
    <div
      onClick={onClick}
      className={`
        bg-white rounded-lg shadow border border-gray-200 p-6
        transition-all hover:shadow-lg hover:scale-105 cursor-pointer
      `}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium mb-2">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className={`text-xs mt-2 font-semibold ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}% this month
            </p>
          )}
        </div>
        <div className={`${bgColor} rounded-lg p-4 text-2xl`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
