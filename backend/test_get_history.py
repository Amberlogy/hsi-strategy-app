#!/usr/bin/env python
"""
測試 get_hsi_history 函數

此腳本用於測試 source_aastocks.py 中的 get_hsi_history 函數
"""

import sys
from datetime import datetime, timedelta
import pandas as pd

# 添加項目根目錄到 Python 路徑
sys.path.append('.')

# 導入 get_hsi_history 函數
from app.data.source_aastocks import get_hsi_history

def main():
    """測試 get_hsi_history 函數並顯示結果"""
    print("\n===== 測試 get_hsi_history 函數 =====")
    
    # 測試1: 默認參數
    print("\n== 測試1: 使用默認參數 ==")
    df1 = get_hsi_history()
    print(f"生成的數據行數: {len(df1)}")
    print(df1.head())
    
    # 測試2: 指定日期範圍 (短期)
    print("\n== 測試2: 指定短期日期範圍 (一個月) ==")
    today = datetime.now()
    one_month_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    df2 = get_hsi_history("HSI", one_month_ago, today_str)
    print(f"時間範圍: {one_month_ago} 至 {today_str}")
    print(f"生成的數據行數: {len(df2)}")
    print(df2.head())
    
    # 測試3: 指定日期範圍 (長期)
    print("\n== 測試3: 指定長期日期範圍 (一年) ==")
    one_year_ago = (today - timedelta(days=365)).strftime('%Y-%m-%d')
    df3 = get_hsi_history("HSI", one_year_ago, today_str)
    print(f"時間範圍: {one_year_ago} 至 {today_str}")
    print(f"生成的數據行數: {len(df3)}")
    print(df3.head())
    
    # 測試4: 不同的股票代碼
    print("\n== 測試4: 使用不同的股票代碼 ==")
    stocks = ["00001", "00700", "HSI"]
    for stock in stocks:
        df4 = get_hsi_history(stock, '2024-01-01', '2024-01-10')
        print(f"\n股票代碼: {stock}")
        print(f"生成的數據行數: {len(df4)}")
        print(f"第一天開盤價: {df4.iloc[0]['open']:.2f}, 收盤價: {df4.iloc[0]['close']:.2f}")
        print(f"最後一天開盤價: {df4.iloc[-1]['open']:.2f}, 收盤價: {df4.iloc[-1]['close']:.2f}")
    
    # 測試5: 數據統計
    print("\n== 測試5: 數據統計 ==")
    df5 = get_hsi_history("HSI", '2024-01-01', '2024-06-30')
    print(f"時間範圍: 2024-01-01 至 2024-06-30")
    print(f"生成的數據行數: {len(df5)}")
    print("\n數據統計:")
    print(df5.describe())
    
    # 測試6: 簡單分析
    print("\n== 測試6: 簡單分析 ==")
    df6 = get_hsi_history("HSI", '2024-01-01', '2024-06-30')
    
    # 計算每日回報率
    df6['return'] = df6['close'].pct_change() * 100
    
    # 顯示統計信息
    print("\n日回報率統計 (%):")
    print(df6['return'].describe())
    
    # 計算累積回報率
    cumulative_return = ((df6['close'].iloc[-1] / df6['close'].iloc[0]) - 1) * 100
    print(f"\n累積回報率: {cumulative_return:.2f}%")
    
    # 找出交易量最大的日子
    max_volume_day = df6.loc[df6['volume'].idxmax()]
    print("\n交易量最大的日子:")
    print(f"日期: {max_volume_day['date'].strftime('%Y-%m-%d')}")
    print(f"交易量: {max_volume_day['volume']}")
    print(f"開盤價: {max_volume_day['open']:.2f}, 收盤價: {max_volume_day['close']:.2f}")

if __name__ == "__main__":
    main() 