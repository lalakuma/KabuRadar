import common_def as DEF
import technical_MovingAve as tc_movave
import technical_BreakOut as tc_break
import technical_Beard as tc_beard
import technical_MACD as tc_macd
import technical_RSI as tc_rsi
import sqlight as db
import line
from datetime import datetime, date, timedelta

#****************************
# スクリーニング用の設定値
#****************************
# 移動平均線の傾き確認に使用する値
scr_lineave = 100
# MACDとシグナルの開きに使用する値
scr_macd_offset = 5
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

#--------------------------------------
# 有効判定設定
#--------------------------------------
# 移動平均判定
jdg_mov  = False
# RSI判定
jdg_rsi  = True
# MACD判定
jdg_macd  = True
# BREAK OUT判定
jdg_brk  = True
# 髭判定
jdg_berd = True
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
    # SELL/BUY モード切替  (買い=MODE_BUY, 売り=MODE_SELL)
    # 初回ループはMODE_BUY、2回目はMODE_SELL

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
        # 過去指定日前からのRSIを取得
        dfrsi = df_price.loc[str_bef:,["RSI"]]

        # 全情報をリストに追加
        #lst_dfprice.append(df_price)

    # 銘柄コードで調査用 
 #       if str(code) == "9101":
 #           print(code)
 #           print(df_price)

        # 終値取得
        i_close = df_price["close"].values[-1]                  # 終値取得
        i_open = df_price["open"].values[-1]                    # 始値取得
        i_low = df_price["low"].values[-1]                      # 安値取得
        i_high = df_price["high"].values[-1]                    # 高値取得


        sb_mode = md
        # 買いモードの時
        if sb_mode == DEF.MODE_BUY:     
            limit_in_rsi = scr_b_rsi        # 過去にRSIが閾値内に入ったかチェック用の閾値
            limit_now_rsi = scr_rsi_max     # RSI現在値の購入許可判定閾値
        # 売りモードの時    
        else:                           
            limit_in_rsi = scr_s_rsi        # 過去にRSIが閾値内に入ったかチェック用の閾値
            limit_now_rsi = scr_rsi_min     # RSI現在値の購入許可判定閾値

        #----------------------
        # ローソク足判定
        #----------------------
        # ローソクが陽線か陰線かを判別
        diff = i_close - i_open             # 始値と現在値の差分から実線の長さを設定
        if diff >= 0:
            line_kind = 1                   # ライン種別を陽線に設定
        else:
            line_kind = 0                   # ライン種別を陰線に設定

        # 買いモードかつローソク足が陰線は処理しない
        if sb_mode == DEF.MODE_BUY and line_kind == 0:
            continue
        # 売りモードかつローソク足が陽線は処理しない
        if sb_mode == DEF.MODE_SELL and line_kind == 1:
            continue
        
        #----------------------
        # 移動平均判定
        #----------------------
        if jdg_mov == True:                  # 移動平均判定が有効な時に実行
            if tc_movave.jdg_movave_trend(sb_mode, df) == 0:
                continue
        #----------------------
        # RSI判定
        #----------------------
        if jdg_rsi == True:                  
            # RSIの現在値が購入許可できる水準かを判定
            if tc_rsi.jdg_rsi_level(sb_mode, dfrsi, limit_now_rsi) == 0:
                continue
            # 過去指定期間でRSIが指定値を閾値を超えたらRSIシグナルスイッチを1にする
            if tc_rsi.jdg_rsi_entered(sb_mode, dfrsi, limit_in_rsi) == 0:
                continue
        #----------------------
        # MACD判定
        #----------------------
        if jdg_macd == True:                  
            # MACDのクロスが発生した後かを判定
            if tc_macd.jdg_macd_cross(sb_mode, df_price, scr_macd_offset) == 0:
                continue
        #----------------------
        # ブレイクアウト判定
        #----------------------
        if jdg_brk == True:
            if tc_break.jdg_break_out(sb_mode, df, scr_break, i_close) == 0:
                continue
        #----------------------
        # 髭判定
        #----------------------
        if jdg_berd == True:
            if tc_beard.jdg_beard(sb_mode, i_open, i_high, i_low, i_close) == 0:
                continue
        #----------------------
        # ここまで残ったコードをリストに追加
        #----------------------
        print(code)
        str_close = "¥{:,d}".format(i_close)
        if sb_mode == DEF.MODE_BUY:
            lst_codes.append(str(code) + "[新買]:" + str_close)
        if sb_mode == DEF.MODE_SELL:
            lst_codes.append(str(code) + "[新売]:" + str_close)

# LINEで結果を通知
line.line_notify(lst_codes)
