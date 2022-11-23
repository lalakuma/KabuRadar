import common_def as DEF
import pandas as pd
#-----------------------------------
# 移動平均線の傾きによるトレンド判定
# 引数：mode  (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df    データフレーム
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#-----------------------------------
def jdg_movave_trend(mode, df, i_close):
    ret_sig = 0
    taildf = df.tail(5)
    sma25_pre5 = taildf["SMA25"].values[-5]
    sma25 = taildf["SMA25"].values[-1]
    ofset25 = sma25 * 0.01 

#    print(taildf)

    # 買いモードの時
    if mode == DEF.MODE_BUY:               
        if (sma25_pre5 + ofset25) < sma25:
            # 25日線より上なら買い
            if i_close >= sma25:
                ret_sig = 1         # 買いシグナル設定
    # 売りモードの時
    elif mode == DEF.MODE_SELL:
        if sma25_pre5 > (sma25 + ofset25) :
            # 25日線より下なら買い
            if i_close <= sma25:
                ret_sig = 1         # 売りシグナル設定
    
    return ret_sig 

#-----------------------------------
# 移動平均線の傾きによるトレンド判定
# 引数：mode  (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : df    データフレーム
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#-----------------------------------
def jdg_longmovave_trend(mode, df, i_close):
    ret_sig = 0
    taildf = df.tail(5)
    smaset_pre1 = taildf["SMASET"].values[-2]
    smaset = taildf["SMASET"].values[-1]
    ofset = smaset * 0.01 

    # 買いモードの時
    if mode == DEF.MODE_BUY:               
        # 右肩上がりなら買い
        if smaset_pre1 < smaset:
            # 長期線より上なら買い
            if i_close > smaset:
                ret_sig = 1         # 買いシグナル設定
    # 売りモードの時
    elif mode == DEF.MODE_SELL:
        # 右肩下がりなら売り
        if smaset_pre1 > smaset:
            # 25日線より下なら買い
            if i_close < smaset:
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
def jdg_movave_Push(mode, df, i_open, i_close):
    pd.set_option('display.max_rows', None)
    ret_sig = 0
    taildf = df.tail(5)
#    print(taildf)

#    pd.set_option('display.max_rows', None)
    sma5 = taildf["SMA5"].values[-1]        # 当日5日線
    low = taildf["low"].values[-1]          # 当日安値
    sma25 = taildf["SMA25"].values[-1]      # 当日25日線
    sma25_pre1 = taildf["SMA25"].values[-2] # 前日25日線
    low_pre1 = taildf["low"].values[-2]     # 前日安値
    sma5_pre1 = taildf["SMA5"].values[-2]   # 前日5日線
    sma5_pre2 = taildf["SMA5"].values[-3]   # 前々日5日線
    sma5_pre3 = taildf["SMA5"].values[-4]   # 前々々日5日線

    sma5_ofset = sma5 * 0.005

#    print(taildf)
    # 当日および前日の安値と25日線の差を算出
    diff1 = abs(low_pre1 - sma25_pre1)
    diff2 = abs(low - sma25)
#    near = sma25_pre1 * 0.015
    near = sma25_pre1 * 0.1
    # 25日線から離れすぎていたら売買シグナルなしとする
    if (near < diff1) or (near < diff2):
        return ret_sig 

    # 買いモードの時
    if mode == DEF.MODE_BUY:    
        if (i_close > sma5 + sma5_ofset) and (i_open < sma5):
            # 過去5日間で5日線が右下がりになっていたか
            if (sma5_pre1 < sma5_pre2) and (sma5_pre2 < sma5_pre3):
                # 前日から右上がりになっていれば買い
#                if sma5_pre1 < (sma5 - sma5_ofset):
                ret_sig = 1         # 買いシグナル設定
    # 売りモードの時
    elif mode == DEF.MODE_SELL:
        if (i_close < sma5 - sma5_ofset ) and (i_open > sma5):
            # 過去5日間で5日線が右上がりになっていたか
            if (sma5_pre1 > sma5_pre2) and (sma5_pre2 > sma5_pre3):
                # 前日から右下がりになっていれば買い
#                if sma5_pre1 > (sma5 + sma5_ofset):   # 
                ret_sig = 1         # 売りシグナル設定

    return ret_sig 