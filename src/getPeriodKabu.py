from datetime import datetime, date, timedelta
import sqlight as db
import technical_MACD as tc_macd
import technical_RSI as tc_rsi

############################################
# の株データを指定期間分取得する
############################################
# 日経平均株価()の取得
def getPeriodKabuData(code, past_period, conn, cursor):

    # 個別銘柄 期間データ取得
    today = date.today()                                                                    # 今日(日付型)
    str_date_sta = datetime.strftime(today + timedelta(days = past_period), '%Y-%m-%d')  # 1200日前
    str_date_end = datetime.strftime(today + timedelta(days = 1), '%Y-%m-%d')               # 明日

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
        df['SMA5'] = df['close'].rolling(window=5).mean()               # 5日移動平均を追加
        df['SMA25'] = df['close'].rolling(window=25).mean()             # 25日移動平均を追加
        df['SMA75'] = df['close'].rolling(window=75).mean()             # 75日移動平均を追加
    except:
        print(code + ": Error")
        return (-1)

    if len(df) == 0:
        return (-1)

    df = df.set_index("datetime").loc[:,["open","high","low","close","volume","SMA5","SMA25","SMA75"]]
    # MACDとRSIを追加
    df = tc_macd.macd(df)
    df = tc_rsi.rsi_tradingview(df)

    return df