####################################################
#   ヤフーファイナンスAPI株価を取得する
#   取得した株価をデータベースに登録する
# 　但し、既にテーブルが存在する場合は差し替える 
####################################################
import sqlight as db
import get_yahoo_api as yahoo
import time
import logging

#----------------------------------------
# LOG設定
#----------------------------------------
sth = logging.StreamHandler()
flh = logging.FileHandler('../../output/log/debug.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                    handlers=[sth, flh])
logger = logging.getLogger(__name__)
logger.info("処理 main_entry_price_one を開始します。")

# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

ptype = "day"
period = 1     # 期間(日)
frequency = 1   # 日足

# 銘柄コードリストに登録されている全コードに対して処理を行う
for code in codes:
    df_daily = yahoo.get_pricedata(code, ptype, period, frequency)
    df_daily = df_daily.tail(1)
    if df_daily.size > 0:    
        # テーブルを作成
        db.create_nametbl(conn, cursor, code)

        print(df_daily)
        # 最新レコードのみを登録
        db.one_marge_df_records(conn, cursor, code, df_daily)
        print(code)
#        time.sleep(1)
    
# DBクローズ
db.close_db(conn)
