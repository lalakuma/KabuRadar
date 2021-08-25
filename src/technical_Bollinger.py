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

    return df
    
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