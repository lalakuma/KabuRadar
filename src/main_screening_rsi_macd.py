import pandas as pd
import mplfinance as mpf
import technical_MACD as tc_macd
import technical_RSI as tc_rsi
import sqlight as db
import line
from datetime import datetime, date, timedelta


#****************************
# 定義値
#****************************
MODE_SELL = 1
MODE_BUY = 0

#****************************
# スクリーニング用の設定値
#****************************
# 移動平均線の傾き確認に使用する値
scr_lineave = 100
# MACDとシグナルの開きに使用する値
scr_macd = 5
# RSIの買いに採用する最大値
scr_rsi_max = 65
# RSIの売りに採用する最小値
scr_rsi_min = 60
# 買いシグナルRSI閾値に使用する値
scr_b_rsi = 30
# 売りシグナルRSI閾値に使用する値
scr_s_rsi = 85
# RSI閾値超過後の猶予日数に使用する値
scr_rsipass = 14
# ブレイクアウト判定期間に使用する値
scr_break = 5

# SELL/BUY モード切替  (買い=MODE_BUY, 売り=MODE_SELL)
sb_mode = MODE_SELL 

#--------------------------------------
# 有効判定設定
#--------------------------------------
# 移動平均判定
judge_move  = False
# RSI判定
judge_rsi  = True
# MACD判定
judge_macd  = True
# BREAK OUT判定
judge_break  = True

#--------------------------------------
# DBから全銘柄コードを取得
#--------------------------------------
# DBに接続
conn, cursor = db.connect_db()

#lst_dfprice = []
lst_low_rsi = []
lst_codes = []

# 個別銘柄 期間データ取得
today = date.today()                                                                    # 今日(日付型)
str_date_sta = datetime.strftime(today + timedelta(days = (scr_lineave * (-1))-10), '%Y-%m-%d')  # 開始日(移動平均線を出せる日付を指定)
str_date_end = datetime.strftime(today + timedelta(days = 1), '%Y-%m-%d')               # 明日
str_today = datetime.strftime(today, '%Y-%m-%d')                                        # 今日
str_bef = datetime.strftime(today + timedelta(days = (-1) * scr_rsipass), '%Y-%m-%d')   # 指定日前

# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")
for md in range(2):
    # 初回ループはMODE_BUY、2回目はMODE_SELL
    sb_mode = md

    # 銘柄コードリストに登録されている全コードに対して処理を行う
    for code in codes:
        # 指定期間のデータをDBから読み出す
        df = db.read_rec_period(conn, cursor, str(code), str_date_sta, str_date_end)
        #df.columns = ["datetime","open","high","low","close","volume"]

        try:
            df['datetime'] = df['datetime'].astype('datetime64')
            df['open'] = df['open'].astype('int64')
            df['high'] = df['high'].astype('int64')
            df['low'] = df['low'].astype('int64')
            df['close'] = df['close'].astype('int64')
            df['volume'] = df['volume'].astype('int64')
            df['SMA5'] = df['close'].rolling(window=5).mean()       # 5日移動平均を追加
            df['SMA25'] = df['close'].rolling(window=25).mean()     # 25日移動平均を追加
            df['SMASET'] = df['close'].rolling(window=scr_lineave).mean()     # 設定した移動平均を追加
        except:
            print(code + ": Error")
            continue        

        #日付をインデックスにして、必要なアイテム順に並び替え
        df_price = df.set_index("datetime").loc[:,["open","high","low","close","volume","SMA5","SMA25","SMASET"]]

        # MACDとRSIを追加
        df_price = tc_macd.macd(df_price)
        df_price = tc_rsi.rsi(df_price)

        # 全情報をリストに追加
        #lst_dfprice.append(df_price)

        # 終値取得
        i_close = df_price["close"].values[-1]

    # 銘柄コードで調査用 
    #    if str(code) == "9107":
    #        print(code)
    #
        #----------------------
        # 移動平均判定
        #----------------------
        if judge_move == True:                  # 移動平均判定が有効な時に実行
            buy_smaset = 0 
            taildf = df.tail(5)
            sma1 = taildf["SMASET"].values[0]
            sma2 = taildf["SMASET"].values[-1]
            if sma1 <= sma2:
                buy_smaset = 1 

            if buy_smaset == 0:
                continue

        #----------------------
        # RSI判定
        #----------------------
        if judge_rsi == True:                  # RSI判定が有効な時に実行
            # 過去指定日前からのRSIを取得
            dfrsi = df_price.loc[str_bef:,["RSI"]]

            # RSI上限判定
            nowrsi = dfrsi["RSI"].values[-1]

            if sb_mode == MODE_BUY:
                if nowrsi > scr_rsi_max:
                    continue
            elif sb_mode == MODE_SELL:
                if nowrsi < scr_rsi_min:
                    continue

            # 過去指定期間でRSIが指定値を閾値を超えたらRSIシグナルスイッチを1にする
            sigsw_rsi = 0
            for i, row in dfrsi.iterrows():
                rsi = row["RSI"]
                # 買いシグナル判定
                if sb_mode == MODE_BUY:
                    if rsi <= scr_b_rsi:
                        sigsw_rsi = 1
                        break
                # 売りシグナル判定
                elif sb_mode == MODE_SELL:
                    if rsi >= scr_s_rsi:
                        sigsw_rsi = 1
                        break
            
            if sigsw_rsi == 0:
                continue

        #----------------------
        # MACD判定
        #----------------------
        if judge_macd == True:                  # MACD判定が有効な時に実行
            # 最新のMACDとシグナルの値を取得
            macd = df_price["MACD"].values[-1]
            sig = df_price["Signal"].values[-1]
            # MACD > SIGで買いシグナル
            sigsw_macd = 0
            # 買いシグナル判定
            if sb_mode == MODE_BUY:
                if macd > sig + scr_macd:
                    sigsw_macd = 1
            # 売りシグナル判定
            elif sb_mode == MODE_SELL:
                if macd < sig - scr_macd:
                    sigsw_macd = 1

            if sigsw_macd == 0:
                continue

        #----------------------
        # ブレイクアウト判定
        #----------------------
        if judge_break == True:                  # MACD判定が有効な時に実行
            sigsw_break = 0
            # 最後から指定期間分のレコードを取得
            breakdf = df.tail(scr_break)

            # 指定期間中の前日までで一番の高値を取得
            size = len(breakdf)
            breakdf = breakdf.set_index("datetime")
            breakdf = breakdf.head(size - 1)

            # 買いシグナル判定
            if sb_mode == MODE_BUY:
                df_max = breakdf.rolling(window=size-1).max()
                max = df_max["high"].values[-1]
                # 現在の価格が前日までの指定期間の高値を超えている場合に買いシグナルON
                if i_close > max:
                    sigsw_break = 1
            # 売りシグナル判定
            elif sb_mode == MODE_SELL:
                df_min = breakdf.rolling(window=size-1).min()
                min = df_min["high"].values[-1]
                # 現在の価格が前日までの指定期間の高値を超えている場合に買いシグナルON
                if i_close < min:
                    sigsw_break = 1


            if sigsw_break == 0:
                continue

        #----------------------
        # ここまで残ったコードをリストに追加
        #----------------------
        print(code, ": RSI=", rsi)
        str_close = "¥{:,d}".format(i_close)
        if sb_mode == MODE_BUY:
            lst_codes.append(str(code) + "[新買]:" + str_close)
        if sb_mode == MODE_SELL:
            lst_codes.append(str(code) + "[新売]:" + str_close)

# LINEで結果を通知
line.line_notify(lst_codes)






