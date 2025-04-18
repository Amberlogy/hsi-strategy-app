'use client';

import { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement, // For Volume
  Title,
  Tooltip,
  Legend,
  TimeScale, // Import TimeScale for time series data
} from 'chart.js';
import { Line, Chart } from 'react-chartjs-2';
import zoomPlugin from 'chartjs-plugin-zoom'; // Import zoom plugin
import 'chartjs-adapter-date-fns'; // Adapter for time scale

// Register necessary Chart.js components and plugins
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale, // Register TimeScale
  zoomPlugin // Register zoom plugin
);

// --- Data Interfaces (Adjusted for time, close, volume) ---
interface HsiCurrentData {
  current_price: number;
  change_percent: number;
  volume: number;
}

interface HistoricalPoint {
  time: string; // Expecting 'YYYY-MM-DD' or a format date-fns can parse
  close: number;
  volume: number;
}

// --- Mock Data (Updated structure) ---
const mockHistoricalData: HistoricalPoint[] = [
  { time: '2024-03-01', close: 17000, volume: 150000000 },
  { time: '2024-03-02', close: 17100, volume: 160000000 },
  { time: '2024-03-03', close: 17200, volume: 175000000 },
  { time: '2024-03-04', close: 17250, volume: 170000000 },
  { time: '2024-03-05', close: 17300, volume: 180000000 },
  { time: '2024-03-06', close: 17350, volume: 165000000 },
  { time: '2024-03-07', close: 17400, volume: 190000000 },
];

// --- Main Page Component ---
export default function MarketOverviewPage() {
  // Assuming we only fetch current data now, historical is mocked
  const [hsiCurrentData, setHsiCurrentData] = useState<HsiCurrentData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Keep historical data mocked for now
  const hsiHistoricalData: HistoricalPoint[] = mockHistoricalData;

  useEffect(() => {
    const fetchCurrentData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:8000/api/indicators/hsi');
        if (!response.ok) {
          throw new Error(`無法獲取即時數據: ${response.status}`);
        }
        const currentData: HsiCurrentData = await response.json();
        setHsiCurrentData(currentData);
      } catch (err: any) {
        setError(err.message || '獲取恆指數據時出錯');
        console.error("Error fetching HSI data:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCurrentData();
  }, []);

  const priceChangeColor = hsiCurrentData?.change_percent
    ? hsiCurrentData.change_percent > 0 ? 'text-green-600' : hsiCurrentData.change_percent < 0 ? 'text-red-600' : 'text-gray-500'
    : 'text-gray-500';

  // --- Prepare Chart.js Data --- 
  const chartData = {
    labels: hsiHistoricalData.map(d => d.time),
    datasets: [
      {
        type: 'line' as const, // Explicitly type as line
        label: '恆生指數 (收盤價)',
        data: hsiHistoricalData.map(d => d.close),
        borderColor: 'rgb(59, 130, 246)', // blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.1,
        pointRadius: 1, // Smaller points
        yAxisID: 'yPrice', // Link to price axis
      },
      {
        type: 'bar' as const, // Explicitly type as bar
        label: '成交量',
        data: hsiHistoricalData.map(d => d.volume),
        backgroundColor: 'rgba(156, 163, 175, 0.4)', // gray-400 with opacity
        borderColor: 'rgba(156, 163, 175, 0.6)',
        yAxisID: 'yVolume', // Link to volume axis
        order: 1 // Ensure bars are behind the line
      },
    ],
  };

  // --- Chart.js Options --- 
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
        text: '恆生指數走勢與成交量',
        font: { size: 16 }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        titleFont: { size: 14 },
        bodyFont: { size: 12 },
        padding: 10,
        // Custom tooltip callbacks if needed
      },
      zoom: {
        pan: {
          enabled: true,
          mode: 'x' as const, // Enable panning only on x-axis
        },
        zoom: {
          wheel: { enabled: true }, // Enable zooming with mouse wheel
          pinch: { enabled: true }, // Enable zooming with pinch gesture
          mode: 'x' as const, // Enable zooming only on x-axis
        },
      }
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
          tooltipFormat: 'yyyy-MM-dd',
          displayFormats: {
             day: 'MM-dd' // Format for x-axis labels
          }
        },
        grid: {
          color: 'rgba(200, 200, 200, 0.1)', // Lighter grid lines
        },
        ticks: {
          source: 'auto' as const,
          maxRotation: 0,
          autoSkip: true,
        }
      },
      yPrice: { // Price Axis
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(200, 200, 200, 0.1)',
        },
        title: {
          display: true,
          text: '指數'
        }
      },
      yVolume: { // Volume Axis
        type: 'linear' as const,
        display: true, // Set to true to show volume axis
        position: 'right' as const,
        grid: { drawOnChartArea: false }, // Don't draw grid lines for volume axis
        ticks: {
          callback: function(value: number | string) {
            if (typeof value === 'number') {
              return value / 1_000_000 + 'M'; // Format as Millions
            }
            return value;
          }
        },
        title: {
          display: true,
          text: '成交量'
        }
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">市場總覽 Market Overview</h1>

      {/* Loading and Error states for Current Data */}
      {isLoading && (
        <div className="flex justify-center items-center h-20">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          <p className="ml-3 text-gray-600">正在加載即時數據...</p>
        </div>
      )}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">錯誤!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}

      {/* Display Current Data if available */}
      {hsiCurrentData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-white p-4 rounded-lg shadow-sm">
            <div className="text-center md:text-left">
              <h2 className="text-sm font-medium text-gray-500">恆生指數 (HSI)</h2>
              <p className="text-2xl font-bold">{hsiCurrentData.current_price.toLocaleString()}</p>
            </div>
             <div className="text-center md:text-left">
               <h2 className="text-sm font-medium text-gray-500">漲跌幅</h2>
               <p className={`text-2xl font-bold ${priceChangeColor}`}>
                 {hsiCurrentData.change_percent > 0 ? '+' : ''}{hsiCurrentData.change_percent.toFixed(2)}%
               </p>
            </div>
             <div className="text-center md:text-left">
               <h2 className="text-sm font-medium text-gray-500">今日成交量</h2>
               <p className="text-xl font-semibold">{(hsiCurrentData.volume / 1_000_000_000).toFixed(2)} B</p>
             </div>
             {/* Add placeholder for other potential current data */}
             <div className="text-center md:text-left">
               <h2 className="text-sm font-medium text-gray-500">--</h2>
               <p className="text-xl font-semibold">--</p>
             </div>
          </div>
      )}

      {/* Chart Area - Always render chart container, Line component handles data */}
      <div className="bg-white p-4 md:p-6 rounded-lg shadow-md">
        <div className="relative h-[500px]"> {/* Increased height for better view */}
          <Chart type='line' options={chartOptions} data={chartData} />
        </div>
      </div>

    </div>
  );
} 