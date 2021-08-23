import common_def as DEF

#-----------------------------------
# 移動平均線の傾きによるトレンド判定
# 引数：mode  (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df    データフレーム
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#-----------------------------------
def jdg_movave_trend(mode, df):
    ret_sig = 0
    taildf = df.tail(5)
    sma1 = taildf["SMASET"].values[0]
    sma2 = taildf["SMASET"].values[-1]
    
    # 買いモードの時
    if mode == DEF.MODE_BUY:               
        # 右肩上がりなら買い
        if sma1 < sma2:
            ret_sig = 1         # 買いシグナル設定
    # 売りモードの時
    elif mode == DEF.MODE_SELL:
        # 右肩下がりなら売り
        if sma1 > sma2:
            ret_sig = 1         # 売りシグナル設定
