"""
技術指標計算單元測試
測試布林帶等技術指標的計算是否正確
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 導入被測試模組
from backend.app.services.indicators import bollinger_bands


class TestBollingerBands:
    """布林帶指標測試類"""
    
    @pytest.fixture
    def sample_data(self):
        """創建測試用的價格數據"""
        # 創建一個包含 20 個交易日收盤價的 DataFrame
        prices = [
            100, 101, 102, 103, 104,  # 上升趨勢
            105, 104, 103, 102, 101,  # 下降趨勢
            100, 101, 102, 103, 104,  # 上升趨勢
            103, 102, 101, 100, 99    # 下降趨勢
        ]
        dates = pd.date_range(start="2024-01-01", periods=len(prices), freq="B")
        df = pd.DataFrame({"close": prices}, index=dates)
        return df
    
    def test_bollinger_bands_columns(self, sample_data):
        """測試布林帶計算結果包含必要的欄位"""
        # 執行布林帶計算
        result = bollinger_bands(sample_data, period=5, std_dev=2)
        
        # 檢查是否包含必要的欄位
        assert "bb_middle" in result.columns, "結果缺少 bb_middle 欄位"
        assert "bb_upper" in result.columns, "結果缺少 bb_upper 欄位"
        assert "bb_lower" in result.columns, "結果缺少 bb_lower 欄位"
        assert "bb_width" in result.columns, "結果缺少 bb_width 欄位"
    
    def test_bollinger_bands_values(self, sample_data):
        """測試布林帶計算結果的值類型和邏輯關係"""
        # 執行布林帶計算
        result = bollinger_bands(sample_data, period=5, std_dev=2)
        
        # 跳過前 period-1 行，因為它們包含 NaN 值
        non_na_results = result.iloc[4:].dropna()
        
        # 檢查值類型是浮點數
        assert non_na_results["bb_middle"].dtype == float, "bb_middle 應該是浮點數"
        assert non_na_results["bb_upper"].dtype == float, "bb_upper 應該是浮點數"
        assert non_na_results["bb_lower"].dtype == float, "bb_lower 應該是浮點數"
        assert non_na_results["bb_width"].dtype == float, "bb_width 應該是浮點數"
        
        # 檢查邏輯關係
        assert (non_na_results["bb_upper"] > non_na_results["bb_middle"]).all(), "上軌應大於中軌"
        assert (non_na_results["bb_middle"] > non_na_results["bb_lower"]).all(), "中軌應大於下軌"
        assert (non_na_results["bb_upper"] > non_na_results["bb_lower"]).all(), "上軌應大於下軌"
    
    def test_bollinger_bands_calculations(self, sample_data):
        """測試布林帶計算公式是否正確"""
        period = 5
        std_dev = 2
        
        # 手動計算布林帶
        sma = sample_data["close"].rolling(window=period).mean()
        std = sample_data["close"].rolling(window=period).std()
        expected_upper = sma + (std * std_dev)
        expected_lower = sma - (std * std_dev)
        expected_width = (expected_upper - expected_lower) / sma
        
        # 使用函數計算布林帶
        result = bollinger_bands(sample_data, period=period, std_dev=std_dev)
        
        # 驗證計算結果是否與預期相符
        pd.testing.assert_series_equal(
            result["bb_middle"].round(8), 
            sma.round(8), 
            check_names=False
        )
        pd.testing.assert_series_equal(
            result["bb_upper"].round(8), 
            expected_upper.round(8), 
            check_names=False
        )
        pd.testing.assert_series_equal(
            result["bb_lower"].round(8), 
            expected_lower.round(8), 
            check_names=False
        )
        pd.testing.assert_series_equal(
            result["bb_width"].round(8), 
            expected_width.round(8), 
            check_names=False
        )
    
    def test_custom_column(self, sample_data):
        """測試自定義列名參數"""
        # 添加一個 high 列
        sample_data["high"] = sample_data["close"] * 1.01
        
        # 使用 high 列計算布林帶
        result = bollinger_bands(sample_data, period=5, std_dev=2, column="high")
        
        # 檢查是否使用了 high 列進行計算
        # 布林帶中軌應該接近 high 列的移動平均
        expected_middle = sample_data["high"].rolling(window=5).mean()
        pd.testing.assert_series_equal(
            result["bb_middle"].round(8), 
            expected_middle.round(8), 
            check_names=False
        )
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 測試非 DataFrame 輸入
        with pytest.raises(TypeError):
            bollinger_bands([1, 2, 3, 4, 5])
        
        # 測試缺少必要列的 DataFrame
        df_without_close = pd.DataFrame({"open": [1, 2, 3, 4, 5]})
        with pytest.raises(ValueError):
            bollinger_bands(df_without_close)


if __name__ == "__main__":
    pytest.main(["-v", __file__]) 