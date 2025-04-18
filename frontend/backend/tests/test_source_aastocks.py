#!/usr/bin/env python
"""
測試 source_aastocks.py 的模擬資料生成函數

此檔案包含對 get_hsi_history 函數的測試，確保其正確回傳 DataFrame 並含有適當的資料
"""

import unittest
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 將專案根目錄添加到 Python 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入要測試的函數
from app.data.source_aastocks import get_hsi_history


class TestSourceAastocks(unittest.TestCase):
    """測試 source_aastocks.py 中的函數"""
    
    def test_get_hsi_history_return_type(self):
        """測試 get_hsi_history 回傳的是否為 DataFrame"""
        result = get_hsi_history()
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_get_hsi_history_columns(self):
        """測試 DataFrame 是否包含必要的欄位"""
        result = get_hsi_history()
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        for column in required_columns:
            self.assertIn(column, result.columns)
    
    def test_get_hsi_history_default_range(self):
        """測試使用默認參數時的資料範圍"""
        result = get_hsi_history()
        # 默認獲取過去 90 天的數據
        today = datetime.now()
        ninety_days_ago = today - timedelta(days=90)
        
        # 把 dataframe 的 date 轉成 datetime 格式進行比較
        result['date'] = pd.to_datetime(result['date'])
        
        # 檢查第一筆資料的日期是否接近 90 天前
        # 考慮週末，允許有 5 天的誤差
        earliest_date = result['date'].min()
        self.assertLessEqual(abs((earliest_date - ninety_days_ago).days), 5)
        
        # 檢查最後一筆資料的日期是否接近今天
        latest_date = result['date'].max()
        self.assertLessEqual((today - latest_date).days, 5)
    
    def test_get_hsi_history_specific_date_range(self):
        """測試指定日期範圍"""
        start_date = '2024-01-01'
        end_date = '2024-01-31'
        
        result = get_hsi_history('HSI', start_date, end_date)
        
        # 計算工作日數量 (排除週末)
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        business_days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # 0-4 是週一至週五
                business_days += 1
            current += timedelta(days=1)
        
        # 檢查資料筆數是否與工作日數相近 (允許有 2 天誤差，考慮節假日)
        self.assertLessEqual(abs(len(result) - business_days), 2)
        
        # 檢查資料日期範圍
        result['date'] = pd.to_datetime(result['date'])
        self.assertGreaterEqual(result['date'].min(), datetime.strptime(start_date, '%Y-%m-%d'))
        self.assertLessEqual(result['date'].max(), datetime.strptime(end_date, '%Y-%m-%d'))
    
    def test_get_hsi_history_data_values(self):
        """測試資料值是否合理"""
        result = get_hsi_history('HSI')
        
        # 檢查是否有缺失值
        self.assertEqual(result.isnull().sum().sum(), 0)
        
        # HSI 的合理範圍檢查 (開高低收價)
        # 恆生指數通常在 15,000 - 35,000 之間
        self.assertGreaterEqual(result['open'].min(), 10000)
        self.assertLessEqual(result['open'].max(), 40000)
        self.assertGreaterEqual(result['high'].min(), 10000)
        self.assertLessEqual(result['high'].max(), 40000)
        self.assertGreaterEqual(result['low'].min(), 10000)
        self.assertLessEqual(result['low'].max(), 40000)
        self.assertGreaterEqual(result['close'].min(), 10000)
        self.assertLessEqual(result['close'].max(), 40000)
        
        # 確保 high 永遠 >= open, close, low
        self.assertTrue((result['high'] >= result['open']).all())
        self.assertTrue((result['high'] >= result['close']).all())
        self.assertTrue((result['high'] >= result['low']).all())
        
        # 確保 low 永遠 <= open, close, high
        self.assertTrue((result['low'] <= result['open']).all())
        self.assertTrue((result['low'] <= result['close']).all())
        self.assertTrue((result['low'] <= result['high']).all())
        
        # 檢查交易量是否為正數
        self.assertTrue((result['volume'] > 0).all())
    
    def test_get_hsi_history_different_symbols(self):
        """測試不同股票代碼"""
        # 測試恆生指數
        hsi_result = get_hsi_history('HSI', '2024-01-01', '2024-01-10')
        
        # 測試其他股票
        stock_result = get_hsi_history('00700', '2024-01-01', '2024-01-10')  # 騰訊
        
        # 兩者都應該返回 DataFrame
        self.assertIsInstance(hsi_result, pd.DataFrame)
        self.assertIsInstance(stock_result, pd.DataFrame)
        
        # 兩者的資料筆數應該相近 (工作日數相同)
        self.assertLessEqual(abs(len(hsi_result) - len(stock_result)), 1)
        
        # 價格範圍應該不同 (恆生指數通常是萬位數，股票通常是十到千位數)
        self.assertGreater(hsi_result['close'].mean(), 10000)  # 恆指應該大於 10000
        self.assertLess(stock_result['close'].mean(), 10000)   # 個股通常小於 10000
    
    def test_get_hsi_history_invalid_dates(self):
        """測試無效日期範圍（結束日期早於開始日期）"""
        with self.assertRaises(ValueError):
            get_hsi_history('HSI', '2024-02-01', '2024-01-01')


if __name__ == '__main__':
    unittest.main() 