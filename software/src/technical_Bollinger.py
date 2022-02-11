import common_def as DEF

#################################################################
# ボリンジャーバンドを計算して追加する
#################################################################
def Bollinger(df):

    # ボリンジャーバンドの計算
    df['bb_mean'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper2'] = df['bb_mean'] + (df['bb_std'] * 2)
    df['bb_lower2'] = df['bb_mean'] - (df['bb_std'] * 2)
    df['bb_upper3'] = df['bb_mean'] + (df['bb_std'] * 3)
    df['bb_lower3'] = df['bb_mean'] - (df['bb_std'] * 3)

    return df
        
#################################################################
# 指定期間内で2回以上ボリンジャーバンドの2σ/-2σを超えているかを判定する
# 引数：mode        (MODE_BUY=買い、MODE_SELL=売り)
#     : dfrsi       データフレーム
#     : period      期間
# 戻り値：True=買いの時に2回以上2σを超えている/売りの時に-2σを超えている
#       ：False=買いの時に2回以上2σを超えていない/売りの時に-2σを超えていない
#################################################################
def jdg_Bollinger_over(sb_mode, df, period):
    # 最後から指定期間分のレコードを取得
    df_bb = df.tail(period)
    # 指定期間のデータを抽出
    size = len(df_bb)
    judge = False

    overCnt = 0
    for row in df_bb.itertuples():
        offset = row.close * 0.005
        if sb_mode == DEF.MODE_BUY:
            if row.close > row.bb_upper2 + offset:
                overCnt += 1
            if overCnt > 1:
                judge = True
                break
        else:
            if row.close < row.bb_lower2 - offset:
                overCnt += 1
            if overCnt > 1:
                judge = True
                break

    return judge

#################################################################
# 指定期間内でボリンジャーバンドの2σ/-2σを超えているかを判定する
# 引数：mode        (MODE_BUY=買い、MODE_SELL=売り)
#     : dfrsi       データフレーム
#     : period      期間
# 戻り値：True=買いの時に2σを超えている/売りの時に-2σを超えている
#       ：False=買いの時に2σを超えていない/売りの時に-2σを超えていない
#################################################################
def jdg_Bollinger_over2(sb_mode, df, period):
    # 最後から指定期間分のレコードを取得
    df_bb = df.tail(period)
    # 指定期間のデータを抽出
    size = len(df_bb)
    judge = False

    for row in df_bb.itertuples():
        offset = row.close * 0.015
        if sb_mode == DEF.MODE_BUY:
            if row.close > row.bb_upper2 + offset:
                judge = True
                break
        else:
            if row.close < row.bb_lower2 - offset:
                judge = True
                break

    return judge

#################################################################
# 当日高値がボリンジャーバンドの3σ/-3σを指定%以上超えているかを判定する
# 引数：mode        (MODE_BUY=買い、MODE_SELL=売り)
#     : dfrsi       データフレーム
#     : period      期間
# 戻り値：True=買いの時に2σを超えている/売りの時に-2σを超えている
#       ：False=買いの時に2σを超えていない/売りの時に-2σを超えていない
#################################################################
def jdg_Bollinger_over3(sb_mode, df, high):
    # 最後から指定期間分のレコードを取得
    judge = False
    now_hige = df["high"].values[-1]
    now_low = df["low"].values[-1]
    now_BBupper3 = df["bb_upper3"].values[-1]
    now_BBlower3 = df["bb_lower3"].values[-1]
#    offset = now_hige * 0.015       # とりあえず1.5%としてみる
    offset = 0                       # やっぱ0
    if sb_mode == DEF.MODE_BUY:
        if now_hige > now_BBupper3 + offset:
            judge = True
    else:
        if now_low < now_BBlower3 - offset:
            judge = True

    return judge