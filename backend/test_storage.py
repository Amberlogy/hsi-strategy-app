#!/usr/bin/env python
"""
測試 storage.py 資料持久化模組

此腳本用於測試 app.data.storage 模組提供的資料庫儲存和讀取功能
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加項目根目錄到 Python 路徑
sys.path.append('.')

# 導入儲存模組
from app.data.storage import (
    save_to_db, 
    load_from_db, 
    save_hsi_data, 
    load_hsi_data,
    get_available_tables
)

# 導入資料模擬模組
from app.data.source_aastocks import get_hsi_history

def test_basic_storage():
    """測試基本的儲存和讀取功能"""
    print("\n===== 測試基本儲存和讀取功能 =====")
    
    # 創建測試資料
    test_data = {
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'value': [100, 101, 102],
        'category': ['A', 'B', 'A']
    }
    df = pd.DataFrame(test_data)
    
    # 測試資料庫路徑
    test_db_path = os.path.join('data', 'test_db.db')
    
    # 確保測試目錄存在
    os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
    
    # 刪除測試資料庫（如果存在）
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    print(f"測試數據: \n{df}\n")
    
    # 測試儲存功能
    save_result = save_to_db(df, 'test_table', test_db_path)
    print(f"儲存結果: {save_result}")
    
    # 驗證儲存是否成功
    if os.path.exists(test_db_path):
        print(f"測試資料庫已成功創建: {test_db_path}")
    else:
        print(f"錯誤: 測試資料庫未創建: {test_db_path}")
        return
    
    # 測試讀取功能
    loaded_df = load_from_db('test_table', test_db_path)
    print(f"讀取結果: \n{loaded_df}\n")
    
    # 驗證讀取是否成功
    if len(loaded_df) == len(df):
        print("✓ 讀取的數據行數與原始數據相同")
    else:
        print(f"✗ 讀取的數據行數與原始數據不同: {len(loaded_df)} != {len(df)}")
    
    # 測試自定義查詢
    query = "SELECT * FROM test_table WHERE category = :category"
    params = {'category': 'A'}
    filtered_df = load_from_db('test_table', test_db_path, query, params)
    print(f"自定義查詢結果 (category='A'): \n{filtered_df}\n")
    
    # 驗證查詢結果
    if len(filtered_df) == 2:  # 應該有兩行 category 為 'A'
        print("✓ 自定義查詢結果正確")
    else:
        print(f"✗ 自定義查詢結果不正確: {len(filtered_df)} != 2")
    
    # 測試獲取資料表列表
    tables = get_available_tables(test_db_path)
    print(f"資料庫中的資料表: {tables}")
    
    # 清理測試資料庫
    try:
        os.remove(test_db_path)
        print(f"已刪除測試資料庫: {test_db_path}")
    except OSError:
        print(f"無法刪除測試資料庫: {test_db_path}")

def test_hsi_data_storage():
    """測試恆生指數數據的儲存和讀取功能"""
    print("\n===== 測試恆生指數數據儲存和讀取功能 =====")
    
    # 獲取恆生指數歷史數據
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    print(f"獲取恆生指數數據，日期範圍: {start_date} 至 {end_date}")
    hsi_df = get_hsi_history("HSI", start_date, end_date)
    
    if hsi_df.empty:
        print("錯誤: 獲取的恆生指數數據為空")
        return
    
    print(f"獲取了 {len(hsi_df)} 行恆生指數數據")
    print(f"數據樣本: \n{hsi_df.head(3)}\n")
    
    # 測試資料庫路徑
    test_db_path = os.path.join('data', 'test_hsi.db')
    
    # 確保測試目錄存在
    os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
    
    # 刪除測試資料庫（如果存在）
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # 測試儲存功能
    save_result = save_hsi_data(hsi_df, test_db_path)
    print(f"儲存結果: {save_result}")
    
    # 驗證儲存是否成功
    if os.path.exists(test_db_path):
        print(f"測試資料庫已成功創建: {test_db_path}")
    else:
        print(f"錯誤: 測試資料庫未創建: {test_db_path}")
        return
    
    # 測試讀取功能 - 讀取所有數據
    loaded_df = load_hsi_data(db_path=test_db_path)
    print(f"讀取結果: {len(loaded_df)} 行數據")
    print(f"數據樣本: \n{loaded_df.head(3)}\n")
    
    # 驗證讀取是否成功
    if len(loaded_df) == len(hsi_df):
        print("✓ 讀取的數據行數與原始數據相同")
    else:
        print(f"✗ 讀取的數據行數與原始數據不同: {len(loaded_df)} != {len(hsi_df)}")
    
    # 測試日期範圍查詢
    test_start_date = (today - timedelta(days=15)).strftime("%Y-%m-%d")
    print(f"測試日期範圍查詢: {test_start_date} 至 {end_date}")
    
    filtered_df = load_hsi_data(test_start_date, end_date, test_db_path)
    print(f"日期範圍查詢結果: {len(filtered_df)} 行數據")
    
    # 清理測試資料庫
    try:
        os.remove(test_db_path)
        print(f"已刪除測試資料庫: {test_db_path}")
    except OSError:
        print(f"無法刪除測試資料庫: {test_db_path}")

def test_real_storage():
    """測試實際應用中的儲存功能"""
    print("\n===== 測試實際應用中的儲存功能 =====")
    
    # 獲取恆生指數歷史數據
    today = datetime.now()
    start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    print(f"獲取恆生指數數據，日期範圍: {start_date} 至 {end_date}")
    hsi_df = get_hsi_history("HSI", start_date, end_date)
    
    if hsi_df.empty:
        print("錯誤: 獲取的恆生指數數據為空")
        return
    
    print(f"獲取了 {len(hsi_df)} 行恆生指數數據")
    
    # 使用默認資料庫路徑
    print("使用默認資料庫路徑儲存數據")
    save_result = save_hsi_data(hsi_df)
    print(f"儲存結果: {save_result}")
    
    # 讀取部分數據進行驗證
    test_start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    print(f"讀取最近 30 天的數據: {test_start_date} 至 {end_date}")
    
    recent_df = load_hsi_data(test_start_date, end_date)
    print(f"讀取結果: {len(recent_df)} 行數據")
    
    if not recent_df.empty:
        print(f"最早日期: {recent_df['date'].min()}")
        print(f"最晚日期: {recent_df['date'].max()}")
        
        # 顯示數據統計
        print("\n數據統計:")
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        print(recent_df[numeric_cols].describe())
    else:
        print("讀取的數據為空")

if __name__ == "__main__":
    print("開始測試 storage.py 資料持久化模組")
    
    # 執行測試
    test_basic_storage()
    test_hsi_data_storage()
    
    # 詢問是否要測試實際儲存功能
    response = input("\n是否要測試實際儲存功能 (將寫入實際資料庫)? (y/n): ")
    if response.lower() == 'y':
        test_real_storage()
    
    print("\n測試完成") 