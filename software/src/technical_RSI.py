import pandas as pd
import numpy as np
import common_def as DEF

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

#    pd.set_option('display.max_rows', 100)     # print表示行数を100行にする
#    print(dfrsicnt)
    
    wk = 0
    ruiseki = 0
    for row in dfrsicnt.itertuples():
        wk += row.count
        wkper = (wk / total) * 100
        if low_per <= wkper:
            get_rsi = row[0]
            break

    print("RSI=", get_rsi)
    return get_rsi


#################################################################
# 現在のRSIが購入を許可できる値であるかをチェックする
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : dfrsi       データフレーム
#     : limit       RSI閾値
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#################################################################
def jdg_rsi_level(sb_mode, dfrsi, limit):
    sigsw_rsi = 0
    # RSI上限判定
    nowrsi = dfrsi["RSI"].values[-1]

    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        # リミット以下なら許可
        if nowrsi <= limit:
            sigsw_rsi = 1
    # 売りシグナル判定
    elif sb_mode == DEF.MODE_SELL:
        # リミット以上なら許可
        if nowrsi >= limit:
            sigsw_rsi = 1

    return sigsw_rsi   

#################################################################
# 過去指定期間でRSIが指定値を閾値内に入ったかどうかを判定する
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : dfrsi       データフレーム
#     : limit_rsi   RSI閾値
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#################################################################
def jdg_rsi_entered(sb_mode, dfrsi, limit_rsi):
    sigsw_rsi = 0
    for i, row in dfrsi.iterrows():
        rsi = row["RSI"]
        # 買いシグナル判定
        if sb_mode == DEF.MODE_BUY:
            if rsi <= limit_rsi:
                sigsw_rsi = 1
                break
        # 売りシグナル判定
        elif sb_mode == DEF.MODE_SELL:
            if rsi >= limit_rsi:
                sigsw_rsi = 1
                break

    return sigsw_rsi   

