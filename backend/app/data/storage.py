"""
資料持久化儲存模組

提供將 pandas DataFrame 儲存到 SQLite 資料庫以及從資料庫讀取資料的功能
"""

import os
import logging
import sqlite3
import pandas as pd
from typing import Optional, Union, List, Dict, Any
from datetime import datetime

# 配置日誌
logger = logging.getLogger(__name__)

# 預設資料庫路徑
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hsi_data.db')

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    獲取資料庫連接
    
    Parameters
    ----------
    db_path : str, optional
        資料庫檔案路徑，默認為 `data/hsi_data.db`
        
    Returns
    -------
    sqlite3.Connection
        資料庫連接物件
    """
    # 使用預設路徑或指定的路徑
    db_path = db_path or DEFAULT_DB_PATH
    
    # 確保資料庫目錄存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(db_path)
        logger.debug(f"成功連接到資料庫: {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"連接資料庫時出錯: {str(e)}")
        raise

def save_to_db(
    df: pd.DataFrame, 
    table_name: str, 
    db_path: Optional[str] = None,
    if_exists: str = 'replace',
    index: bool = False
) -> bool:
    """
    將 pandas DataFrame 儲存到 SQLite 資料庫
    
    Parameters
    ----------
    df : pd.DataFrame
        要儲存的資料框
    table_name : str
        資料表名稱
    db_path : str, optional
        資料庫檔案路徑，默認為 `data/hsi_data.db`
    if_exists : str, optional
        如果資料表已存在，執行的操作:
        - 'fail': 引發異常
        - 'replace': 刪除現有表並創建新表
        - 'append': 追加到現有表
        默認為 'replace'
    index : bool, optional
        是否儲存 DataFrame 的索引，默認為 False
        
    Returns
    -------
    bool
        儲存是否成功
    """
    if df.empty:
        logger.warning(f"無法儲存空的 DataFrame 到資料表 {table_name}")
        return False
    
    try:
        # 獲取資料庫連接
        conn = get_db_connection(db_path)
        
        # 儲存 DataFrame 到資料庫
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists=if_exists,
            index=index
        )
        
        # 提交並關閉連接
        conn.commit()
        conn.close()
        
        logger.info(f"成功將 {len(df)} 行資料儲存到資料表 {table_name}")
        return True
    
    except Exception as e:
        logger.error(f"儲存資料到資料表 {table_name} 時出錯: {str(e)}")
        return False

def load_from_db(
    table_name: str, 
    db_path: Optional[str] = None,
    query: Optional[str] = None,
    params: Optional[Union[List, Dict[str, Any]]] = None
) -> pd.DataFrame:
    """
    從 SQLite 資料庫讀取資料到 pandas DataFrame
    
    Parameters
    ----------
    table_name : str
        資料表名稱
    db_path : str, optional
        資料庫檔案路徑，默認為 `data/hsi_data.db`
    query : str, optional
        自訂 SQL 查詢，如果提供，將覆蓋 table_name
    params : list or dict, optional
        SQL 查詢的參數
        
    Returns
    -------
    pd.DataFrame
        包含查詢結果的資料框
    """
    try:
        # 獲取資料庫連接
        conn = get_db_connection(db_path)
        
        # 構建查詢
        if query is None:
            query = f"SELECT * FROM {table_name}"
        
        # 執行查詢並讀取到 DataFrame
        df = pd.read_sql(query, conn, params=params)
        
        # 關閉連接
        conn.close()
        
        logger.info(f"成功從資料表 {table_name} 讀取 {len(df)} 行資料")
        return df
    
    except Exception as e:
        logger.error(f"從資料表 {table_name} 讀取資料時出錯: {str(e)}")
        # 返回空的 DataFrame
        return pd.DataFrame()

def save_hsi_data(df: pd.DataFrame, db_path: Optional[str] = None) -> bool:
    """
    將恆生指數歷史數據儲存到資料庫
    
    Parameters
    ----------
    df : pd.DataFrame
        包含恆生指數歷史數據的資料框
    db_path : str, optional
        資料庫檔案路徑
        
    Returns
    -------
    bool
        儲存是否成功
    """
    # 確保日期欄位為標準格式
    df_copy = df.copy()
    if 'date' in df_copy.columns:
        df_copy['date'] = pd.to_datetime(df_copy['date']).dt.strftime('%Y-%m-%d')
    
    # 添加更新時間欄位
    df_copy['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 儲存到資料庫
    return save_to_db(df_copy, 'hsi_history', db_path)

def load_hsi_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None, 
    db_path: Optional[str] = None
) -> pd.DataFrame:
    """
    從資料庫讀取恆生指數歷史數據
    
    Parameters
    ----------
    start_date : str, optional
        開始日期，格式為 'YYYY-MM-DD'
    end_date : str, optional
        結束日期，格式為 'YYYY-MM-DD'
    db_path : str, optional
        資料庫檔案路徑
        
    Returns
    -------
    pd.DataFrame
        包含查詢結果的資料框
    """
    # 構建查詢條件
    query = "SELECT * FROM hsi_history"
    params = {}
    
    if start_date or end_date:
        query += " WHERE "
        
        if start_date:
            query += "date >= :start_date"
            params['start_date'] = start_date
            
        if end_date:
            if start_date:
                query += " AND "
            query += "date <= :end_date"
            params['end_date'] = end_date
    
    # 按日期排序
    query += " ORDER BY date ASC"
    
    # 執行查詢
    df = load_from_db(None, db_path, query, params)
    
    # 確保日期欄位為 datetime 格式
    if not df.empty and 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    return df

def get_available_tables(db_path: Optional[str] = None) -> List[str]:
    """
    獲取資料庫中所有可用的資料表
    
    Parameters
    ----------
    db_path : str, optional
        資料庫檔案路徑
        
    Returns
    -------
    List[str]
        包含所有資料表名稱的列表
    """
    try:
        # 獲取資料庫連接
        conn = get_db_connection(db_path)
        
        # 查詢資料表列表
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 關閉連接
        conn.close()
        
        return tables
    
    except Exception as e:
        logger.error(f"獲取資料表列表時出錯: {str(e)}")
        return [] 