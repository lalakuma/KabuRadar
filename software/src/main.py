import pandas as pd
import mplfinance as mpf
import technical_MACD as tc_macd
import technical_RSI as tc_rsi
import sqlight as db
from datetime import date
#--------------------------------------
# DBから全銘柄コードを取得
#--------------------------------------
# DBに接続
conn, cursor = db.connect_db()

lst_dfprice = []

# 個別銘柄 全データ取得
#df_price = db.read_rec_all(conn, cursor, "tbl_1332")

# 個別銘柄 期間データ取得
today = str(date.today())

date_sta = "2021-05-01"
date_end = today

# 全銘柄コードリスト取得
#codes = db.read_code_all(cursor, "tbl_codelist")

# 銘柄コードリストに登録されている全コードに対して処理を行う
#for code in codes:
# 指定期間のデータをDBから読み出す
df = db.read_rec_period(conn, cursor, "1321", date_sta, date_end)
#df.columns = ["datetime","open","high","low","close","volume"]
df['datetime'] = df['datetime'].astype('datetime64')
df['open'] = df['open'].astype('int64')
df['high'] = df['high'].astype('int64')
df['low'] = df['low'].astype('int64')
df['close'] = df['close'].astype('int64')
df['volume'] = df['volume'].astype('int64')

#日付をインデックスにして、必要なアイテム順に並び替え
df_daily = df.set_index("datetime").loc[:,["open","high","low","close","volume"]]

df_daily = tc_macd.macd(df_daily)
df_daily = tc_rsi.rsi(df_daily)    
#lst_dfprice.append(df_price)

print(lst_dfprice)

#df_daily.head()

add_plot = [
    mpf.make_addplot(df_daily['MACD'], color='r',panel=1,secondary_y=False),
    mpf.make_addplot(df_daily['Signal'], color='g',panel=1,secondary_y=False),    
    mpf.make_addplot(df_daily['RSI'], color='b',panel=2,secondary_y=False),    
]
mpf.plot(df_daily,type="candle", volume_panel=3, volume=True,mav=(5,13),addplot=add_plot)
mpf.show()
