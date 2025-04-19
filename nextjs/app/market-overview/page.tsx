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
  type Plugin, // Import Plugin type
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

// 動態導入 chartjs-adapter-date-fns 和 zoom 插件
const dynamicImports = async () => {
  await import('chartjs-adapter-date-fns');
  const zoomModule = await import('chartjs-plugin-zoom');
  return { zoomPlugin: zoomModule.default };
};

// Define available chart types
type ChartDisplayType = 'candlestick' | 'line' | 'area' | 'ohlc';

// --- NEW: Define available main technical indicators ---
type MainIndicatorType = 'sma' | 'wma' | 'ema' | 'bollinger' | 'sar';
const indicatorLabels: Record<MainIndicatorType, string> = {
  sma: '移動平均線 (SMA)',
  wma: '加權移動平均線 (WMA)',
  ema: '指數移動平均線 (EMA)',
  bollinger: '保力加通道 (Bollinger)',
  sar: '拋物線轉向 (SAR)',
};
// --- NEW: Define available periods ---
const availablePeriods = [5, 10, 20, 50, 100, 150];

// --- NEW: Define available sub-chart indicators ---
type SubIndicatorType = 'rsi' | 'macd' | 'slow_stc' | 'william_r' | 'roc' | 'volume'; // Added volume as an option
const subIndicatorLabels: Record<SubIndicatorType, string> = {
  rsi: '相對強弱指數 (RSI)',
  macd: '移動平均匯聚背馳指標 (MACD)',
  slow_stc: '隨機慢步指標 (Slow STC)',
  william_r: '威廉指標 (William %R)',
  roc: '變速率 (ROC)',
  volume: '成交量 (Volume)' // Added Volume here
};

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

// --- Helper Function for WMA ---
const calculateWMA = (data: { x: number, y: number }[], period: number): ({ x: number, y: number | null }[]) => {
  if (!data || data.length < period) return new Array(data.length).fill(null).map((_, i) => ({ x: data[i]?.x, y: null }));

  const wmaValues: ({ x: number, y: number | null }[]) = new Array(data.length).fill(null);
  const weightSum = period * (period + 1) / 2;

  for (let i = period - 1; i < data.length; i++) {
    let weightedSum = 0;
    for (let j = 0; j < period; j++) {
      weightedSum += data[i - j].y * (period - j);
    }
    wmaValues[i] = { x: data[i].x, y: weightedSum / weightSum };
  }
   // Fill initial nulls
   for (let i = 0; i < period - 1; i++) {
      wmaValues[i] = {x: data[i].x, y: null};
   }
  return wmaValues;
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

// --- Helper Function for Bollinger Bands ---
interface BollingerBandsResult {
    middle: { x: number, y: number | null }[];
    upper: { x: number, y: number | null }[];
    lower: { x: number, y: number | null }[];
}

const calculateBollingerBands = (data: { x: number, y: number }[], period: number = 20, stdDevMultiplier: number = 2): BollingerBandsResult => {
    if (!data || data.length < period) {
        const emptyResult = new Array(data.length).fill(null).map((_, i) => ({ x: data[i]?.x, y: null }));
        return { middle: emptyResult, upper: emptyResult, lower: emptyResult };
    }

    const middleBand: { x: number, y: number | null }[] = new Array(data.length).fill(null);
    const upperBand: { x: number, y: number | null }[] = new Array(data.length).fill(null);
    const lowerBand: { x: number, y: number | null }[] = new Array(data.length).fill(null);

    for (let i = period - 1; i < data.length; i++) {
        let sum = 0;
        const slice = data.slice(i - period + 1, i + 1);
        slice.forEach(d => sum += d.y);
        const sma = sum / period;
        middleBand[i] = { x: data[i].x, y: sma };

        let sumSqDiff = 0;
        slice.forEach(d => sumSqDiff += Math.pow(d.y - sma, 2));
        const stdDev = Math.sqrt(sumSqDiff / period);

        upperBand[i] = { x: data[i].x, y: sma + stdDev * stdDevMultiplier };
        lowerBand[i] = { x: data[i].x, y: sma - stdDev * stdDevMultiplier };
    }
     // Fill initial nulls
     for (let i = 0; i < period - 1; i++) {
        middleBand[i] = {x: data[i].x, y: null};
        upperBand[i] = {x: data[i].x, y: null};
        lowerBand[i] = {x: data[i].x, y: null};
     }

    return { middle: middleBand, upper: upperBand, lower: lowerBand };
};

// --- Helper Function for Parabolic SAR ---
interface SARPoint { x: number; y: number | null }
const calculateSAR = (
    highData: number[], // Array of high prices
    lowData: number[],  // Array of low prices
    timestamps: number[], // Array of corresponding timestamps
    accelerationFactorStart: number = 0.02,
    accelerationFactorIncrement: number = 0.02,
    accelerationFactorMax: number = 0.2
): SARPoint[] => {
    if (!highData || !lowData || highData.length !== lowData.length || highData.length < 2) {
        return new Array(highData?.length ?? 0).fill(null).map((_, i) => ({ x: timestamps?.[i] ?? 0, y: null }));
    }

    const sarValues: SARPoint[] = new Array(highData.length).fill(null).map((_, i) => ({ x: timestamps[i], y: null }));
    let isLong = true; // Initial trend assumption (can be refined)
    let accelerationFactor = accelerationFactorStart;
    let extremePoint = highData[0]; // Initial extreme point

    // Determine initial trend and SAR (often based on first few bars)
    if (lowData.length > 1) {
         isLong = highData[1] > highData[0]; // Simple check for initial trend
         sarValues[1] = { x: timestamps[1], y: isLong ? lowData[0] : highData[0] };
         extremePoint = isLong ? highData[1] : lowData[1];
    } else {
        return sarValues; // Not enough data
    }


    for (let i = 2; i < highData.length; i++) {
        const prevSar = sarValues[i - 1]?.y;
        if (prevSar === null) continue; // Skip if previous SAR is null

        let currentSar = prevSar + accelerationFactor * (extremePoint - prevSar);

        if (isLong) {
            // Clamp SAR below the low of the previous two periods
            currentSar = Math.min(currentSar, lowData[i - 1], lowData[i - 2] ?? lowData[i-1]);

            if (lowData[i] < currentSar) { // Trend reversal to short
                isLong = false;
                currentSar = extremePoint; // SAR becomes the recent extreme high
                accelerationFactor = accelerationFactorStart;
                extremePoint = lowData[i]; // New extreme point is the current low
            } else { // Continue long trend
                if (highData[i] > extremePoint) {
                    extremePoint = highData[i];
                    accelerationFactor = Math.min(accelerationFactor + accelerationFactorIncrement, accelerationFactorMax);
                }
            }
        } else { // Short trend
            // Clamp SAR above the high of the previous two periods
            currentSar = Math.max(currentSar, highData[i - 1], highData[i - 2] ?? highData[i-1]);

            if (highData[i] > currentSar) { // Trend reversal to long
                isLong = true;
                currentSar = extremePoint; // SAR becomes the recent extreme low
                accelerationFactor = accelerationFactorStart;
                extremePoint = highData[i]; // New extreme point is the current high
            } else { // Continue short trend
                if (lowData[i] < extremePoint) {
                    extremePoint = lowData[i];
                    accelerationFactor = Math.min(accelerationFactor + accelerationFactorIncrement, accelerationFactorMax);
                }
            }
        }
        sarValues[i] = { x: timestamps[i], y: currentSar };
    }

    return sarValues;
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

// --- Helper Function for Slow STC (%K and %D) ---
interface STCResult {
  percentK: { x: number, y: number | null }[];
  percentD: { x: number, y: number | null }[];
}

const calculateSlowSTC = (
  highData: number[],
  lowData: number[],
  closeData: { x: number, y: number }[],
  kPeriod: number = 14,
  dPeriod: number = 3,
  smoothK: number = 3 // Smoothing period for %K to make it slow STC
): STCResult => {
  if (!highData || !lowData || !closeData || highData.length < kPeriod || highData.length !== lowData.length || highData.length !== closeData.length) {
    const empty = new Array(highData?.length ?? 0).fill(null).map((_, i) => ({ x: closeData[i]?.x ?? 0, y: null }));
    return { percentK: empty, percentD: empty };
  }

  const rawKValues: { x: number, y: number | null }[] = new Array(highData.length).fill(null);

  // Calculate Raw %K
  for (let i = kPeriod - 1; i < highData.length; i++) {
    const sliceHigh = highData.slice(i - kPeriod + 1, i + 1);
    const sliceLow = lowData.slice(i - kPeriod + 1, i + 1);
    const highestHigh = Math.max(...sliceHigh);
    const lowestLow = Math.min(...sliceLow);
    const currentClose = closeData[i].y;

    if (highestHigh === lowestLow) {
      rawKValues[i] = { x: closeData[i].x, y: 50 }; // Handle division by zero, common practice is 50 or previous value
    } else {
      rawKValues[i] = { x: closeData[i].x, y: 100 * (currentClose - lowestLow) / (highestHigh - lowestLow) };
    }
  }

  // Smooth Raw %K to get Slow %K
   // Need a simple SMA function for smoothing K and calculating D
  const sma = (data: { x: number, y: number | null }[], period: number): { x: number, y: number | null }[] => {
    if (!data) return [];
    const result: { x: number, y: number | null }[] = new Array(data.length).fill(null).map((_, i)=> ({ x: data[i]?.x ?? 0, y: null}));
    for (let i = period -1; i < data.length; i++) {
        let sum = 0;
        let count = 0;
        for (let j=0; j < period; j++) {
            if (data[i-j]?.y !== null) {
                sum += data[i-j].y as number;
                count++;
            }
        }
        if (count > 0) {
           result[i] = { x: data[i].x, y: sum / count };
        }
    }
    return result;
  };

  const slowKValues = sma(rawKValues, smoothK);

  // Calculate Slow %D (SMA of Slow %K)
  const slowDValues = sma(slowKValues, dPeriod);

  return { percentK: slowKValues, percentD: slowDValues };
};

// --- Helper Function for William %R ---
const calculateWilliamPercentR = (
  highData: number[],
  lowData: number[],
  closeData: { x: number, y: number }[],
  period: number = 14
): { x: number, y: number | null }[] => {
  if (!highData || !lowData || !closeData || highData.length < period || highData.length !== lowData.length || highData.length !== closeData.length) {
      return new Array(highData?.length ?? 0).fill(null).map((_, i) => ({ x: closeData[i]?.x ?? 0, y: null }));
  }

  const williamRValues: { x: number, y: number | null }[] = new Array(highData.length).fill(null);

  for (let i = period - 1; i < highData.length; i++) {
    const sliceHigh = highData.slice(i - period + 1, i + 1);
    const sliceLow = lowData.slice(i - period + 1, i + 1);
    const highestHigh = Math.max(...sliceHigh);
    const lowestLow = Math.min(...sliceLow);
    const currentClose = closeData[i].y;

    if (highestHigh === lowestLow) {
      williamRValues[i] = { x: closeData[i].x, y: -50 }; // Handle division by zero
    } else {
      williamRValues[i] = { x: closeData[i].x, y: -100 * (highestHigh - currentClose) / (highestHigh - lowestLow) };
    }
  }

  return williamRValues;
};

// --- Helper Function for ROC (Rate of Change) ---
const calculateROC = (
  data: { x: number, y: number }[],
  period: number = 12
): { x: number, y: number | null }[] => {
  if (!data || data.length < period) {
    return new Array(data.length).fill(null).map((_, i) => ({ x: data[i]?.x ?? 0, y: null }));
  }

  const rocValues: { x: number, y: number | null }[] = new Array(data.length).fill(null);

  for (let i = period; i < data.length; i++) {
    const currentClose = data[i].y;
    const pastClose = data[i - period].y;

    if (pastClose === 0) {
      rocValues[i] = { x: data[i].x, y: null }; // Avoid division by zero
    } else {
      rocValues[i] = { x: data[i].x, y: 100 * (currentClose - pastClose) / pastClose };
    }
  }
   // Fill initial nulls
   for (let i = 0; i < period; i++) {
      rocValues[i] = {x: data[i].x, y: null};
   }

  return rocValues;
};

// --- Main Page Component ---
export default function MarketOverviewPage() {
  const [hsiCurrentData] = useState<HsiCurrentData>(mockCurrentData);
  const hsiHistoricalData: HistoricalPoint[] = mockHistoricalData;
  const [chartRegistered, setChartRegistered] = useState(false);
  const [chartType, setChartType] = useState<ChartDisplayType>('candlestick');
  const [interval, setInterval] = useState<Interval>('1D');
  const [duration, setDuration] = useState<Duration>('6M');
  // --- NEW State for main indicators ---
  const [mainIndicatorType, setMainIndicatorType] = useState<MainIndicatorType>('sma');
  const [activePeriods, setActivePeriods] = useState<number[]>([10, 20]);
  // --- NEW State for sub-chart indicators ---
  const [subChart1Indicator, setSubChart1Indicator] = useState<SubIndicatorType>('rsi');
  const [subChart2Indicator, setSubChart2Indicator] = useState<SubIndicatorType>('macd');

  // Refs for charts (optional, for potential future sync)
  const mainChartRef = useRef<ChartJS | null>(null);
  const volumeChartRef = useRef<ChartJS | null>(null);

  // --- Modified useEffect for dynamic imports and registration ---
  useEffect(() => {
    const registerChart = async () => {
      // Dynamically import adapter and plugin
      const { zoomPlugin } = await dynamicImports();

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
  const { mainChartData, volumeChartData, subChart1Data, subChart2Data, timeUnit } = useMemo(() => {
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
    // --- Renamed for clarity ---
    const closeDataForIndicators = filteredData.map(d => ({
         x: 'timestamp' in d ? d.timestamp : new Date(d.time).valueOf(),
         y: d.close
    }));
    // --- Added for SAR ---
    const highDataForSAR = filteredData.map(d => d.high);
    const lowDataForSAR = filteredData.map(d => d.low);
    const timestampsForSAR = filteredData.map(d => 'timestamp' in d ? d.timestamp : new Date(d.time).valueOf());

    // 4. Calculate SMAs (using potentially fewer points for intraday)
    const sma10Data = calculateSMA(closeDataForIndicators, 10);
    const sma20Data = calculateSMA(closeDataForIndicators, 20);

    // Calculate RSI
    const rsiData = calculateRSI(closeDataForIndicators, 14); 

    // Calculate MACD
    const { macdLine, signalLine, histogram } = calculateMACD(closeDataForIndicators);

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

    // --- NEW: Calculate Main Indicator Datasets ---
    const indicatorDatasets: any[] = [];
    const indicatorColors = [ // Define some colors for indicators
      'rgba(255, 159, 64, 1)', // Orange
      'rgba(153, 102, 255, 1)', // Purple
      'rgba(75, 192, 192, 1)',  // Teal
      'rgba(255, 206, 86, 1)',  // Yellow
      'rgba(54, 162, 235, 1)',  // Blue
      'rgba(255, 99, 132, 1)',   // Pink
    ];
    let colorIndex = 0;

    if (mainIndicatorType !== 'sar') { // SAR is handled differently (plotted as points usually)
        activePeriods.forEach(period => {
            const periodColor = indicatorColors[colorIndex % indicatorColors.length];
            colorIndex++;
            let calculatedData;

            switch (mainIndicatorType) {
                case 'sma':
                    calculatedData = calculateSMA(closeDataForIndicators, period);
                    indicatorDatasets.push({ type: 'line' as const, label: `SMA(${period})`, data: calculatedData, borderColor: periodColor, borderWidth: 1, pointRadius: 0, yAxisID: 'yPrice', tension: 0.1 });
                    break;
                case 'wma':
                    calculatedData = calculateWMA(closeDataForIndicators, period);
                    indicatorDatasets.push({ type: 'line' as const, label: `WMA(${period})`, data: calculatedData, borderColor: periodColor, borderWidth: 1, pointRadius: 0, yAxisID: 'yPrice', tension: 0.1 });
                    break;
                case 'ema':
                    calculatedData = calculateEMA(closeDataForIndicators, period);
                    indicatorDatasets.push({ type: 'line' as const, label: `EMA(${period})`, data: calculatedData, borderColor: periodColor, borderWidth: 1, pointRadius: 0, yAxisID: 'yPrice', tension: 0.1 });
                    break;
                case 'bollinger':
                    const { upper, middle, lower } = calculateBollingerBands(closeDataForIndicators, period);
                    // Middle Band (often same as SMA)
                    indicatorDatasets.push({ type: 'line' as const, label: `BB Mid(${period})`, data: middle, borderColor: periodColor, borderWidth: 1, borderDash: [5, 5], pointRadius: 0, yAxisID: 'yPrice', tension: 0.1 });
                    // Upper Band
                    indicatorDatasets.push({ type: 'line' as const, label: `BB Upper(${period})`, data: upper, borderColor: indicatorColors[colorIndex % indicatorColors.length], borderWidth: 1, pointRadius: 0, yAxisID: 'yPrice', tension: 0.1, fill: false }); // Don't fill upper/lower by default
                    colorIndex++;
                    // Lower Band
                    indicatorDatasets.push({ type: 'line' as const, label: `BB Lower(${period})`, data: lower, borderColor: indicatorColors[colorIndex % indicatorColors.length], borderWidth: 1, pointRadius: 0, yAxisID: 'yPrice', tension: 0.1, fill: '-1' }); // Fill to previous dataset (upper)
                    colorIndex++;
                    break;
                // SAR handled below
            }
        });
    } else {
        // Calculate and add SAR dataset (plotted as points)
        const sarData = calculateSAR(highDataForSAR, lowDataForSAR, timestampsForSAR);
        indicatorDatasets.push({
            type: 'line' as const, // Use line type but customize points
            label: 'SAR',
            data: sarData,
            borderColor: 'transparent', // Hide the line itself
            backgroundColor: indicatorColors[0], // Color for the points
            pointStyle: 'crossRot', // Style for SAR points
            pointRadius: 3,
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            showLine: false, // Ensure line is not shown
            yAxisID: 'yPrice',
            order: -1 // Try to draw SAR points below candles/bars
        });
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

    // --- NEW: Calculate Sub-Chart Indicators Dynamically ---
    const calculateSubIndicator = (indicatorType: SubIndicatorType) => {
        switch (indicatorType) {
            case 'rsi':
                const rsiData = calculateRSI(closeDataForIndicators, 14);
                return { datasets: [{ type: 'line' as const, label: 'RSI(14)', data: rsiData, borderColor: 'rgba(255, 99, 132, 1)', backgroundColor: 'rgba(255, 99, 132, 0.1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yRsi', tension: 0.1 }] };
            case 'macd':
                const { macdLine, signalLine, histogram } = calculateMACD(closeDataForIndicators);
                 const macdLineDataset = { type: 'line' as const, label: 'MACD', data: macdLine, borderColor: 'rgba(54, 162, 235, 1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yMacd', tension: 0.1 };
                 const signalLineDataset = { type: 'line' as const, label: 'Signal', data: signalLine, borderColor: 'rgba(255, 99, 132, 1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yMacd', tension: 0.1 };
                 const histogramDataset = { type: 'bar' as const, label: 'Histogram', data: histogram, backgroundColor: histogram.map(d => d.y !== null ? (d.y >= 0 ? 'rgba(75, 192, 192, 0.5)' : 'rgba(255, 99, 132, 0.5)') : 'transparent'), borderColor: histogram.map(d => d.y !== null ? (d.y >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)') : 'transparent'), borderWidth: 1, yAxisID: 'yMacd' };
                return { datasets: [histogramDataset, macdLineDataset, signalLineDataset] };
            case 'slow_stc':
                const { percentK, percentD } = calculateSlowSTC(highDataForSAR, lowDataForSAR, closeDataForIndicators);
                const kDataset = { type: 'line' as const, label: '%K (Slow)', data: percentK, borderColor: 'rgba(54, 162, 235, 1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yStc', tension: 0.1 };
                const dDataset = { type: 'line' as const, label: '%D (Slow)', data: percentD, borderColor: 'rgba(255, 159, 64, 1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yStc', tension: 0.1 };
                return { datasets: [kDataset, dDataset] };
            case 'william_r':
                const williamRData = calculateWilliamPercentR(highDataForSAR, lowDataForSAR, closeDataForIndicators);
                return { datasets: [{ type: 'line' as const, label: 'William %R(14)', data: williamRData, borderColor: 'rgba(153, 102, 255, 1)', backgroundColor: 'rgba(153, 102, 255, 0.1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yWilliamR', tension: 0.1 }] };
            case 'roc':
                const rocData = calculateROC(closeDataForIndicators);
                return { datasets: [{ type: 'line' as const, label: 'ROC(12)', data: rocData, borderColor: 'rgba(75, 192, 192, 1)', backgroundColor: 'rgba(75, 192, 192, 0.1)', borderWidth: 1, pointRadius: 0, yAxisID: 'yRoc', tension: 0.1 }] };
             case 'volume':
                 return { datasets: [volumeDataset] }; // Reuse calculated volume data
            default:
                return { datasets: [] }; // Return empty for unhandled types
        }
    };

    const subChart1Result = calculateSubIndicator(subChart1Indicator);
    const subChart2Result = calculateSubIndicator(subChart2Indicator);

    // 8. Return structured data including sub-chart results
    return {
      mainChartData: { datasets: [priceDataset, ...indicatorDatasets] },
      volumeChartData: { datasets: [volumeDataset] },
      subChart1Data: subChart1Result,
      subChart2Data: subChart2Result,
      timeUnit: calculatedTimeUnit
    };
  }, [
      hsiHistoricalData, mockIntradayData, chartType, interval, duration, 
      mainIndicatorType, activePeriods, 
      subChart1Indicator, subChart2Indicator // Add new dependencies
  ]);

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
        labels: {
            boxWidth: 12,
            font: { size: 10 },
            filter: (item: LegendItem) => {
                if (item.text && (item.text.startsWith('HSI') || item.datasetIndex === 0)) return true;
                const indicatorPrefixes = ['SMA(', 'WMA(', 'EMA(', 'BB ', 'SAR'];
                return item.text ? indicatorPrefixes.some(prefix => item.text?.startsWith(prefix)) : false;
            }
        }
      },
      title: {
        display: true, 
        text: `恆生指數 ${chartType.toUpperCase()} (模擬數據)`, 
        font: { size: 16 } 
      },
    },
    scales: {
      ...commonOptions.scales,
      x: { ...commonOptions.scales.x, ticks: { ...commonOptions.scales.x?.ticks, display: false } }, // Hide X ticks on main chart
      yPrice: { type: 'linear' as const, display: true, position: 'left' as const, grid: { color: 'rgba(200, 200, 200, 0.2)' }, title: { display: true, text: '指數' } },
    }
  }), [commonOptions, chartType, timeUnit, mainIndicatorType, activePeriods]);

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

  // --- NEW: Function to get Sub-Chart Options --- 
  const getSubChartOptions = (indicatorType: SubIndicatorType): ChartOptions => {
      let yAxisID: string;
      let titleText: string;
      let yAxisOptions: any = {}; // Use 'any' for flexibility or define a stricter type
      let legendFilter: ((item: LegendItem) => boolean) | undefined = undefined;
      let showLegend = false;

      switch (indicatorType) {
          case 'rsi':
              yAxisID = 'yRsi';
              titleText = 'RSI(14)';
              yAxisOptions = { min: 0, max: 100 };
              break;
          case 'macd':
              yAxisID = 'yMacd';
              titleText = 'MACD';
              showLegend = true;
              legendFilter = (item: LegendItem) => item.text !== 'Histogram';
              break;
          case 'slow_stc':
              yAxisID = 'yStc';
              titleText = 'Slow STC(14,3,3)';
              yAxisOptions = { min: 0, max: 100 };
              showLegend = true; // Show %K and %D legend
              break;
          case 'william_r':
               yAxisID = 'yWilliamR';
               titleText = 'William %R(14)';
               yAxisOptions = { min: -100, max: 0 };
               break;
           case 'roc':
               yAxisID = 'yRoc';
               titleText = 'ROC(12)';
               // yAxisOptions can be left default or set based on data range if needed
               break;
            case 'volume':
                yAxisID = 'yVolume';
                titleText = '成交量';
                yAxisOptions = { // Copy relevant volume axis options
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
                        maxTicksLimit: 5
                    }
                };
                break;
          default:
              yAxisID = 'yDefaultSub';
              titleText = 'Indicator';
              break;
      }

    // Use useMemo inside for performance, but dependencies are tricky here.
    // For simplicity, constructing options directly. Consider memoization if performance issues arise.
     return {
        ...commonOptions,
        plugins: {
          ...commonOptions.plugins,
          legend: { 
              display: showLegend, // Control legend visibility 
              position: 'top' as const, 
              labels: { 
                  boxWidth: 10, 
                  font: { size: 10 },
                  filter: legendFilter // Apply specific legend filter inside labels
              },
          }, 
          title: { display: false }, // Sub-charts usually don't need a big title 
        },
        scales: {
            x: { 
                ...commonOptions.scales.x,
                ticks: { 
                    ...commonOptions.scales.x?.ticks,
                     // Show X ticks only on the last sub-chart
                    display: true // Needs logic to determine if it's the last chart
                } 
            },
            [yAxisID]: { // Dynamic Y-axis based on indicator
                type: 'linear' as const, 
                display: true, 
                position: 'left' as const, 
                grid: { drawOnChartArea: false }, 
                ticks: { maxTicksLimit: 5, ...yAxisOptions.ticks }, // Merge general and specific ticks
                title: { display: true, text: titleText },
                 ...yAxisOptions // Spread other Y-axis options like min/max
            }
        }
      };
  };

  // Updated function to get button style, accepting a generic type T
  const getButtonStyle = <T extends string>(currentValue: T, targetValue: T) => {
    return `px-3 py-1 rounded mr-2 text-sm ${currentValue === targetValue 
      ? 'bg-blue-600 text-white' 
      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`;
  };

  // --- NEW: Handler for toggling active periods ---
  const handlePeriodToggle = (period: number) => {
    setActivePeriods(prev =>
      prev.includes(period)
        ? prev.filter(p => p !== period) // Remove if exists
        : [...prev, period] // Add if doesn't exist
    );
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

         {/* --- NEW: Main Indicator Controls --- */}
         <div className="flex flex-col md:flex-row flex-wrap gap-y-2 mb-4 items-center border-t pt-4 mt-4">
            {/* Indicator Type Dropdown */}
            <div className="mr-4 mb-2 md:mb-0">
                 <label htmlFor="mainIndicatorSelect" className="text-sm font-medium mr-2">主圖指標:</label>
                 <select
                    id="mainIndicatorSelect"
                    value={mainIndicatorType}
                    onChange={(e) => setMainIndicatorType(e.target.value as MainIndicatorType)}
                    className="p-1 border rounded text-sm bg-gray-50"
                 >
                    {Object.entries(indicatorLabels).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                    ))}
                 </select>
            </div>

            {/* Indicator Period Buttons */}
             {mainIndicatorType !== 'sar' && ( // SAR doesn't use periods in this implementation
                 <div>
                     <span className="text-sm font-medium mr-2">週期:</span>
                     {availablePeriods.map(period => (
                         <button
                             key={period}
                             className={`px-2 py-1 rounded mr-2 text-xs ${activePeriods.includes(period)
                                 ? 'bg-indigo-600 text-white'
                                 : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
                             onClick={() => handlePeriodToggle(period)}
                         >
                             {period}
                         </button>
                     ))}
                 </div>
             )}
         </div>

        {/* --- NEW: Sub-Chart Controls --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 border-t pt-4 mt-4">
            <div>
                <label htmlFor="subChart1Select" className="text-sm font-medium mr-2">副圖一 指標:</label>
                <select
                    id="subChart1Select"
                    value={subChart1Indicator}
                    onChange={(e) => setSubChart1Indicator(e.target.value as SubIndicatorType)}
                    className="p-1 border rounded text-sm bg-gray-50 w-full md:w-auto"
                >
                    {Object.entries(subIndicatorLabels).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                    ))}
                </select>
            </div>
             <div>
                <label htmlFor="subChart2Select" className="text-sm font-medium mr-2">副圖二 指標:</label>
                <select
                    id="subChart2Select"
                    value={subChart2Indicator}
                    onChange={(e) => setSubChart2Indicator(e.target.value as SubIndicatorType)}
                    className="p-1 border rounded text-sm bg-gray-50 w-full md:w-auto"
                >
                    {Object.entries(subIndicatorLabels).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                    ))}
                </select>
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

         {/* --- NEW: Sub Chart 1 Container --- */}
         <div className="relative h-[100px] mb-1">
            {chartRegistered && subChart1Data?.datasets?.length > 0 ? (
                <DynamicChart 
                   type={subChart1Indicator === 'macd' || subChart1Indicator === 'volume' ? 'bar' : 'line'} // Adjust base type
                   data={subChart1Data}
                   options={getSubChartOptions(subChart1Indicator) as ChartOptions}
                 />
            ) : (
               <p>Loading {subIndicatorLabels[subChart1Indicator]} chart...</p>
             )}
         </div>

         {/* --- NEW: Sub Chart 2 Container --- */}
         <div className="relative h-[100px]">
            {chartRegistered && subChart2Data?.datasets?.length > 0 ? (
                <DynamicChart 
                   type={subChart2Indicator === 'macd' || subChart2Indicator === 'volume' ? 'bar' : 'line'} // Adjust base type
                   data={subChart2Data}
                   options={getSubChartOptions(subChart2Indicator) as ChartOptions} // Apply options based on selection
                 />
            ) : (
               <p>Loading {subIndicatorLabels[subChart2Indicator]} chart...</p>
             )}
         </div>
      </div>

    </div>
  );
} 