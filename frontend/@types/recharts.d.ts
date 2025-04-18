declare module 'recharts' {
  export interface LineProps {
    type?: 'basis' | 'basisClosed' | 'basisOpen' | 'linear' | 'linearClosed' | 'natural' | 'monotoneX' | 'monotoneY' | 'monotone' | 'step' | 'stepBefore' | 'stepAfter';
    dataKey: string;
    stroke?: string;
    name?: string;
  }

  export interface ResponsiveContainerProps {
    width?: string | number;
    height?: string | number;
    children?: React.ReactNode;
  }

  export interface LineChartProps {
    data?: any[];
    children?: React.ReactNode;
  }

  export interface CartesianGridProps {
    strokeDasharray?: string;
  }

  export interface XAxisProps {
    dataKey?: string;
  }

  export interface YAxisProps {}

  export interface TooltipProps {}

  export interface LegendProps {}

  export const LineChart: React.FC<LineChartProps>;
  export const Line: React.FC<LineProps>;
  export const ResponsiveContainer: React.FC<ResponsiveContainerProps>;
  export const CartesianGrid: React.FC<CartesianGridProps>;
  export const XAxis: React.FC<XAxisProps>;
  export const YAxis: React.FC<YAxisProps>;
  export const Tooltip: React.FC<TooltipProps>;
  export const Legend: React.FC<LegendProps>;
}
