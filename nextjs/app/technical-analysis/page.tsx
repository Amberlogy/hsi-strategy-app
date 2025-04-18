'use client';

import { useState, useEffect } from 'react';
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
import { Line, Bar, Chart } from 'react-chartjs-2';

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

// --- Data Interfaces (Assumed API responses) ---
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

// --- Helper function for chart options ---
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

// --- Chart Card Component ---
interface ChartCardProps {
  title: string;
  children: React.ReactNode;
  isLoading: boolean;
  error: string | null;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, children, isLoading, error }) => (
  <div className="bg-white p-6 rounded-lg shadow-md min-h-[400px] flex flex-col">
    <h2 className="text-xl font-semibold mb-4 text-gray-700">{title}</h2>
    <div className="flex-grow relative">
      {isLoading && <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75"><p className="text-gray-500">正在加載...</p></div>}
      {error && <div className="absolute inset-0 flex items-center justify-center bg-red-50"><p className="text-red-600">錯誤: {error}</p></div>}
      {!isLoading && !error && children}
    </div>
  </div>
);

// --- Main Page Component ---
export default function TechnicalAnalysisPage() {
  const [bollingerData, setBollingerData] = useState<BollingerData | null>(null);
  const [macdData, setMacdData] = useState<MacdData | null>(null);
  const [rsiData, setRsiData] = useState<RsiData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errors, setErrors] = useState<Record<string, string | null>>({});

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setErrors({});
      const currentErrors: Record<string, string | null> = {};

      try {
        const results = await Promise.allSettled([
          fetch('http://localhost:8000/api/indicators/bollinger'),
          fetch('http://localhost:8000/api/indicators/macd'),
          fetch('http://localhost:8000/api/indicators/rsi'),
        ]);

        // Process Bollinger Bands
        if (results[0].status === 'fulfilled' && results[0].value.ok) {
          setBollingerData(await results[0].value.json());
        } else {
          currentErrors.bollinger = results[0].status === 'rejected' ? results[0].reason.message : `HTTP Error: ${results[0].value.status}`;
        }

        // Process MACD
        if (results[1].status === 'fulfilled' && results[1].value.ok) {
          setMacdData(await results[1].value.json());
        } else {
          currentErrors.macd = results[1].status === 'rejected' ? results[1].reason.message : `HTTP Error: ${results[1].value.status}`;
        }

        // Process RSI
        if (results[2].status === 'fulfilled' && results[2].value.ok) {
          setRsiData(await results[2].value.json());
        } else {
          currentErrors.rsi = results[2].status === 'rejected' ? results[2].reason.message : `HTTP Error: ${results[2].value.status}`;
        }

        setErrors(currentErrors);

      } catch (err: any) {
        // Catch potential general errors (unlikely with Promise.allSettled)
        console.error("Error fetching technical indicators:", err);
        setErrors({ general: err.message || 'An unexpected error occurred' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // --- Prepare Chart Data ---
  const bollingerChartData = {
    labels: bollingerData?.labels || [],
    datasets: [
      {
        label: 'Upper Band',
        data: bollingerData?.upper || [],
        borderColor: 'rgba(156, 163, 175, 0.5)', // gray-400
        tension: 0.1,
        pointRadius: 0,
        fill: '+1', // Fill to next dataset (Middle Band)
        backgroundColor: 'rgba(209, 213, 219, 0.2)', // gray-300 with opacity
      },
      {
        label: 'Middle Band (SMA)',
        data: bollingerData?.middle || [],
        borderColor: 'rgb(59, 130, 246)', // blue-500
        tension: 0.1,
        pointRadius: 0,
      },
      {
        label: 'Lower Band',
        data: bollingerData?.lower || [],
        borderColor: 'rgba(156, 163, 175, 0.5)', // gray-400
        tension: 0.1,
        pointRadius: 0,
        fill: '-1', // Fill to previous dataset (Middle Band)
        backgroundColor: 'rgba(209, 213, 219, 0.2)', // gray-300 with opacity
      },
    ],
  };

  const macdChartData = {
    labels: macdData?.labels || [],
    datasets: [
      {
        type: 'line' as const,
        label: 'MACD',
        data: macdData?.macd || [],
        borderColor: 'rgb(34, 197, 94)', // green-500
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'y',
      },
      {
        type: 'line' as const,
        label: 'Signal Line',
        data: macdData?.signal || [],
        borderColor: 'rgb(239, 68, 68)', // red-500
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'y',
      },
      {
        type: 'bar' as const,
        label: 'Histogram',
        data: macdData?.histogram || [],
        backgroundColor: macdData?.histogram.map(v => v >= 0 ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'), // Green/Red bars
        borderColor: macdData?.histogram.map(v => v >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'),
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
    labels: rsiData?.labels || [],
    datasets: [
      {
        label: 'RSI',
        data: rsiData?.rsi || [],
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
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">技術分析 Technical Analysis</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <ChartCard title="布林帶 Bollinger Bands" isLoading={isLoading} error={errors.bollinger}>
          {bollingerData ? (
            <Line options={getChartOptions('布林帶 Bollinger Bands')} data={bollingerChartData} />
          ) : <p className="text-gray-500 flex items-center justify-center h-full">無法加載布林帶數據。</p>}
        </ChartCard>

        <ChartCard title="MACD" isLoading={isLoading} error={errors.macd}>
          {macdData ? (
            <Chart type='bar' options={macdChartOptions} data={macdChartData} />
          ) : <p className="text-gray-500 flex items-center justify-center h-full">無法加載 MACD 數據。</p>}
        </ChartCard>

        <ChartCard title="相對強弱指數 RSI" isLoading={isLoading} error={errors.rsi}>
          {rsiData ? (
            <Line options={getChartOptions('相對強弱指數 RSI')} data={rsiChartData} />
          ) : <p className="text-gray-500 flex items-center justify-center h-full">無法加載 RSI 數據。</p>}
        </ChartCard>

        {/* Add more indicator cards here as needed */}

      </div>
    </div>
  );
} 