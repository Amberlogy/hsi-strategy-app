#!/usr/bin/env python
"""
測試 daily_update.py 定時更新任務模組

此腳本用於測試 app.tasks.daily_update 模組的更新和數據獲取功能
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加項目根目錄到 Python 路徑
sys.path.append('.')

# 導入測試模組
from app.tasks.daily_update import update_hsi_data, get_latest_hsi_data

def test_update_with_cache_only():
    """測試僅使用 Redis 快取更新數據"""
    print("\n===== 測試僅使用 Redis 快取更新數據 =====")
    
    # 執行更新操作，只使用快取
    success = update_hsi_data(use_db=False, use_cache=True)
    print(f"更新結果: {'成功' if success else '失敗'}")
    
    if success:
        # 獲取最近 3 天的數據，只從快取中讀取
        data = get_latest_hsi_data(3, use_db=False, use_cache=True)
        print(f"獲取到 {len(data)} 天的數據:")
        
        for date, daily_data in sorted(data.items()):
            print(f"日期: {date}, 收盤價: {daily_data['close']}")
    else:
        print("更新失敗，無法進行後續測試")

def test_update_with_db_only():
    """測試僅使用 SQLite 資料庫更新數據"""
    print("\n===== 測試僅使用 SQLite 資料庫更新數據 =====")
    
    # 執行更新操作，只使用資料庫
    success = update_hsi_data(use_db=True, use_cache=False)
    print(f"更新結果: {'成功' if success else '失敗'}")
    
    if success:
        # 獲取最近 3 天的數據，只從資料庫中讀取
        data = get_latest_hsi_data(3, use_db=True, use_cache=False)
        print(f"獲取到 {len(data)} 天的數據:")
        
        for date, daily_data in sorted(data.items()):
            print(f"日期: {date}, 收盤價: {daily_data['close']}")
    else:
        print("更新失敗，無法進行後續測試")

def test_update_with_both():
    """測試同時使用 Redis 快取和 SQLite 資料庫更新數據"""
    print("\n===== 測試同時使用 Redis 快取和 SQLite 資料庫更新數據 =====")
    
    # 執行更新操作，同時使用快取和資料庫
    success = update_hsi_data(use_db=True, use_cache=True)
    print(f"更新結果: {'成功' if success else '失敗'}")
    
    if success:
        # 獲取最近 7 天的數據
        data = get_latest_hsi_data(7, use_db=True, use_cache=True)
        print(f"獲取到 {len(data)} 天的數據:")
        
        # 顯示數據統計
        if data:
            dates = sorted(data.keys())
            print(f"日期範圍: {dates[0]} 至 {dates[-1]}")
            
            # 計算平均價格
            avg_open = sum(data[date]['open'] for date in dates) / len(dates)
            avg_close = sum(data[date]['close'] for date in dates) / len(dates)
            avg_volume = sum(data[date]['volume'] for date in dates) / len(dates)
            
            print(f"平均開盤價: {avg_open:.2f}")
            print(f"平均收盤價: {avg_close:.2f}")
            print(f"平均交易量: {avg_volume:.0f}")
    else:
        print("更新失敗，無法進行後續測試")

def test_data_consistency():
    """測試從快取和資料庫獲取的數據一致性"""
    print("\n===== 測試數據一致性 =====")
    
    # 先更新數據，確保快取和資料庫都有數據
    success = update_hsi_data(use_db=True, use_cache=True)
    if not success:
        print("更新失敗，無法進行一致性測試")
        return
    
    # 獲取最近 5 天的數據，分別從快取和資料庫讀取
    cache_data = get_latest_hsi_data(5, use_db=False, use_cache=True)
    db_data = get_latest_hsi_data(5, use_db=True, use_cache=False)
    
    print(f"從快取獲取到 {len(cache_data)} 天的數據")
    print(f"從資料庫獲取到 {len(db_data)} 天的數據")
    
    # 檢查日期一致性
    cache_dates = set(cache_data.keys())
    db_dates = set(db_data.keys())
    
    common_dates = cache_dates.intersection(db_dates)
    print(f"共同日期數量: {len(common_dates)}")
    
    # 檢查數據一致性
    consistency_count = 0
    for date in common_dates:
        cache_entry = cache_data[date]
        db_entry = db_data[date]
        
        # 比較收盤價是否一致
        if abs(cache_entry['close'] - db_entry['close']) < 0.01:
            consistency_count += 1
    
    if consistency_count == len(common_dates):
        print("✓ 快取和資料庫中的數據完全一致")
    else:
        print(f"✗ 數據不一致: {consistency_count}/{len(common_dates)} 天的數據一致")

if __name__ == "__main__":
    print("開始測試 daily_update.py 定時更新任務模組")
    
    # 詢問要執行的測試
    print("\n請選擇要執行的測試:")
    print("1. 僅使用 Redis 快取更新數據")
    print("2. 僅使用 SQLite 資料庫更新數據")
    print("3. 同時使用 Redis 快取和 SQLite 資料庫更新數據")
    print("4. 測試數據一致性")
    print("5. 執行所有測試")
    
    choice = input("請輸入選項 (1-5): ")
    
    if choice == '1':
        test_update_with_cache_only()
    elif choice == '2':
        test_update_with_db_only()
    elif choice == '3':
        test_update_with_both()
    elif choice == '4':
        test_data_consistency()
    elif choice == '5':
        test_update_with_cache_only()
        test_update_with_db_only()
        test_update_with_both()
        test_data_consistency()
    else:
        print("無效的選項")
    
    print("\n測試完成") 