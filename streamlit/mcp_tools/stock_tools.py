"""
簡化版本的股票分析工具模塊，專為 Streamlit 部署設計
"""
import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import warnings
warnings.filterwarnings("ignore")

# Tiingo API 配置
TIINGO_API_KEY = os.getenv('TIINGO_API_KEY', "2146105fde5488455a958c98755941aafb9d9c66")

def get_stock_data(ticker: str, time_period: str = "365d") -> pd.DataFrame:
    """使用 Tiingo API 獲取股票歷史數據"""
    try:
        if not TIINGO_API_KEY or TIINGO_API_KEY == "YOUR_TIINGO_API_KEY_HERE":
            raise ValueError("有效的 Tiingo API 金鑰未配置。")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {TIINGO_API_KEY}'
        }

        # 標準化股票代碼
        ticker_processed = ticker.strip().upper()
        ticker_map = {
            "GOOG": "GOOGL",
            "GOOGLE": "GOOGL",
            "AMAZON": "AMZN"
        }
        actual_ticker = ticker_map.get(ticker_processed, ticker_processed)
        
        # 計算起始日期
        days = 365 # 預設為一年
        if "d" in time_period:
            days = int(time_period.replace("d", ""))
        elif "m" in time_period:
            days = int(time_period.replace("m", "")) * 30
        elif "y" in time_period:
            days = int(time_period.replace("y", "")) * 365
        
        now_utc = datetime.now(timezone.utc) 
        api_start_date_utc = now_utc - timedelta(days=days + 250) 
        
        five_years_ago_utc = now_utc - timedelta(days=5*365)
        if api_start_date_utc < five_years_ago_utc:
            api_start_date_utc = five_years_ago_utc
            
        start_date_str = api_start_date_utc.strftime('%Y-%m-%d')

        url = f"https://api.tiingo.com/tiingo/daily/{actual_ticker}/prices?startDate={start_date_str}&format=json"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 401:
            raise ValueError(f"Tiingo API 金鑰無效或未授權。")
        if response.status_code == 429:
            raise ValueError(f"Tiingo API 速率限制。請稍後再試。")
        if response.status_code == 404:
            raise ValueError(f"Tiingo API 找不到股票代碼 {actual_ticker}。")

        response.raise_for_status() 
        
        data = response.json()

        if not isinstance(data, list) or not data:
            if isinstance(data, dict) and "detail" in data:
                raise ValueError(f"無法獲取 {actual_ticker} 的股票數據: Tiingo API 錯誤 - {data['detail']}")
            raise ValueError(f"無法獲取 {actual_ticker} (原始: {ticker}) 的股票數據。API 未返回有效數據。")

        df = pd.DataFrame(data)
        
        if df.empty:
            raise ValueError(f"從 Tiingo API 獲取的 {actual_ticker} 數據為空。")

        column_mapping = {
            'date': 'date', 'adjOpen': 'open', 'adjHigh': 'high',
            'adjLow': 'low', 'adjClose': 'close', 'adjVolume': 'volume'
        }
        required_tiingo_cols = list(column_mapping.keys())
        missing_cols = [col for col in required_tiingo_cols if col not in df.columns]
        if missing_cols:
            # 如果 adjVolume 不存在，嘗試使用 volume
            if 'adjVolume' in missing_cols and 'volume' in df.columns:
                column_mapping['volume'] = 'volume'
                required_tiingo_cols.remove('adjVolume')
                if 'volume' not in required_tiingo_cols: required_tiingo_cols.append('volume')
                missing_cols = [col for col in required_tiingo_cols if col not in df.columns]
            
            if missing_cols:
                 raise ValueError(f"Tiingo API 返回的數據缺少必要欄位: {', '.join(missing_cols)}")

        df = df[list(column_mapping.keys())].rename(columns=column_mapping)
        
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)
        df.set_index('date', inplace=True)
        
        # 過濾數據
        filter_start_date_utc = now_utc - timedelta(days=days)
        filtered_df = df[df.index >= filter_start_date_utc].copy()
        
        if len(filtered_df) < 20:
            num_rows_to_take = min(len(df), max(days, 250)) 
            filtered_df = df.iloc[-num_rows_to_take:].copy()
            if len(filtered_df) < 20:
                 raise ValueError(f"獲取 {actual_ticker} 的股票數據不足20行 ({len(filtered_df)}行)，無法進行分析。")

        return filtered_df
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        raise ValueError(f"獲取 {ticker} 的股票數據時 (Tiingo API) 發生網路錯誤: {error_msg}")
    except ValueError as e:
        error_msg = str(e)
        raise ValueError(f"獲取 {ticker} 的股票數據時 (Tiingo API) 出錯: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        raise ValueError(f"獲取 {ticker} 的股票數據時 (Tiingo API) 發生未預期錯誤: {error_msg}")

def get_stock_price(ticker: str) -> dict:
    """獲取股票當前價格"""
    try:
        df = get_stock_data(ticker, "30d")
        
        if df.empty:
            return {"error": "無法獲取股票數據", "ticker": ticker}
    
        latest = df.iloc[-1]
        
        result = {
            "ticker": ticker.upper(),
            "current_price": float(latest["close"]),
            "open_price": float(latest["open"]),
            "high_price": float(latest["high"]),
            "low_price": float(latest["low"]),
            "volume": int(latest["volume"]),
            "date": latest.name.strftime("%Y-%m-%d"),
            "company_name": get_stock_name(ticker),
            "status": "success"
        }
        
        return result
        
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

def get_stock_name(ticker: str) -> str:
    """獲取股票名稱"""
    try:
        ticker_upper = ticker.strip().upper()
        common_names = {
            "AAPL": "Apple Inc.", 
            "MSFT": "Microsoft Corporation", 
            "GOOGL": "Alphabet Inc. Class A", 
            "GOOG": "Alphabet Inc. Class C", 
            "AMZN": "Amazon.com, Inc.", 
            "TSLA": "Tesla, Inc.", 
            "META": "Meta Platforms, Inc.", 
            "NVDA": "NVIDIA Corporation", 
            "JPM": "JPMorgan Chase & Co.", 
            "V": "Visa Inc.", 
            "VOO": "Vanguard S&P 500 ETF", 
            "VTI": "Vanguard Total Stock Market ETF", 
            "QQQ": "Invesco QQQ Trust", 
            "SPY": "SPDR S&P 500 ETF"
        }
        
        if ticker_upper in common_names:
            return common_names[ticker_upper]
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {TIINGO_API_KEY}'
        }
        
        meta_url = f"https://api.tiingo.com/tiingo/daily/{ticker_upper}"
        response = requests.get(meta_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "name" in data and data["name"]:
                return data["name"]
                
        return f"{ticker_upper} 股票/ETF"
    except:
        return f"{ticker.upper()} 股票/ETF"

def get_technical_indicators(ticker: str, indicators: str = "SMA,EMA,RSI,MACD", time_period: str = "365d") -> dict:
    """計算股票技術指標 (簡化版)"""
    try:
        indicator_list = [ind.strip().upper() for ind in indicators.split(',')]
        
        # 獲取股票數據
        df = get_stock_data(ticker, time_period)
        
        if df.empty:
            return {
                "error": f"無法獲取 {ticker} 的股票數據",
                "ticker": ticker
            }
            
        # 計算簡單技術指標
        results = {
            "ticker": ticker.upper(),
            "company_name": get_stock_name(ticker),
            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            "current_price": round(float(df['close'].iloc[-1]), 2),
            "data_points": len(df),
            "indicators": {}
        }
        
        if "SMA" in indicator_list:
            sma20 = df['close'].rolling(window=20).mean().iloc[-1]
            sma50 = df['close'].rolling(window=50).mean().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            results["indicators"]["SMA"] = {
                "SMA_20": round(float(sma20), 2),
                "SMA_50": round(float(sma50), 2),
                "Price_vs_SMA20": f"{((current_price / sma20) - 1) * 100:.2f}%",
                "Trend": "上升" if current_price > sma20 > sma50 else "下降" if current_price < sma20 < sma50 else "盤整"
            }
            
        if "RSI" in indicator_list:
            # 簡化的 RSI 計算
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            results["indicators"]["RSI"] = {
                "RSI_14": round(float(current_rsi), 2),
                "Signal": "超買" if current_rsi > 70 else "超賣" if current_rsi < 30 else "中性"
            }
            
        if "MACD" in indicator_list:
            # 簡化的 MACD 計算
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            results["indicators"]["MACD"] = {
                "MACD_line": round(float(macd_line.iloc[-1]), 4),
                "Signal_line": round(float(signal_line.iloc[-1]), 4),
                "Histogram": round(float(histogram.iloc[-1]), 4),
                "Signal": "買入" if macd_line.iloc[-1] > signal_line.iloc[-1] else "賣出"
            }
            
        return results
        
    except Exception as e:
        return {
            "error": str(e),
            "ticker": ticker
        }

def get_momentum_analysis(ticker: str, time_period: str = "180d") -> dict:
    """進行股票動量分析 (簡化版)"""
    try:
        df = get_stock_data(ticker, time_period)
        company_name = get_stock_name(ticker)
        
        if df.empty:
            return {
                "error": "無法獲取股票數據進行動量分析",
                "ticker": ticker,
                "name": company_name
            }
            
        # 計算簡單動量指標
        close = df['close']
        current_price = close.iloc[-1]
        
        # 計算 RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # 計算均線
        sma20 = close.rolling(window=20).mean().iloc[-1]
        sma50 = close.rolling(window=50).mean().iloc[-1]
        
        # 計算 MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        
        # 計算動能評分
        score = 50
        
        # 均線趨勢
        if current_price > sma20 > sma50:
            score += 15
        elif current_price < sma20 < sma50:
            score -= 15
            
        # RSI
        if current_rsi > 70:
            score += 10
        elif current_rsi < 30:
            score -= 10
            
        # MACD
        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            score += 10
        else:
            score -= 10
            
        # 近期表現
        if len(close) > 20:
            recent_change = (current_price / close.iloc[-20] - 1) * 100
            if recent_change > 10:
                score += 15
            elif recent_change < -10:
                score -= 15
                
        # 限制評分範圍
        score = max(0, min(100, score))
        
        # 生成評級
        if score >= 80:
            rating = "強勁看漲"
        elif score >= 60:
            rating = "看漲"
        elif score >= 40:
            rating = "中性"
        elif score >= 20:
            rating = "看跌"
        else:
            rating = "強勁看跌"
            
        # 建議
        if score >= 70:
            recommendation = "技術指標顯示強烈的上升動能，可考慮買入或持有"
        elif score >= 55:
            recommendation = "技術指標顯示良好的上升動能，可考慮持有"
        elif score >= 45:
            recommendation = "技術指標顯示中性動能，建議觀望"
        elif score >= 30:
            recommendation = "技術指標顯示下降動能，可考慮減倉"
        else:
            recommendation = "技術指標顯示強烈的下降動能，建議避開"
            
        if current_rsi > 70:
            recommendation += "，但注意 RSI 已達超買水平，可能面臨短期回調"
        elif current_rsi < 30:
            recommendation += "，但 RSI 已達超賣水平，可能出現短期反彈機會"
            
        return {
            "ticker": ticker.upper(),
            "name": company_name,
            "momentum_score": int(score),
            "rating": rating,
            "current_price": round(float(current_price), 2),
            "technical_summary": {
                "RSI_14": round(float(current_rsi), 2),
                "SMA_20": round(float(sma20), 2),
                "SMA_50": round(float(sma50), 2),
                "MACD": round(float(macd_line.iloc[-1]), 4),
                "Signal": round(float(signal_line.iloc[-1]), 4)
            },
            "recommendation": recommendation,
            "analysis_period": time_period
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "ticker": ticker,
            "name": company_name,
            "analysis_period": time_period
        }

def get_volume_analysis(ticker: str, time_period: str = "365d") -> dict:
    """進行成交量分析 (簡化版)"""
    try:
        df = get_stock_data(ticker, time_period)
        company_name = get_stock_name(ticker)
        
        if df.empty:
            return {
                "error": "無法獲取股票數據進行成交量分析",
                "ticker": ticker,
                "name": company_name
            }
            
        # 計算成交量指標
        current_price = df['close'].iloc[-1]
        
        # 成交量均線
        volume_ma20 = df['volume'].rolling(window=20).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        volume_ratio = current_volume / volume_ma20
        
        # 計算 VWAP (成交量加權平均價格)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        current_vwap = vwap.iloc[-1]
        
        # 計算 OBV (平衡成交量)
        obv = pd.Series(index=df.index, dtype='float64')
        obv.iloc[0] = df['volume'].iloc[0]
        
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
                
        obv_trend = "上升" if obv.iloc[-1] > obv.iloc[-6] else "下降"
        
        # 成交量趨勢分析
        volume_trend = "增加" if volume_ratio > 1.1 else "減少" if volume_ratio < 0.9 else "穩定"
        
        # 生成分析結果
        vwap_analysis = "價格高於 VWAP" if current_price > current_vwap else "價格低於 VWAP"
        vwap_deviation = ((current_price - current_vwap) / current_vwap) * 100
        
        analysis = ""
        if obv_trend == "上升" and volume_trend == "增加":
            analysis = "成交量指標呈現看漲，顯示買盤增強"
        elif obv_trend == "下降" and volume_trend == "增加":
            analysis = "成交量增加但 OBV 下降，顯示賣壓增大"
        elif volume_trend == "減少":
            analysis = "成交量正在減少，可能預示趨勢減弱"
        
        if vwap_deviation > 3:
            analysis += "，價格大幅高於 VWAP，可能面臨回調"
        elif vwap_deviation < -3:
            analysis += "，價格大幅低於 VWAP，可能存在買入機會"
            
        return {
            "ticker": ticker.upper(),
            "name": company_name,
            "current_price": round(float(current_price), 2),
            "volume_indicators": {
                "Current_Volume": int(current_volume),
                "Volume_MA20": int(volume_ma20),
                "Volume_Ratio": round(float(volume_ratio), 2),
                "VWAP": round(float(current_vwap), 2),
                "Price_vs_VWAP": f"{vwap_deviation:.2f}%",
                "OBV_Trend": obv_trend
            },
            "volume_trend": volume_trend,
            "vwap_analysis": vwap_analysis,
            "analysis": analysis,
            "analysis_period": time_period
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "ticker": ticker,
            "name": company_name,
            "analysis_period": time_period
        }

def list_available_indicators() -> dict:
    """列出所有可用的技術指標"""
    return {
        "basic_indicators": {
            "SMA": "簡單移動平均線 - 計算指定期間的平均價格",
            "EMA": "指數移動平均線 - 對近期價格給予更多權重", 
            "RSI": "相對強弱指標 - 衡量價格變動的速度和幅度 (0-100)",
            "MACD": "移動平均收斂背離指標 - 顯示兩條移動平均線的關係"
        },
        "volume_indicators": {
            "VWAP": "成交量加權平均價格 - 重要的交易基準價格",
            "OBV": "平衡成交量 - 結合價格和成交量的動量指標",
            "Volume_Ratio": "成交量比率 - 當前成交量與平均成交量的比值",
            "Volume_MA": "成交量移動平均線 - 成交量的趨勢指標"
        },
        "usage_examples": {
            "basic_analysis": "get_technical_indicators('AAPL', 'SMA,EMA,RSI,MACD')",
            "momentum_analysis": "get_momentum_analysis('AAPL', '180d')",
            "volume_analysis": "get_volume_analysis('AAPL', '365d')",
            "get_price": "get_stock_price('AAPL')"
        },
        "data_source": "Tiingo API",
        "status": "可用"
    }

def check_mcp_status() -> dict:
    """檢查 MCP 工具狀態"""
    try:
        # 測試基本調用
        test_result = get_stock_price("AAPL")
        
        return {
            "method": "simplified_streamlit",
            "status": "正常" if "error" not in test_result else "有問題",
            "tiingo_api_key": "已設置" if TIINGO_API_KEY and TIINGO_API_KEY != "YOUR_TIINGO_API_KEY_HERE" else "未設置"
        }
        
    except Exception as e:
        return {
            "method": "simplified_streamlit",
            "status": "失敗",
            "error": str(e)
        }
