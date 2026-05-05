import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_pricedata(code, ptype, peri, freq):
    
    ticker_code = ""
    if code == '0':
        ticker_code = '^N225'
    elif code == '800':
        ticker_code = '^DJI'
    else:
        ticker_code = str(code) + '.T'

    period_str = ""
    if ptype == "day":
        period_str = str(peri) + "d"
    elif ptype == "year":
        period_str = str(peri) + "y"
    else:
        period_str = "10d"

    interval_str = "1d"

    try:
        ticker = yf.Ticker(ticker_code)
        df_daily = ticker.history(period=period_str, interval=interval_str, auto_adjust=False)

        if df_daily.empty:
            print(f"Code {code}: No data found for the given period.")
            return pd.DataFrame()

        df_daily.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        df_daily = df_daily[["open", "high", "low", "close", "volume"]]

    except Exception as e:
        print(f"Code {code}: 予期しないエラーが発生しました: {e}")
        return pd.DataFrame()

    df_daily.index.name = 'datetime'
    return df_daily