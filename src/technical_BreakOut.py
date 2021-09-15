import common_def as DEF

#################################################################
# ブレイクアウトが発生したかを判定する
# 指定期間内における最大値または最小値を現在価格が超えているかを調べる
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : dfrsi       データフレーム
#     : period      期間
#     : offset      オフセット
#     : close       終値(現在価格)
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#################################################################
def jdg_break_out(sb_mode, df, period, offset, close):
    sigsw_break = 0
    breakoffset = close * offset

    # 最後から指定期間分のレコードを取得
    breakdf = df.tail(period)
    # 指定期間のデータを抽出
    size = len(breakdf)

    breakdf = breakdf.set_index("datetime")
    breakdf = breakdf.head(size - 1)

    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        # 指定期間で一番の高値を取得
        df_max = breakdf.rolling(window=size-1).max()
        max = df_max["high"].values[-1]
        # 現在の価格が前日までの指定期間の高値を超えている場合に買いシグナルON
        if close > max + breakoffset:
            sigsw_break = 1
    # 売りシグナル判定
    elif sb_mode == DEF.MODE_SELL:
        # 指定期間で一番の安値を取得
        df_min = breakdf.rolling(window=size-1).min()
        min = df_min["low"].values[-1]
        # 現在の価格が前日までの指定期間の高値を超えている場合に買いシグナルON
        if close < min - breakoffset:
            sigsw_break = 1

    return sigsw_break

def jdg_break_out2(sb_mode, df, period, offset, close):
    sigsw_break = 0
    breakoffset = close * offset

    # 最後から指定期間分のレコードを取得
    breakdf = df.tail(period)
    # 指定期間のデータを抽出
    size = len(breakdf)

    breakdf = breakdf.set_index("datetime")
    breakdf_bef1 = breakdf.head(size - 1)   # 前日までのデータ
    breakdf_bef2 = breakdf.head(size - 2)   # 前々日までのデータ

    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        # 前日の終値取得
        close_bef1 = breakdf_bef1["close"].values[-1]
        # 指定期間で一番の高値を取得
        df_max = breakdf_bef2.rolling(window=size-2).max()
        max = df_max["high"].values[-1]

        # 前日の終値が前々日までの期間の最高値より低い時に処理する
        if close_bef1 < max:
            # 現在の価格が前日までの指定期間の高値を超えている場合に買いシグナルON
            if close > max + breakoffset:
                sigsw_break = 1
    # 売りシグナル判定
    elif sb_mode == DEF.MODE_SELL:
        # 前日の終値取得
        close_bef1 = breakdf_bef1["close"].values[-1]
        # 指定期間で一番の安値を取得
        df_min = breakdf_bef2.rolling(window=size-2).min()
        min = df_min["low"].values[-1]

        # 前日の終値が前々日までの期間の最安値より高い時に処理する
        if close_bef1 > min:
            # 現在の価格が前日までの指定期間の安値を超えている場合に売りシグナルON
            if close < min - breakoffset:
                sigsw_break = 1

    return sigsw_break