'use client';

import React from 'react';

interface FilterOption {
  label: string;
  value: string;
}

interface FilterBarProps {
  filters: {
    [key: string]: {
      label: string;
      type: 'select' | 'search' | 'date';
      options?: FilterOption[];
      placeholder?: string;
    };
  };
  onFilterChange: (filters: { [key: string]: string }) => void;
  onReset?: () => void;
}

export default function FilterBar({ filters, onFilterChange, onReset }: FilterBarProps) {
  const [filterValues, setFilterValues] = React.useState<{ [key: string]: string }>({});

  const handleChange = (key: string, value: string) => {
    const newFilters = { ...filterValues, [key]: value };
    setFilterValues(newFilters);
    onFilterChange(newFilters);
  };

  const handleReset = () => {
    setFilterValues({});
    onReset?.();
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Filters</h3>
        {Object.keys(filterValues).some(k => filterValues[k]) && (
          <button
            onClick={handleReset}
            className="text-xs text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(filters).map(([key, filter]) => (
          <div key={key}>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              {filter.label}
            </label>
            {filter.type === 'select' && (
              <select
                value={filterValues[key] || ''}
                onChange={(e) => handleChange(key, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All</option>
                {filter.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            )}
            {filter.type === 'search' && (
              <input
                type="text"
                placeholder={filter.placeholder || 'Search...'}
                value={filterValues[key] || ''}
                onChange={(e) => handleChange(key, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
            {filter.type === 'date' && (
              <input
                type="date"
                value={filterValues[key] || ''}
                onChange={(e) => handleChange(key, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
