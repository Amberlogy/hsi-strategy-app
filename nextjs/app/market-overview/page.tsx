'use client';

import React, { useState, useEffect, useMemo, useRef } from 'react';
import dynamic from 'next/dynamic';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  PointElement,
  LineElement,
  Filler,
  type LegendItem,
  type ChartData,
  type ChartOptions,
} from 'chart.js';
import { CandlestickElement, OhlcElement } from 'chartjs-chart-financial';
// --- REMOVE STATIC IMPORTS for adapter and plugin ---
// import 'chartjs-adapter-date-fns'; 
// import zoomPlugin from 'chartjs-plugin-zoom';

// Dynamically import the Chart component
const DynamicChart = dynamic(() => import('react-chartjs-2').then((mod) => mod.Chart), {
  ssr: false,
  loading: () => <p>Loading chart...</p>
});

// Define available chart types
type ChartDisplayType = 'candlestick' | 'line' | 'area' | 'ohlc';

// Define time interval options
type Interval = '5m' | '15m' | '1H' | '1D' | '1W' | '1M';

// Define duration options
type Duration = '1D' | '5D' | '1M' | '3M' | '6M' | '1Y' | 'All';

// Define Chart.js accepted time units
type ChartTimeUnit = 'minute' | 'hour' | 'day' | 'week' | 'month';

// --- Data Interfaces ---
interface HsiCurrentData {
  current_price: number;
  change_percent: number;
  volume: number;
}

// Updated interface for OHLC data
interface HistoricalPoint {
  time: string; 
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// --- Mock Data (Updated with OHLC) ---
const mockHistoricalData: HistoricalPoint[] = [
  { time: '2024-03-01', open: 16950, high: 17050, low: 16900, close: 17000, volume: 150000000 },
  { time: '2024-03-02', open: 17000, high: 17150, low: 16980, close: 17100, volume: 160000000 },
  { time: '2024-03-03', open: 17120, high: 17250, low: 17080, close: 17200, volume: 175000000 },
  { time: '2024-03-04', open: 17200, high: 17300, low: 17180, close: 17250, volume: 170000000 },
  { time: '2024-03-05', open: 17260, high: 17350, low: 17220, close: 17300, volume: 180000000 },
  { time: '2024-03-06', open: 17300, high: 17400, low: 17280, close: 17350, volume: 165000000 },
  { time: '2024-03-07', open: 17360, high: 17450, low: 17320, close: 17400, volume: 190000000 },
];

// Add mock current data
const mockCurrentData: HsiCurrentData = {
    current_price: 17425.50,
    change_percent: 0.35, // Example positive change
    volume: 195000000,
};

// --- Generate Mock Intraday Data (Example: 5-minute intervals for the last day) ---
interface IntradayPoint extends Omit<HistoricalPoint, 'time'> {
    timestamp: number; // Use timestamp for intraday
}

const generateMockIntradayData = (basePrice = 17400, numPoints = 100, intervalMinutes = 5): IntradayPoint[] => {
    const data: IntradayPoint[] = [];
    let currentTime = new Date().getTime(); // Start from now
    let currentPrice = basePrice;

    for (let i = 0; i < numPoints; i++) {
        const open = currentPrice;
        const change = (Math.random() - 0.5) * 20; // Random small fluctuation
        const close = open + change;
        const high = Math.max(open, close) + Math.random() * 5;
        const low = Math.min(open, close) - Math.random() * 5;
        const volume = 1000000 + Math.random() * 5000000; // Smaller volume for intraday
        const timestamp = currentTime - (numPoints - 1 - i) * intervalMinutes * 60 * 1000;

        data.push({ timestamp, open, high, low, close, volume });
        currentPrice = close; // Next open starts from last close
    }
    return data;
};

const mockIntradayData = generateMockIntradayData(mockHistoricalData[mockHistoricalData.length-1]?.close || 17400);

// --- Helper Function for SMA ---
const calculateSMA = (data: { x: number, y: number }[], period: number): ({ x: number, y: number | null }[]) => {
  if (!data || data.length < period) return [];

  const smaValues: ({ x: number, y: number | null }[]) = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      smaValues.push({ x: data[i].x, y: null }); // Not enough data for SMA yet
    } else {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j].y;
      }
      smaValues.push({ x: data[i].x, y: sum / period });
    }
  }
  return smaValues;
};

// --- Helper Function for RSI ---
const calculateRSI = (data: { x: number, y: number }[], period: number = 14): ({ x: number, y: number | null }[]) => {
  if (!data || data.length <= period) return [];

  const rsiValues: ({ x: number, y: number | null }[]) = new Array(data.length).fill(null);
  let gains: number[] = [];
  let losses: number[] = [];

  // Calculate initial changes
  for (let i = 1; i <= period; i++) {
    const change = data[i].y - data[i - 1].y;
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? -change : 0);
  }

  let avgGain = gains.reduce((a, b) => a + b, 0) / period;
  let avgLoss = losses.reduce((a, b) => a + b, 0) / period;

  const calculateRSIValue = (ag: number, al: number): number | null => {
    if (al === 0) return 100;
    if (ag === 0) return 0; // Avoid division by zero, RSI is 0 if only losses
    const rs = ag / al;
    return 100 - (100 / (1 + rs));
  };

  rsiValues[period] = { x: data[period].x, y: calculateRSIValue(avgGain, avgLoss) };

  // Calculate subsequent RSI values using Wilder's smoothing
  for (let i = period + 1; i < data.length; i++) {
    const change = data[i].y - data[i - 1].y;
    const gain = change > 0 ? change : 0;
    const loss = change < 0 ? -change : 0;

    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;

    rsiValues[i] = { x: data[i].x, y: calculateRSIValue(avgGain, avgLoss) };
  }
  
  // Fill initial nulls for alignment
  for (let i = 0; i < period; i++) {
      rsiValues[i] = {x: data[i].x, y: null};
  }

  return rsiValues;
};

// --- Helper Function for EMA (used by MACD) ---
const calculateEMA = (data: { x: number, y: number }[], period: number): ({ x: number, y: number | null }[]) => {
  if (!data || data.length < period) return new Array(data.length).fill(null).map((_, i) => ({ x: data[i]?.x, y: null }));

  const emaValues: ({ x: number, y: number | null }[]) = new Array(data.length).fill(null);
  const multiplier = 2 / (period + 1);

  // Calculate the initial SMA for the first EMA value
  let initialSum = 0;
  for (let i = 0; i < period; i++) {
    initialSum += data[i].y;
  }
  emaValues[period - 1] = { x: data[period - 1].x, y: initialSum / period };

  // Calculate subsequent EMA values
  for (let i = period; i < data.length; i++) {
    const currentPrice = data[i].y;
    const previousEMA = emaValues[i - 1]?.y;
    if (previousEMA !== null) { // Check if previous EMA is valid
        const currentEMA = (currentPrice - previousEMA) * multiplier + previousEMA;
        emaValues[i] = { x: data[i].x, y: currentEMA };
    } else {
        // Handle cases where previous EMA is null (e.g., start of data)
        // Recalculate SMA if needed, or handle as appropriate for your logic
        // For simplicity, we'll keep it null if the previous was null after the initial calculation
         emaValues[i] = { x: data[i].x, y: null };
    }
  }

   // Fill initial nulls
   for (let i = 0; i < period - 1; i++) {
      emaValues[i] = {x: data[i].x, y: null};
   }

  return emaValues;
};

// --- Helper Function for MACD ---
interface MACDResult {
    macdLine: { x: number, y: number | null }[];
    signalLine: { x: number, y: number | null }[];
    histogram: { x: number, y: number | null }[];
}

const calculateMACD = (
    data: { x: number, y: number }[],
    fastPeriod: number = 12,
    slowPeriod: number = 26,
    signalPeriod: number = 9
): MACDResult => {
    const emaFast = calculateEMA(data, fastPeriod);
    const emaSlow = calculateEMA(data, slowPeriod);

    const macdLine: { x: number, y: number | null }[] = emaFast.map((fast, i) => {
        const slow = emaSlow[i];
        if (fast?.y !== null && slow?.y !== null) {
            return { x: fast.x, y: fast.y - slow.y };
        } else {
            return { x: fast?.x ?? slow?.x ?? 0, y: null }; // Use x from either, default 0 if both missing
        }
    });

    // Prepare data for signal line calculation (MACD line itself)
    const macdLineForSignal = macdLine.filter(d => d.y !== null) as { x: number, y: number }[];
    const signalLineRaw = calculateEMA(macdLineForSignal, signalPeriod);

    // Align signal line back to original data length/timestamps
    const signalLine: { x: number, y: number | null }[] = new Array(data.length).fill(null);
    let signalIndex = 0;
    for(let i=0; i< macdLine.length; i++){
        signalLine[i] = { x: macdLine[i].x, y: null }; // Initialize with null
        if(macdLine[i].y !== null && signalIndex < signalLineRaw.length){
            // Find the corresponding raw signal value by matching timestamp if possible
            // This simple alignment assumes macdLineForSignal keeps order
            if(signalLineRaw[signalIndex].x === macdLine[i].x) {
                signalLine[i].y = signalLineRaw[signalIndex].y;
                signalIndex++;
            }
             // More robust alignment might be needed for sparse data
        }
    }


    const histogram: { x: number, y: number | null }[] = macdLine.map((macd, i) => {
        const signal = signalLine[i];
        if (macd?.y !== null && signal?.y !== null) {
            return { x: macd.x, y: macd.y - signal.y };
        } else {
            return { x: macd?.x ?? signal?.x ?? 0, y: null };
        }
    });

    return { macdLine, signalLine, histogram };
};

// --- Main Page Component ---
export default function MarketOverviewPage() {
  const [hsiCurrentData] = useState<HsiCurrentData>(mockCurrentData);
  const hsiHistoricalData: HistoricalPoint[] = mockHistoricalData;
  const [chartRegistered, setChartRegistered] = useState(false);
  const [chartType, setChartType] = useState<ChartDisplayType>('candlestick');
  const [interval, setInterval] = useState<Interval>('1D');
  const [duration, setDuration] = useState<Duration>('6M');

  // Refs for charts (optional, for potential future sync)
  const mainChartRef = useRef<ChartJS | null>(null);
  const volumeChartRef = useRef<ChartJS | null>(null);

  // --- Modified useEffect for dynamic imports and registration ---
  useEffect(() => {
    const registerChart = async () => {
      // Dynamically import adapter and plugin
      await import('chartjs-adapter-date-fns');
      const zoomPlugin = (await import('chartjs-plugin-zoom')).default;

      // Register components including Candlestick
      ChartJS.register(
        CategoryScale,
        LinearScale,
        BarElement,
        Title,
        Tooltip,
        Legend,
        TimeScale,
        CandlestickElement,
        OhlcElement,
        PointElement,
        LineElement,
        Filler,
        zoomPlugin
      );
      setChartRegistered(true);
    };

    if (!chartRegistered) {
        registerChart();
    }

  }, [chartRegistered]);

  const priceChangeColor = hsiCurrentData.change_percent > 0 ? 'text-green-600' : hsiCurrentData.change_percent < 0 ? 'text-red-600' : 'text-gray-500';

  // --- Prepare Chart Data (Handles Interval and Duration) --- 
  const { mainChartData, volumeChartData, rsiChartData, macdChartData, timeUnit } = useMemo(() => {
    let sourceData: (HistoricalPoint | IntradayPoint)[] = [];
    let calculatedTimeUnit: ChartTimeUnit = 'day'; // Initialize with a default valid type

    // 1. Select data source and determine time unit
    if (interval === '5m' || interval === '15m') {
      sourceData = mockIntradayData;
      calculatedTimeUnit = 'minute';
    } else if (interval === '1H') {
      sourceData = mockIntradayData;
      calculatedTimeUnit = 'hour';
    } else if (interval === '1W') {
      sourceData = hsiHistoricalData;
      calculatedTimeUnit = 'week';
    } else if (interval === '1M') {
       sourceData = hsiHistoricalData;
       calculatedTimeUnit = 'month';
    } else { // Default to '1D'
      sourceData = hsiHistoricalData;
      calculatedTimeUnit = 'day';
    }

    // 2. Filter data based on duration
    const now = new Date().getTime();
    let startTimestamp = 0; 

    switch (duration) {
        case '1D': startTimestamp = now - 1 * 24 * 60 * 60 * 1000; break;
        case '5D': startTimestamp = now - 5 * 24 * 60 * 60 * 1000; break;
        case '1M': startTimestamp = new Date(new Date().setMonth(new Date().getMonth() - 1)).getTime(); break;
        case '3M': startTimestamp = new Date(new Date().setMonth(new Date().getMonth() - 3)).getTime(); break;
        case '6M': startTimestamp = new Date(new Date().setMonth(new Date().getMonth() - 6)).getTime(); break;
        case '1Y': startTimestamp = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).getTime(); break;
        case 'All': startTimestamp = 0; break;
    }

    const filteredData = sourceData.filter(d => {
        const pointTimestamp = 'timestamp' in d ? d.timestamp : new Date(d.time).getTime();
        return pointTimestamp >= startTimestamp;
    });

    // 3. Prepare data points for charts using filteredData
    const baseData = filteredData.map(d => ({
        x: 'timestamp' in d ? d.timestamp : new Date(d.time).valueOf(),
        o: d.open,
        h: d.high,
        l: d.low,
        c: d.close,
        y: d.close
    }));    
    const volumeDataPoints = filteredData.map(d => ({
         x: 'timestamp' in d ? d.timestamp : new Date(d.time).valueOf(), 
         y: d.volume
    }));
    const closeDataForSMA = filteredData.map(d => ({
         x: 'timestamp' in d ? d.timestamp : new Date(d.time).valueOf(), 
         y: d.close
    }));

    // 4. Calculate SMAs (using potentially fewer points for intraday)
    const sma10Data = calculateSMA(closeDataForSMA, 10);
    const sma20Data = calculateSMA(closeDataForSMA, 20);

    // Calculate RSI
    const rsiData = calculateRSI(closeDataForSMA, 14); 

    // Calculate MACD
    const { macdLine, signalLine, histogram } = calculateMACD(closeDataForSMA);

    // 5. Create priceDataset based on chartType (logic remains similar)
    let priceDataset: any;
    switch (chartType) {
        case 'line':
          priceDataset = {
            type: 'line' as const, label: 'HSI (Close)', data: baseData.map(d => ({ x: d.x, y: d.c })), 
            borderColor: 'rgba(59, 130, 246, 1)', backgroundColor: 'rgba(59, 130, 246, 0.1)',
            yAxisID: 'yPrice', tension: 0.1, pointRadius: 0, 
          }; break;
        case 'area':
          priceDataset = {
            type: 'line' as const, label: 'HSI (Close)', data: baseData.map(d => ({ x: d.x, y: d.c })), 
            borderColor: 'rgba(59, 130, 246, 1)', backgroundColor: 'rgba(59, 130, 246, 0.3)', fill: true, 
            yAxisID: 'yPrice', tension: 0.1, pointRadius: 0, 
          }; break;
        case 'ohlc':
          priceDataset = {
            type: 'ohlc' as const, label: 'HSI (OHLC Bars)', data: baseData.map(d => ({ x: d.x, o: d.o, h: d.h, l: d.l, c: d.c })), 
            yAxisID: 'yPrice', color: { up: 'rgba(8, 153, 129, 0.8)', down: 'rgba(213, 70, 64, 0.8)', unchanged: 'rgba(156, 163, 175, 0.8)' }, 
            borderColor: { up: 'rgba(8, 153, 129, 1)', down: 'rgba(213, 70, 64, 1)', unchanged: 'rgba(156, 163, 175, 1)' }, borderWidth: 1, 
          }; break;
        case 'candlestick': default:
          priceDataset = {
            type: 'candlestick' as const, label: 'HSI (OHLC)', data: baseData.map(d => ({ x: d.x, o: d.o, h: d.h, l: d.l, c: d.c })), 
            yAxisID: 'yPrice', color: { up: 'rgba(8, 153, 129, 0.8)', down: 'rgba(213, 70, 64, 0.8)', unchanged: 'rgba(156, 163, 175, 0.8)' }, 
            borderColor: 'rgba(50, 50, 50, 1)', borderWidth: 1,
          }; break;
    }

    // 6. Create SMA datasets (using sma10Data, sma20Data)
    const sma10Dataset = { type: 'line' as const, label: 'SMA(10)', data: sma10Data, borderColor: 'rgba(255, 159, 64, 1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yPrice', tension: 0.1 };
    const sma20Dataset = { type: 'line' as const, label: 'SMA(20)', data: sma20Data, borderColor: 'rgba(153, 102, 255, 1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yPrice', tension: 0.1 };
    
    // 7. Create volume dataset (using volumeDataPoints)
    const volumeDataset = { type: 'bar' as const, label: '成交量', data: volumeDataPoints, backgroundColor: 'rgba(156, 163, 175, 0.4)', borderColor: 'rgba(156, 163, 175, 0.6)', yAxisID: 'yVolume', order: 1 };

    // Create RSI dataset
    const rsiDataset = {
        type: 'line' as const,
        label: 'RSI(14)',
        data: rsiData,
        borderColor: 'rgba(255, 99, 132, 1)', // Example pink color
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 1,
        pointRadius: 0,
        yAxisID: 'yRsi', // Assign to RSI Y-axis
        tension: 0.1,
    };

    // Create MACD datasets
    const macdLineDataset = {
        type: 'line' as const,
        label: 'MACD',
        data: macdLine,
        borderColor: 'rgba(54, 162, 235, 1)', // Blue
        borderWidth: 1,
        pointRadius: 0,
        yAxisID: 'yMacd',
        tension: 0.1,
    };
    const signalLineDataset = {
        type: 'line' as const,
        label: 'Signal',
        data: signalLine,
        borderColor: 'rgba(255, 99, 132, 1)', // Red
        borderWidth: 1,
        pointRadius: 0,
        yAxisID: 'yMacd',
        tension: 0.1,
    };
    const histogramDataset = {
        type: 'bar' as const,
        label: 'Histogram',
        data: histogram,
        backgroundColor: histogram.map(d => d.y !== null ? (d.y >= 0 ? 'rgba(75, 192, 192, 0.5)' : 'rgba(255, 99, 132, 0.5)') : 'transparent'), // Green/Red bars
        borderColor: histogram.map(d => d.y !== null ? (d.y >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)') : 'transparent'),
        borderWidth: 1,
        yAxisID: 'yMacd',
    };

    // 8. Return structured data including MACD
    return {
      mainChartData: { datasets: [priceDataset, sma10Dataset, sma20Dataset] },
      volumeChartData: { datasets: [volumeDataset] },
      rsiChartData: { datasets: [rsiDataset] },
      macdChartData: { datasets: [histogramDataset, macdLineDataset, signalLineDataset] }, // Add MACD data (Histogram first for layering)
      timeUnit: calculatedTimeUnit
    };
  }, [hsiHistoricalData, mockIntradayData, chartType, interval, duration]);

  // --- Define Chart Options (Use correctly typed timeUnit) --- 
  const commonOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index' as const, intersect: false },
    plugins: {
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        titleFont: { size: 14 },
        bodyFont: { size: 12 },
        padding: 10,
      },
      zoom: { 
        pan: {
          enabled: chartRegistered,
          mode: 'x' as const,
        },
        zoom: {
          wheel: { enabled: chartRegistered },
          pinch: { enabled: chartRegistered },
          mode: 'x' as const,
        },
      }
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: timeUnit,
          tooltipFormat: timeUnit === 'minute' || timeUnit === 'hour' ? 'yyyy-MM-dd HH:mm' : 'yyyy-MM-dd', 
          displayFormats: {
             minute: 'HH:mm', 
             hour: 'MM-dd HH:mm', 
             day: 'MM-dd', 
             week: 'yyyy-MM-dd', 
             month: 'yyyy-MM' 
          }
        },
        grid: {
          color: 'rgba(200, 200, 200, 0.1)',
        },
        ticks: {
          source: 'auto' as const,
          maxRotation: 0,
          autoSkip: true,
        }
      },
    }
  }), [chartRegistered, timeUnit]);

  const mainChartOptions: ChartOptions = useMemo(() => ({
    ...commonOptions,
    plugins: {
      ...commonOptions.plugins,
      legend: {
        display: true, 
        position: 'top' as const, 
        labels: { boxWidth: 12, font: { size: 10 }, filter: (item: LegendItem) => item.text ? item.text.startsWith('SMA') : false }
      },
      title: { display: true, text: `恆生指數 ${chartType.toUpperCase()} (模擬數據)`, font: { size: 16 } },
    },
    scales: {
      ...commonOptions.scales,
      x: { ...commonOptions.scales.x, ticks: { ...commonOptions.scales.x?.ticks, display: false } }, // Hide X ticks on main chart
      yPrice: { type: 'linear' as const, display: true, position: 'left' as const, grid: { color: 'rgba(200, 200, 200, 0.2)' }, title: { display: true, text: '指數' } },
    }
  }), [commonOptions, chartType, timeUnit]);

  const volumeChartOptions: ChartOptions = useMemo(() => ({
    ...commonOptions,
    plugins: {
      ...commonOptions.plugins,
       legend: { display: false }, // No legend for volume chart
      title: { display: false }, // No title for volume chart
    },
    scales: {
      ...commonOptions.scales, // Inherit X axis config
      yVolume: { 
        type: 'linear' as const, 
        display: true, 
        position: 'left' as const, // Volume usually on left if solo 
        grid: { drawOnChartArea: false }, 
        ticks: {
          callback: function(value: number | string) {
            if (typeof value === 'number') {
              if (value >= 1_000_000_000) return (value / 1_000_000_000).toFixed(1) + 'B';
              if (value >= 1_000_000) return (value / 1_000_000).toFixed(1) + 'M';
              if (value >= 1_000) return (value / 1_000).toFixed(1) + 'K';
              return value;
            }
            return value;
          },
           maxTicksLimit: 5 // Limit ticks on volume axis
        },
        title: { display: true, text: '成交量' }
      }
    }
  }), [commonOptions, timeUnit]);

  // Define RSI Chart Options
  const rsiChartOptions: ChartOptions = useMemo(() => ({
    ...commonOptions,
    plugins: {
      ...commonOptions.plugins,
      legend: { display: false }, 
      title: { display: false }, 
    },
    scales: {
      ...commonOptions.scales, // Inherit X axis config
      yRsi: { // Define Y axis for RSI
        type: 'linear' as const, 
        display: true, 
        position: 'left' as const, 
        min: 0, // RSI scale is 0-100
        max: 100,
        grid: { 
            drawOnChartArea: false, 
            // Optional: add grid lines for 30 and 70
            // color: (context) => context.tick.value === 30 || context.tick.value === 70 ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 0, 0, 0.1)',
         }, 
        ticks: {
           maxTicksLimit: 5 
        },
        title: { display: true, text: 'RSI(14)' }
      }
    }
  }), [commonOptions, timeUnit]);

  // Define MACD Chart Options
  const macdChartOptions: ChartOptions = useMemo(() => ({
    ...commonOptions,
    plugins: {
      ...commonOptions.plugins,
      legend: { display: true, position: 'top' as const, labels: { boxWidth: 10, font: { size: 10 }, filter: (item: LegendItem) => item.text !== 'Histogram' } }, // Show only MACD and Signal in legend
      title: { display: false },
    },
    scales: {
      ...commonOptions.scales, // Inherit X axis config
      x: { ...commonOptions.scales.x, ticks: { ...commonOptions.scales.x?.ticks, display: true } }, // Show X ticks on the bottom chart
      yMacd: { // Define Y axis for MACD
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: { drawOnChartArea: false },
        ticks: {
           maxTicksLimit: 5
        },
        title: { display: true, text: 'MACD' }
      }
    }
  }), [commonOptions, timeUnit]);

  // Updated function to get button style, accepting a generic type T
  const getButtonStyle = <T extends string>(currentValue: T, targetValue: T) => {
    return `px-3 py-1 rounded mr-2 text-sm ${currentValue === targetValue 
      ? 'bg-blue-600 text-white' 
      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`;
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">市場總覽 Market Overview (模擬數據)</h1>

      {/* Display Mock Current Data */}
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
         <div className="text-center md:text-left">
           <h2 className="text-sm font-medium text-gray-500">--</h2>
           <p className="text-xl font-semibold">--</p>
         </div>
      </div>

      {/* Chart Area - Adjust heights */} 
      <div className="bg-white p-4 md:p-6 rounded-lg shadow-md">
         {/* Controls Container */}
         <div className="flex flex-col md:flex-row flex-wrap gap-y-2 mb-4">
           {/* Chart Type Switcher */}    
           <div className="mr-6 mb-2 md:mb-0">
             <span className="text-sm font-medium mr-3">圖表類型:</span>
             <button className={getButtonStyle(chartType, 'candlestick')} onClick={() => setChartType('candlestick')}>陰陽燭</button>
             <button className={getButtonStyle(chartType, 'line')} onClick={() => setChartType('line')}>線形圖</button>
             <button className={getButtonStyle(chartType, 'area')} onClick={() => setChartType('area')}>山形圖</button>
             <button className={getButtonStyle(chartType, 'ohlc')} onClick={() => setChartType('ohlc')}>OHLC</button>
           </div>

           {/* Interval Switcher */} 
           <div className="mr-6 mb-2 md:mb-0">
              <span className="text-sm font-medium mr-3">間隔:</span>
              <button className={getButtonStyle(interval, '5m')} onClick={() => setInterval('5m')}>5分</button>
              <button className={getButtonStyle(interval, '15m')} onClick={() => setInterval('15m')}>15分</button>
              <button className={getButtonStyle(interval, '1H')} onClick={() => setInterval('1H')}>1小時</button>
              <button className={getButtonStyle(interval, '1D')} onClick={() => setInterval('1D')}>日線</button>
              <button className={getButtonStyle(interval, '1W')} onClick={() => setInterval('1W')}>週線</button>
              <button className={getButtonStyle(interval, '1M')} onClick={() => setInterval('1M')}>月線</button>
            </div>

           {/* Duration Switcher */} 
           <div>
              <span className="text-sm font-medium mr-3">持續時間:</span>
              <button className={getButtonStyle(duration, '1D')} onClick={() => setDuration('1D')}>1天</button>
              <button className={getButtonStyle(duration, '5D')} onClick={() => setDuration('5D')}>5天</button>
              <button className={getButtonStyle(duration, '1M')} onClick={() => setDuration('1M')}>1個月</button>
              <button className={getButtonStyle(duration, '3M')} onClick={() => setDuration('3M')}>3個月</button>
              <button className={getButtonStyle(duration, '6M')} onClick={() => setDuration('6M')}>6個月</button>
              <button className={getButtonStyle(duration, '1Y')} onClick={() => setDuration('1Y')}>1年</button>
              <button className={getButtonStyle(duration, 'All')} onClick={() => setDuration('All')}>全部</button>
            </div>
         </div>

        {/* Main Chart Container (Adjust height ~45%) */}
        <div className="relative h-[250px] mb-1"> 
          {chartRegistered && mainChartData.datasets && mainChartData.datasets[0].data && mainChartData.datasets[0].data.length > 0 ? (
            <DynamicChart 
              ref={mainChartRef} // Optional ref
              type={chartType === 'area' ? 'line' : chartType}
              data={mainChartData} 
              options={mainChartOptions as ChartOptions} // Cast options
            /> 
          ) : (
            <p>Loading main chart...</p>
          )}
        </div>

         {/* Volume Chart Container (Adjust height ~18%) */}
         <div className="relative h-[100px] mb-1">
           {chartRegistered && volumeChartData.datasets && volumeChartData.datasets[0].data && volumeChartData.datasets[0].data.length > 0 ? (
             <DynamicChart 
               ref={volumeChartRef} // Optional ref
               type={'bar'} // Volume is always bar
               data={volumeChartData} 
               options={volumeChartOptions as ChartOptions} // Cast options
             /> 
           ) : (
             <p>Loading volume chart...</p>
           )}
         </div>

         {/* RSI Chart Container (Adjust height ~18%) */}
         <div className="relative h-[100px] mb-1">
            {chartRegistered && rsiChartData.datasets && rsiChartData.datasets[0].data && rsiChartData.datasets[0].data.length > 0 ? (
              <DynamicChart 
                // ref={rsiChartRef} // Optional ref if needed later
                type={'line'} 
                data={rsiChartData} 
                options={rsiChartOptions as ChartOptions} 
              /> 
            ) : (
              <p>Loading RSI chart...</p>
            )}
          </div>

         {/* MACD Chart Container (New, Adjust height ~18%) */}
         <div className="relative h-[100px]">
            {chartRegistered && macdChartData.datasets && macdChartData.datasets[0].data && macdChartData.datasets[0].data.length > 0 ? (
              <DynamicChart 
                // ref={macdChartRef} // Optional ref if needed later
                type={'bar'} // Base type for chart, lines are specified in datasets
                data={macdChartData}
                options={macdChartOptions as ChartOptions}
              />
            ) : (
              <p>Loading MACD chart...</p>
            )}
          </div>
      </div>

    </div>
  );
} 