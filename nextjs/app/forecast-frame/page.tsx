'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale, // Needed for time series data
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns'; // Ensure date adapter is loaded for TimeScale

// Dynamically import the Chart component
const DynamicChart = dynamic(() => import('react-chartjs-2').then((mod) => mod.Chart), {
  ssr: false,
  loading: () => <p>Loading chart...</p>,
});

// Mock historical data (replace with actual data later)
const mockHistoricalData = [
  { x: new Date(2024, 2, 1).toISOString(), y: 17100 },
  { x: new Date(2024, 2, 2).toISOString(), y: 17200 },
  { x: new Date(2024, 2, 3).toISOString(), y: 17250 },
  { x: new Date(2024, 2, 4).toISOString(), y: 17350 },
  { x: new Date(2024, 2, 5).toISOString(), y: 17300 },
  { x: new Date(2024, 2, 6).toISOString(), y: 17420 },
  { x: new Date(2024, 2, 7).toISOString(), y: 17480 },
];

// Mock forecast data (replace with actual forecast later)
const mockForecastData = [
  // Start from the last historical point for continuity
  { x: new Date(2024, 2, 7).toISOString(), y: 17480 }, 
  { x: new Date(2024, 2, 8).toISOString(), y: 17550 },
  { x: new Date(2024, 2, 9).toISOString(), y: 17600 },
  { x: new Date(2024, 2, 10).toISOString(), y: 17580 },
  { x: new Date(2024, 2, 11).toISOString(), y: 17650 },
  { x: new Date(2024, 2, 12).toISOString(), y: 17700 },
];

export default function ForecastFramePage() {
  const [chartRegistered, setChartRegistered] = useState(false);

  useEffect(() => {
    const registerChart = async () => {
      await import('chartjs-adapter-date-fns'); // Ensure adapter is loaded client-side
      ChartJS.register(
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        Title,
        Tooltip,
        Legend,
        TimeScale,
        Filler
      );
      setChartRegistered(true);
    };
    if (!chartRegistered) {
      registerChart();
    }
  }, [chartRegistered]);

  const chartData = {
    datasets: [
      {
        label: '歷史收盤價',
        data: mockHistoricalData,
        borderColor: 'rgb(59, 130, 246)', // Blue
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.1,
        pointRadius: 2,
      },
      {
        label: '預測收盤價',
        data: mockForecastData,
        borderColor: 'rgb(234, 88, 12)', // Orange
        backgroundColor: 'rgba(234, 88, 12, 0.5)',
        borderDash: [5, 5], // Dashed line for forecast
        tension: 0.1,
        pointRadius: 2,
        fill: false,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '恆生指數收盤價預測 (ARIMA 模型 - 模擬)',
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
          tooltipFormat: 'yyyy-MM-dd',
        },
        adapters: {
          date: { locale: 'zh-HK' } 
        }
      },
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: '指數點位'
        }
      }
    }
  };

  const latestForecast = mockForecastData[mockForecastData.length - 1];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">預測框架 Forecast Frame</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Area */}
        <div className="lg:col-span-2 bg-white p-4 md:p-6 rounded-lg shadow-md h-[500px]">
          {chartRegistered ? (
            <DynamicChart type='line' options={chartOptions} data={chartData} />
          ) : (
            <p>Loading chart...</p>
          )}
        </div>

        {/* Forecast Summary Area */}
        <div className="lg:col-span-1 bg-white p-4 md:p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">模型預測摘要</h2>
          <div className="space-y-3">
            <div>
              <h3 className="text-sm font-medium text-gray-500">預測模型</h3>
              <p className="text-lg font-semibold">ARIMA (自動回歸整合移動平均模型) - 模擬</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">預測期間</h3>
              <p className="text-lg font-semibold">未來 5 個交易日</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">預計 {new Date(latestForecast.x).toLocaleDateString('zh-HK')} 收盤價</h3>
              <p className="text-2xl font-bold text-blue-600">{latestForecast.y.toLocaleString()}</p>
            </div>
             <div>
              <h3 className="text-sm font-medium text-gray-500">信心區間 (95%)</h3>
              <p className="text-lg font-semibold">+/- 150 點 (模擬)</p>
            </div>
          </div>
           <p className="text-xs text-gray-500 mt-6">* 預測結果基於歷史數據和統計模型，僅供參考，不構成任何投資建議。市場存在風險，投資需謹慎。</p>
        </div>
      </div>
    </div>
  );
} 