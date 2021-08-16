####################################################
#   ヤフーファイナンスAPI株価を取得する
#   取得した株価をデータベースに登録する
# 　但し、既にテーブルが存在する場合は差し替える 
####################################################
import sys
import pandas as pd
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import datetime 

def get_pricedata(code, ptype, peri, freq):
    my_share = share.Share(code + '.T')
    symbol_data = None
    
    if ptype == "year":
        peri_type = share.PERIOD_TYPE_YEAR
    else:
        peri_type = share.PERIOD_TYPE_DAY


    try:
        symbol_data = my_share.get_historical(
            peri_type, peri,
            share.FREQUENCY_TYPE_DAY, freq)
        
    except YahooFinanceError as e:
        print(e.message)
        sys.exit(1)
    
    df = pd.DataFrame(symbol_data)
    if df.size > 0:
        df["datetime"] = pd.to_datetime(df.timestamp, unit="ms")    
        # 日本時間へ変換
        df["datetime"] = df["datetime"] + datetime.timedelta(hours=9)
        # データ型を設定　(数値はNaNが含まれるとintegerにできないので浮動小数点型にする)
        df['datetime'] = df['datetime'].astype('datetime64')

        #日付をインデックスにして、必要なアイテム順に並び替え
        df_daily = df.set_index("datetime").loc[:,["open","high","low","close","volume"]]
    else:
        df_daily = df

    return(df_daily)

