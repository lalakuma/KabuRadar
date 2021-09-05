import common_def as DEF
import sqlight as db
import backtest_proc as bktst
import line
from datetime import datetime, date, timedelta
import getPeriodKabu as pkabu
import technical_BreakOut as tc_break
import technical_Beard as tc_beard
import pandas as pd

lst_codes = []

#****************************
# スクリーニング用の設定値
#****************************
# ブレイクアト判定期間に使用する値
scr_break = 6
#--------------------------------------
# 有効判定設定
#--------------------------------------
# ローソク判定
jdg_candle  = True
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
PAST_PERIOD=(-20)
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

# 設定テーブル 全データ取得
df_set = db.read_rec_all(conn, cursor, "tbl_code_set")
df_set = df_set.set_index('code')

# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")
sb_mode = DEF.MODE_BUY

# スクリーニング結果格納用データフレーム
cols = ["code","PF","mark","close"]
df_rlt = pd.DataFrame(index=[], columns=cols)

# 銘柄コードリストに登録されている全コードに対して処理を行う
for code in codes:
    #codeが無効に設定されている場合は処理しない
    code_ena = df_set.at[str(code), 'Enable']
    if code_ena == 0:
        continue

    # PF取得
    code_PF = df_set.at[str(code), 'PF']


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
#    ind_sma75 = int(df_indicator["SMA75"].values[-1])
    ind_close = df_indicator["close"].values[-1]

    # 銘柄コードで調査用 
#    if str(code) == "1801":
#        print(code)
#        print(df_price)


    #----------------------
    # 価格判定
    #----------------------
    # 最新価格が10000を超える株は対象外とする（資金的にまだ早い）
    if i_close > 10000:
        continue
    #----------------------
    # ローソク足判定
    #----------------------
    if jdg_candle == True:
        # ローソクが陽線か陰線かを判別
        diff = i_close - i_open             # 始値と現在値の差分から実線の長さを設定
        if diff >= 0:
            line_kind = 1                   # ライン種別を陽線に設定
        else:
            line_kind = 0                   # ライン種別を陰線に設定

        # ローソクの大きさが1%未満は処理しない (2%にしたら悪くなった)
        if abs(diff) < abs(i_close * 0.01):
            continue
        # 買いモードかつローソク足が陰線は処理しない
        if sb_mode == DEF.MODE_BUY and line_kind == 0:
            continue
        # 売りモードかつローソク足が陽線は処理しない
        if sb_mode == DEF.MODE_SELL and line_kind == 1:
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
    str_close = "¥{:,d}".format(i_close)
    if sb_mode == DEF.MODE_BUY:
#        strmsg = str(code) + "[PF]" + str(code_PF) + ", [新買]" + str_close
        df_rlt=df_rlt.append({'code' : str(code), 'PF' : code_PF, 'mark' : '新買', 'close' : str_close} , ignore_index=True)
    if sb_mode == DEF.MODE_SELL:
#        strmsg = str(code) + "[PF]" + str(code_PF) + ", [新売]" + str_close
        df_rlt=df_rlt.append({'code' : str(code), 'PF' : code_PF, 'mark' : '新売', 'close' : str_close} , ignore_index=True)
#    lst_codes.append(strmsg)

#--------------------------------
# スクリーニング結果出力処理
#--------------------------------
df_rlt = df_rlt.sort_values("PF", ascending=False)    # 高PF順にソート
# LINE送信用の文字列リストを作成
for row_rlt in df_rlt.itertuples():
    strmsg = row_rlt.code + "[PF:" + str(row_rlt.PF) + "][" +  row_rlt.mark + "] " + row_rlt.close
    lst_codes.append(strmsg)

# LINEで結果を通知
line.line_notify(lst_codes)

# DBクローズ
db.close_db(conn)
