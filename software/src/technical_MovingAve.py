import common_def as DEF
import pandas as pd
#-----------------------------------
# 移動平均線の傾きによるトレンド判定
# 引数：mode  (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df    データフレーム
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#-----------------------------------
def jdg_movave_trend(mode, df):
    ret_sig = 0
    taildf = df.tail(5)
    sma1_pre1 = taildf["SMASET"].values[0]
    sma2 = taildf["SMASET"].values[-1]
    sma25_pre5 = taildf["SMA25"].values[-5]
    sma25 = taildf["SMA25"].values[-1]
    ofset25 = sma25 * 0.01 

#    print(taildf)

    # 買いモードの時
    if mode == DEF.MODE_BUY:               
        # 右肩上がりなら買い
        if sma1_pre1 < sma2:
            if (sma25_pre5 + ofset25) < sma25:
                ret_sig = 1         # 買いシグナル設定
    # 売りモードの時
    elif mode == DEF.MODE_SELL:
        # 右肩下がりなら売り
        if sma1_pre1 > sma2:
            if sma25_pre5 > (sma25 + ofset25) :
                ret_sig = 1         # 売りシグナル設定
    
    return ret_sig 
#-----------------------------------
# パーフェクトオーダー判定
# 買いの時に5日＞25日＞75日、売りの時に5日＜25日＜75日
# となっているかを判定する。（長期が75日である場合）
# 引数：mode  (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df    データフレーム
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#-----------------------------------
def jdg_movave_PfctOder(mode, df):
    ret_sig = 0
#    print(df)
    taildf = df.tail(5)
    smaLong = taildf["SMASET"].values[-1]
    sma25 = taildf["SMA25"].values[-1]
    sma5 = taildf["SMA5"].values[-1]
    
    # 買いモードの時
    if mode == DEF.MODE_BUY:             
        # 長期線 < 25日線 < 5日線なら買い
        if smaLong < sma25:
            if sma25 < sma5:
                ret_sig = 1         # 買いシグナル設定
    # 売りモードの時
    elif mode == DEF.MODE_SELL:
        # 長期線 > 25日線 > 5日線なら買い
        if smaLong > sma25:
            if sma25 > sma5:
                ret_sig = 1         # 売りシグナル設定

    return ret_sig 

#-----------------------------------
# 押し目判定
# 引数：mode  (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df    データフレーム
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#-----------------------------------
def jdg_movave_Push(mode, df, i_close):
    pd.set_option('display.max_rows', None)
    ret_sig = 0
#    print(df)
    taildf = df.tail(5)

#    pd.set_option('display.max_rows', None)
    sma5 = taildf["SMA5"].values[-1]        # 当日5日線
    sma5_pre1 = taildf["SMA5"].values[-2]   # 前日5日線
    sma5_pre2 = taildf["SMA5"].values[-3]   # 前々日5日線
    sma5_pre3 = taildf["SMA5"].values[-4]   # 前々々日5日線

    sma5_ofset = sma5 * 0.005

#    print(taildf)
    
    # 買いモードの時
    if mode == DEF.MODE_BUY:               
        # 過去3日間で5日線が右下がりになっていたか
        if (sma5_pre1 < sma5_pre2) and (sma5_pre2 < sma5_pre3):
            # 前日から右上がりになっていれば買い
            if sma5_pre1 < (sma5 - sma5_ofset):
                ret_sig = 1         # 買いシグナル設定
    # 売りモードの時
    elif mode == DEF.MODE_SELL:
        # 過去3日間で5日線が右上がりになっていたか
        if (sma5_pre1 > sma5_pre2) and (sma5_pre2 > sma5_pre3):
            # 前日から右下がりになっていれば買い
            if sma5_pre1 > (sma5 + sma5_ofset):   # 
                ret_sig = 1         # 売りシグナル設定

    return ret_sig 