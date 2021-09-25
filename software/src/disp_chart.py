"""
yahoo_finance_api2で株価を取得してMACDとRSIを計算してグラフで表示する
"""

import mplfinance as mpf
import technical_MACD as tc_macd
import technical_RSI as tc_rsi

def display(df):
    df = tc_macd.macd(df)
    df = tc_rsi.rsi(df)

    df.head()

    add_plot = [
        mpf.make_addplot(df['MACD'], color='r',panel=1,secondary_y=False),
        mpf.make_addplot(df['Signal'], color='g',panel=1,secondary_y=False),    
        mpf.make_addplot(df['RSI'], color='b',panel=2,secondary_y=False),    
    ]
    mpf.plot(df,type="candle", volume_panel=3, volume=True,mav=(5,13),addplot=add_plot)
