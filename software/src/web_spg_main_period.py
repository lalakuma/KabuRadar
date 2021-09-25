##########################
# 1銘柄(期間)取得
##########################
import web_spg
import sqlight as db

# DBオープン
conn, cursor = db.connect_db()

web_spg.get_kabuka_period()

# DBクローズ
db.close_db(conn)
