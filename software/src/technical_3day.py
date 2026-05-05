import common_def as DEF

#################################################################
# 以下のような法則に該当するかを判定する
# 1日目に窓を大きく開けて陰線
# 2日目に陰線
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : dfrsi       データフレーム
#     : close       終値(現在価格)
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#################################################################
def jdg_3day(sb_mode, df):
    sigsw_3day = 0

    # 最後から指定期間分のレコードを取得
    df_3day = df.tail(3).loc[:,['datetime','open','high','low','close']]
   
    pre2_low = df_3day["low"].values[-3]
    pre2_open = df_3day["open"].values[-3]
    pre2_close = df_3day["close"].values[-3]
    pre1_hi = df_3day["high"].values[-2]
    pre1_open = df_3day["open"].values[-2]
    pre1_close = df_3day["close"].values[-2]
    open = df_3day["open"].values[-1]
    close = df_3day["close"].values[-1]
#    print(df_3day)

    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        # 前々日に窓が空いているか
        sp = pre2_low - pre1_hi
        if(sp > (pre2_close * 0.03)):
            # 過去2日連続陰線か
            if((pre1_open - pre1_close) > 0):
                if((open - close) > 0):
                    sigsw_3day = 1
            
    return sigsw_3day

