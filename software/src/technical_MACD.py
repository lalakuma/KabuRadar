import common_def as DEF

#################################################################
# MACDを計算して追加する
#################################################################
def macd(df, prmtype=1):
    if prmtype == 1:
        FastEMA_period = 8  # 短期EMAの期間
        SlowEMA_period = 18  # 長期EMAの期間
        SignalSMA_period = 6  # SMAを取る期間
    else:
        FastEMA_period = 12  # 短期EMAの期間
        SlowEMA_period = 26  # 長期EMAの期間
        SignalSMA_period = 9  # SMAを取る期間
        
    df["MACD"] = df["close"].ewm(span=FastEMA_period).mean() - df["close"].ewm(span=SlowEMA_period).mean()
    df["Signal"] = df["MACD"].rolling(SignalSMA_period).mean()
    return df


#################################################################
# MACDとシグナルの上限関係を判定する
# 買いシグナルが発生したときはゴールデンクロス後になる
# 売りシグナルが発生したときはデッドクロス後になる
# 売買シグナルを強くする為に、オフセットを使用してMACDとSignalの開きを大きく
# してから売買シグナルを発生させるようにしている
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : dfrsi       データフレーム
#     : offset      オフセット
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#################################################################
def jdg_macd_cross(sb_mode, df, offset):
    sigsw_macd = 0

    # 最新のMACDとシグナルの値を取得
    macd = df["MACD"].values[-1]
    sig = df["Signal"].values[-1]
    # MACD > SIGで買いシグナル
    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        if macd > sig + offset:     # MACDがシグナルより上にあれば買いシグナル
            sigsw_macd = 1
    # 売りシグナル判定
    elif sb_mode == DEF.MODE_SELL:
        if macd < sig - offset:     # MACDがシグナルより下にあれば買いシグナル
            sigsw_macd = 1

    return sigsw_macd

#################################################################
# MACDとシグナルの位置関係より売り目線か買い目線かを取得する
# 引数：dfrsi       データフレーム
# 戻り値：MODE_SELL=売り方向, MODE_BUY=買い方向シグナルあり
#################################################################
def get_macd_direction(df):
    direction = DEF.MODE_BUY    # 買い目線で初期化

    # 最新のMACDとシグナルの値を取得
    macd = df["MACD"].values[-1]
    sig = df["Signal"].values[-1]

    # sigの方が高ければ売り目線
    if macd < sig:
        direction = DEF.MODE_BUY

    return direction
