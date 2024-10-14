import pandas as pd
import numpy as np
import common_def as DEF

#################################################################
#   コナーズRSIを取得する
# ################################################################

# コナーズRSI取得関数
def get_connors_rsi(df, period: int = 4):
    cns_rsi = connors_rsi(df, 4, 4, 100)
    df['RSI4'] = cns_rsi['RSI4']
    return df

# ワイルダー式RSI算出
def wilders_rsi(df, period):
    delta = df['close'].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    avg_gain = up.ewm(com=period-1, min_periods=period).mean()
    avg_loss = abs(down.ewm(com=period-1, min_periods=period).mean())
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi.name = 'RSI'  # RSIの計算結果の列名を'RSI'に変更
    df_wrsi = pd.DataFrame(rsi)
    return df_wrsi

# 連続騰落期間のRSI算出
def streak_rsi(df, period):
    streak = df['close'].diff()
    streak[streak < 0] = -1
    streak[streak > 0] = 1
    streak = streak.cumsum()
    streak_df = pd.DataFrame(streak, columns=['close'])
    streak_rsi = wilders_rsi(streak_df, period)
    return streak_rsi

# ROC算出
def roc(df, period):
    roc = df['close'].diff(period) / df['close'].shift(period) * 100
    roc.name = 'ROC'  # ROCの計算結果の列名を'ROC'に変更
    df_roc = pd.DataFrame(roc)
    return df_roc

# コナーズRSI算出
def connors_rsi(df, rsi_period, streak_period, roc_period):
    rsi_value = wilders_rsi(df, rsi_period)
    streak_rsi_value = streak_rsi(df, streak_period)
    roc_value = roc(df, roc_period)
    # print(rsi_value)
    # print(streak_rsi_value)
    # print(roc_value)
    connors_rsi_value = (rsi_value['RSI'] + streak_rsi_value['RSI'] + roc_value['ROC']) / 3
    df_crsi = pd.DataFrame(connors_rsi_value, columns=['RSI4'])
    return df_crsi

#################################################################
#   RSIを算出する
#   (TradingViewで表示されるのはこっち[ワイルダー式])
#   (こちらのRSIの方がいい気がする)
# ################################################################
def rsi_tradingview(ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = False):
    delta = ohlc["close"].diff()

    up = delta.copy()
    up[up < 0] = 0
    up = pd.Series.ewm(up, alpha=1/period).mean()

    down = delta.copy()
    down[down > 0] = 0
    down *= -1
    down = pd.Series.ewm(down, alpha=1/period).mean()
    rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))
    if period == 14:
        ohlc["RSI"] = np.round(rsi, 2) if round_rsi else rsi
    elif period == 4:
        ohlc["RSI4"] = np.round(rsi, 2) if round_rsi else rsi
    return ohlc

#################################################################
#   RSIを算出する
#   (SIB証券のアプリで表示されるのはこっち[カトラー式])
#   (正直　rsi_tradingview()とどちらがいいのか分からない)
# ################################################################
def rsi(df, period: int = 14):
    # 前日との差分を計算
    df_diff = df["close"].diff(1)
 
    # 計算用のDataFrameを定義
    df_up, df_down = df_diff.copy(), df_diff.copy()
    
    # df_upはマイナス値を0に変換
    # df_downはプラス値を0に変換して正負反転
    df_up[df_up < 0] = 0
    df_down[df_down > 0] = 0
    df_down = df_down * -1
    
    # 指定期間でそれぞれの平均を算出
    df_up_sma = df_up.rolling(window=period, center=False).mean()
    df_down_sma = df_down.rolling(window=period, center=False).mean()
 
    # RSIを算出
    df["RSI4"] = 100.0 * (df_up_sma / (df_up_sma + df_down_sma))
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

#################################################################
# RSIパワーゾーン短期売買法
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df       データフレーム
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#################################################################
def jdg_rsi_short(sb_mode, df, srsi_low, jdg_rsi4rev):
    sigsw_rsi = 0
    taildf = df.tail(5)
    rsi4 = taildf["RSI4"].values[-1]        # 当日短期RSI
    rsi4_pre1 = taildf["RSI4"].values[-2]   # 前日短期RSI

#    print(taildf)
    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        if(jdg_rsi4rev == 0):
            if (rsi4 < srsi_low):             # 当日RSIが下限を下回った
                sigsw_rsi = 1
        else:
            if (rsi4_pre1 < srsi_low):          # 前日RSIが下限RSIを下回った
                if (rsi4_pre1 < rsi4):          # 前日より当日RSIが高い
                    if (rsi4 < 40):             # 当日RSIが40未満   
                        sigsw_rsi = 1
    # 売りシグナル判定
    elif sb_mode == DEF.MODE_SELL:
        if(jdg_rsi4rev == 0):
            if (rsi4 > (100 - srsi_low)):
                sigsw_rsi = 1
        else:
            if (rsi4_pre1 > (100 - srsi_low)):
                if (rsi4_pre1 > rsi4):
                    if (rsi4 > (100 - 40)):             # 当日RSIが40未満   
                        sigsw_rsi = 1

    return sigsw_rsi   
#################################################################
# RSIパワーゾーン短期売買法の決済判定
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df       データフレーム
# 戻り値：True=決済する, False=決済しない
#################################################################
def jdg_rsi_shortkessai(sb_mode, df, srsi_hi, srsi_low ):
    sigsw_rsi = False
    taildf = df.tail(5)
    rsi4 = taildf["RSI4"].values[-1]      # 当日短期RSI
    rsi4_pre1 = taildf["RSI4"].values[-2]   # 前日短期RSI

    # 買いエントリー時の決済シグナル判定
    if sb_mode == DEF.MODE_BUY:
        if (srsi_hi < rsi4):    # 上限を超えたら利確
            sigsw_rsi = True
#        if (srsi_low > rsi4):   # ポジション保持中に再度下限を超えたら損切
#            sigsw_rsi = True
    # 売りエントリー時の決済シグナル判定
    elif sb_mode == DEF.MODE_SELL:
        if (100 - srsi_hi > rsi4):
            sigsw_rsi = True
        # if (srsi_low < rsi4):
        #     sigsw_rsi = True

    return sigsw_rsi   
