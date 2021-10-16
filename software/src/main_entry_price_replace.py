####################################################
#   指定期間の株価をまとめて入れ替える（デフォルトは10日間）
#   (データが抜けてたり重複してたり異常な時に使うとよい)
####################################################
from numpy import add, true_divide
import sqlight as db
import get_yahoo_api as yahoo
from enum import Enum
from datetime import datetime, date, timedelta

# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

ptype = "day"
period = 10     # 期間(日)
frequency = 1   # 日足

# 現在DBに登録されている全テーブルリストを取得
lst_tbl = db.get_tablelist(conn, cursor)

# 銘柄コードリストに登録されている全コードに対して処理を行う
for code in codes:
    strtbl = "tbl_" + code
    # 存在するテーブルのみ処理する
    if strtbl in lst_tbl:
        # ヤフーAPIにより株価データ取得
        df_daily = yahoo.get_pricedata(code, ptype, period, frequency)
        print(df_daily)

        if df_daily.empty == False:
            idx = df_daily.index[0]
            str_date = str(idx)

            # 指定日以降のレコードを削除
            db.del_price_after_date(conn, cursor, code, str_date)

            # DBにレコードを追加
            db.add_df_records(conn, code, df_daily)

    print(code)

# DBクローズ
db.close_db(conn)
