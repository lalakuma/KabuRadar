import pandas as pd
import numpy as np

#################################################################
#   RSIを算出する
#   (TradingViewで表示されるのはこっち)
#   (正直　下のrsi()とどちらがいいのか分からない)
# ################################################################
def rsi_tradingview(ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = False):
    """ Implements the RSI indicator as defined by TradingView on March 15, 2021.
        The TradingView code is as follows:
        //@version=4
        study(title="Relative Strength Index", shorttitle="RSI", format=format.price, precision=2, resolution="")
        len = input(14, minval=1, title="Length")
        src = input(close, "Source", type = input.source)
        up = rma(max(change(src), 0), len)
        down = rma(-min(change(src), 0), len)
        rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))
        plot(rsi, "RSI", color=#8E1599)
        band1 = hline(70, "Upper Band", color=#C0C0C0)
        band0 = hline(30, "Lower Band", color=#C0C0C0)
        fill(band1, band0, color=#9915FF, transp=90, title="Background")
    :param ohlc:
    :param period:
    :param round_rsi:
    :return: an array with the RSI indicator values
    """

    delta = ohlc["close"].diff()

    up = delta.copy()
    up[up < 0] = 0
    up = pd.Series.ewm(up, alpha=1/period).mean()

    down = delta.copy()
    down[down > 0] = 0
    down *= -1
    down = pd.Series.ewm(down, alpha=1/period).mean()

    rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))
    ohlc["RSI"] = np.round(rsi, 2) if round_rsi else rsi
    return ohlc

#################################################################
#   RSIを算出する
#   (SIB証券のアプリで表示されるのはこっち)
#   (正直　rsi_tradingview()とどちらがいいのか分からない)
# ################################################################
def rsi(df):
    # 前日との差分を計算
    df_diff = df["close"].diff(1)
 
    # 計算用のDataFrameを定義
    df_up, df_down = df_diff.copy(), df_diff.copy()
    
    # df_upはマイナス値を0に変換
    # df_downはプラス値を0に変換して正負反転
    df_up[df_up < 0] = 0
    df_down[df_down > 0] = 0
    df_down = df_down * -1
    
    # 期間14でそれぞれの平均を算出
    df_up_sma14 = df_up.rolling(window=14, center=False).mean()
    df_down_sma14 = df_down.rolling(window=14, center=False).mean()
 
    # RSIを算出
    df["RSI"] = 100.0 * (df_up_sma14 / (df_up_sma14 + df_down_sma14))
 
    return df

#################################################################
#   RSIの下限値を指定銘柄におけるRSI全体の合計数の割合から求める
#################################################################
def search_proper_rsi(df, low_per):  
    dfrsi = df.loc[:,['RSI']]
    dfrsi["count"] = 0
    dfrsi = dfrsi.round()

    dfrsicnt = dfrsi.groupby(['RSI']).count()
    total = dfrsicnt["count"].sum()
    wk = 0
    ruiseki = 0
    for row in dfrsicnt.itertuples():
        wk += row.count
        wkper = (wk / total) * 100
        ruiseki += wkper
        if low_per <= ruiseki:
            get_rsi = row[0]
            break

    print("RSI=", get_rsi)
    return get_rsi

