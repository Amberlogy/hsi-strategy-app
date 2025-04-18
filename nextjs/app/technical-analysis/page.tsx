'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic'; // Import dynamic
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement, // For MACD Histogram
  Title,
  Tooltip,
  Legend,
  Filler, // For Bollinger Bands fill
} from 'chart.js';
// import { Line, Bar, Chart } from 'react-chartjs-2'; // Remove static imports

// Register necessary Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// --- Mock Data Definitions ---
const mockLabels = ['2024-03-01', '2024-03-02', '2024-03-03', '2024-03-04', '2024-03-05', '2024-03-06', '2024-03-07'];

const mockBollingerData = {
  labels: mockLabels,
  upper: [17200, 17300, 17450, 17500, 17600, 17550, 17650],
  middle: [17000, 17100, 17200, 17250, 17300, 17350, 17400],
  lower: [16800, 16900, 16950, 17000, 17000, 17150, 17150],
};

const mockMacdData = {
  labels: mockLabels,
  macd: [50, 60, 75, 80, 70, 65, 70],
  signal: [40, 45, 55, 65, 68, 66, 67],
  histogram: [10, 15, 20, 15, 2, -1, 3],
};

const mockRsiData = {
  labels: mockLabels,
  rsi: [60, 65, 72, 75, 68, 65, 67],
};

// --- Data Interfaces (Keep for type safety) ---
interface BollingerData {
  labels: string[];
  upper: number[];
  middle: number[];
  lower: number[];
}

interface MacdData {
  labels: string[];
  macd: number[];
  signal: number[];
  histogram: number[];
}

interface RsiData {
  labels: string[];
  rsi: number[];
}

// --- Helper function for chart options (Unchanged) ---
const getChartOptions = (titleText: string) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: titleText,
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
    }
  },
  scales: {
    x: {
      display: true,
    },
    y: {
      display: true,
    },
  },
});

// --- Chart Card Component (Simplified: remove loading/error props) ---
interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, children }) => (
  <div className="bg-white p-6 rounded-lg shadow-md min-h-[400px] flex flex-col">
    <h2 className="text-xl font-semibold mb-4 text-gray-700">{title}</h2>
    <div className="flex-grow relative">
      {children} {/* Directly render children */}
    </div>
  </div>
);

// Dynamically import the Chart component, disable SSR
const DynamicChart = dynamic(() => import('react-chartjs-2').then(mod => mod.Chart), {
    ssr: false,
    loading: () => <p>正在加載圖表...</p> // Optional loading state
});

// --- Main Page Component ---
export default function TechnicalAnalysisPage() {
  // Initialize state directly with mock data
  const [bollingerData] = useState<BollingerData>(mockBollingerData);
  const [macdData] = useState<MacdData>(mockMacdData);
  const [rsiData] = useState<RsiData>(mockRsiData);
  // Removed isLoading and errors state

  // Removed useEffect hook for fetching data

  // --- Prepare Chart Data (Uses state initialized with mock data) ---
  const bollingerChartData = {
    labels: bollingerData.labels,
    datasets: [
      {
        label: 'Upper Band',
        data: bollingerData.upper,
        borderColor: 'rgba(156, 163, 175, 0.5)', // gray-400
        tension: 0.1,
        pointRadius: 0,
        fill: '+1', // Fill to next dataset (Middle Band)
        backgroundColor: 'rgba(209, 213, 219, 0.2)', // gray-300 with opacity
      },
      {
        label: 'Middle Band (SMA)',
        data: bollingerData.middle,
        borderColor: 'rgb(59, 130, 246)', // blue-500
        tension: 0.1,
        pointRadius: 0,
      },
      {
        label: 'Lower Band',
        data: bollingerData.lower,
        borderColor: 'rgba(156, 163, 175, 0.5)', // gray-400
        tension: 0.1,
        pointRadius: 0,
        fill: '-1', // Fill to previous dataset (Middle Band)
        backgroundColor: 'rgba(209, 213, 219, 0.2)', // gray-300 with opacity
      },
    ],
  };

  const macdChartData = {
    labels: macdData.labels,
    datasets: [
      {
        type: 'line' as const,
        label: 'MACD',
        data: macdData.macd,
        borderColor: 'rgb(34, 197, 94)', // green-500
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'y',
      },
      {
        type: 'line' as const,
        label: 'Signal Line',
        data: macdData.signal,
        borderColor: 'rgb(239, 68, 68)', // red-500
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'y',
      },
      {
        type: 'bar' as const,
        label: 'Histogram',
        data: macdData.histogram,
        backgroundColor: macdData.histogram.map(v => v >= 0 ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'), // Green/Red bars
        borderColor: macdData.histogram.map(v => v >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'),
        borderWidth: 1,
        yAxisID: 'y1', // Use a secondary axis if desired for histogram scale
      },
    ],
  };

   const macdChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index' as const, intersect: false },
    plugins: { legend: { position: 'top' as const }, title: { display: true, text: 'MACD' } },
    scales: {
      x: { display: true },
      y: { type: 'linear' as const, display: true, position: 'left' as const, title: { display: false, text: 'MACD/Signal' } },
      y1: { type: 'linear' as const, display: true, position: 'right' as const, title: { display: false, text: 'Histogram' }, grid: { drawOnChartArea: false } }, // Secondary axis for histogram
    },
  };

  const rsiChartData = {
    labels: rsiData.labels,
    datasets: [
      {
        label: 'RSI',
        data: rsiData.rsi,
        borderColor: 'rgb(168, 85, 247)', // purple-500
        backgroundColor: 'rgba(168, 85, 247, 0.5)',
        tension: 0.1,
        pointRadius: 0,
        // Add overbought/oversold lines if needed
      },
    ],
  };


  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">技術分析 Technical Analysis (模擬數據)</h1> {/* Updated title */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Pass only needed props to ChartCard */}
        <ChartCard title="布林帶 Bollinger Bands">
          <DynamicChart type='line' options={getChartOptions('布林帶 Bollinger Bands')} data={bollingerChartData} />
        </ChartCard>

        <ChartCard title="MACD">
          <DynamicChart type='bar' options={macdChartOptions} data={macdChartData} />
        </ChartCard>

        <ChartCard title="相對強弱指數 RSI">
          <DynamicChart type='line' options={getChartOptions('相對強弱指數 RSI')} data={rsiChartData} />
        </ChartCard>

        {/* Add more indicator cards here as needed */}

      </div>
    </div>
  );
} 