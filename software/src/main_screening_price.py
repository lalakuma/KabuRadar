#********************************** 
# 指定した日付と価格の銘柄を検索する
#**********************************
import common_def as DEF
import technical_MovingAve as tc_movave
import technical_BreakOut as tc_break
import technical_Beard as tc_beard
import technical_MACD as tc_macd
import technical_RSI as tc_rsi
import technical_Bollinger as tc_bb
import sqlight as db
import line
from datetime import datetime, date, timedelta

#****************************
# スクリーニング用の設定値
#****************************
srch_price_close = 0     # 検索したい終値(未指定は0を入力)
srch_price_high = 0   # 検索したい高値(未指定は0を入力)
srch_price_low = 378       # 検索したい安値(未指定は0を入力)
srch_date = '2023-03-16' # 検索したい日付
#--------------------------------------
# DBから全銘柄コードを取得
#--------------------------------------
str_date_sta = srch_date
str_date_end = srch_date

# DBに接続
conn, cursor = db.connect_db2('..\\..\\DB\\全ALL\\KabuRadar.db')

#lst_dfprice = []
lst_low_rsi = []
lst_codes = []

# 個別銘柄 期間データ取得
today = date.today()                                                                    # 今日(日付型)
#str_date_sta = srch_date
#str_date_end = srch_date

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
    except:
    #    print(code + ": Error")
        continue        
    
    #日付をインデックスにして、必要なアイテム順に並び替え
    df_price = df.set_index("datetime").loc[:,["open","high","low","close","volume"]]

    if df_price["close"].empty == True:
        continue

    if df_price["close"].values[-1] == None:
        continue

    # 終値取得
    i_close = df_price["close"].values[-1]                  # 終値取得
    i_high = df_price["high"].values[-1]                  # 終値取得
    i_low = df_price["low"].values[-1]                  # 終値取得

    if srch_price_close != 0:        
        if i_close == srch_price_close:
            print("見つけました!! コード = " + code)
        
    if srch_price_high != 0:        
        if i_high == srch_price_high:
            print("見つけました!! コード = " + code)

    if srch_price_low != 0:        
        if i_low == srch_price_low:
            print("見つけました!! コード = " + code)

print("終了しました")