####################################################
#   ヤフーファイナンスAPI株価を取得する
#   取得した株価をデータベースに登録する
# 　但し、既にテーブルが存在する場合は差し替える 
####################################################
from numpy import add, true_divide
import sqlight as db
import get_yahoo_api as yahoo
from enum import Enum

class Order(Enum):
    RAPLACE = 0     # 重複時は全て差し替え
    APPEND  = 1     # 新規の追加のみ（重複時は処理なし）

proc_order = Order.APPEND

# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

ptype = "year"
period = 5     # 期間(年)
frequency = 1   # 日足

# 現在DBに登録されている全テーブルリストを取得
lst_tbl = db.get_tablelist(conn, cursor)

# 銘柄コードリストに登録されている全コードに対して処理を行う
for code in codes:
    # 処理要求が追加の時
    if proc_order == Order.APPEND:
        strtbl = "tbl_" + code
        # 既に存在するテーブルには処理しない
        if not strtbl in lst_tbl:
            # ヤフーAPIにより株価データ取得
            df_daily = yahoo.get_pricedata(code, ptype, period, frequency)
            # DBに保存(既存テーブルがある場合は差し替え)
            db.replace_df_records(conn, code, df_daily)
    # 処理要求が差し替えの時
    else:
        # ヤフーAPIにより株価データ取得
        df_daily = yahoo.get_pricedata(code, ptype, period, frequency)
        # DBに保存(既存テーブルがある場合は差し替え)
        db.replace_df_records(conn, code, df_daily)

    print(code)

# DBクローズ
db.close_db(conn)
