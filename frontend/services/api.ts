const API_BASE_URL = '/api/trade';

export interface SimulateParams {
  start_date: string;
  end_date: string;
  strategy_name?: string;
  short_period?: number;
  long_period?: number;
  ma_type?: 'sma' | 'ema';
  initial_cash?: number;
}

export interface TradeRecord {
  timestamp: string;
  type: 'buy' | 'sell';
  price: number;
  quantity: number;
}

export interface StrategyPerformance {
  total_return: number;
  max_drawdown: number;
  win_rate: number;
  trade_count: number;
}

export interface SimulatorStatus {
  cash: number;
  positions: Record<string, number>;
  trade_log: TradeRecord[];
  performance: StrategyPerformance;
}

export async function getSimulatorStatus(): Promise<SimulatorStatus> {
  const response = await fetch(`${API_BASE_URL}/simulator/status`);
  if (!response.ok) {
    throw new Error('Failed to fetch simulator status');
  }
  return response.json();
}

export async function simulateStrategy(params: SimulateParams): Promise<any> {
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      queryParams.append(key, value.toString());
    }
  });

  const response = await fetch(`${API_BASE_URL}/simulator/simulate?${queryParams}`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Strategy simulation failed');
  }

  return response.json();
}