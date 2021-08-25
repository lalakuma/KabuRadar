import common_def as DEF
import sqlight as db
import backtest_proc as bktst
import line
from datetime import datetime, date, timedelta
import getPeriodKabu as pkabu
import technical_BreakOut as tc_break
import technical_Beard as tc_beard

lst_codes = []

#****************************
# スクリーニング用の設定値
#****************************
# ブレイクアウト判定期間に使用する値
scr_break = 5
#--------------------------------------
# 有効判定設定
#--------------------------------------
# BREAK OUT判定
jdg_brk  = True
# 髭判定
jdg_berd = True
#--------------------------------------
# DBから全銘柄コードを取得
#--------------------------------------
# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

# データ取得期間に過去80日間を指定(75日移動平均線を使用する為)
PAST_PERIOD=(-150)
CD_NIKKEI = 1321    # 日経平均ETF
code = CD_NIKKEI

# 指標株価を取得する
df_indicator = pkabu.getPeriodKabuData(code, PAST_PERIOD, conn, cursor)

# 個別銘柄 期間データ取得
today = date.today()                                                                    # 今日(日付型)
str_date_sta = datetime.strftime(today + timedelta(days = PAST_PERIOD), '%Y-%m-%d')     # 開始日(移動平均線を出せる日付を指定)
str_date_end = datetime.strftime(today + timedelta(days = 1), '%Y-%m-%d')               # 明日
str_today = datetime.strftime(today, '%Y-%m-%d')                                        # 今日
str_bef = datetime.strftime(today + timedelta(days = PAST_PERIOD), '%Y-%m-%d')          # 指定日前

# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

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
    except:
        print(code + ": Error")
        continue        

    #日付をインデックスにして、必要なアイテム順に並び替え
    df_price = df.set_index("datetime").loc[:,["open","high","low","close","volume","SMA5","SMA25"]]

    # 終値取得
    i_close = df_price["close"].values[-1]                  # 終値取得
    i_open = df_price["open"].values[-1]                    # 始値取得
    i_low = df_price["low"].values[-1]                      # 安値取得
    i_high = df_price["high"].values[-1]                    # 高値取得

    # 指標株価の個別データを取得
    ind_sma75 = int(df_indicator["SMA75"].values[-1])
    ind_close = df_indicator["close"].values[-1]

    # 指標銘柄の75日線より売買モードを設定
    if ind_sma75 > ind_close:
        sb_mode = DEF.MODE_SELL
    else:
        sb_mode = DEF.MODE_BUY  

    # 銘柄コードで調査用 
    if str(code) == "1801":
        print(code)
        print(df_price)

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

# DBクローズ
db.close_db(conn)
