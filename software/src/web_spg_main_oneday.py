##########################
# 1銘柄(最新1日)取得
##########################
import web_spg
import sqlight as db
from typing import List, Tuple

# DBオープン
conn, cursor = db.connect_db()

db.create_nametbl(conn, cursor)

df_name, df_price = web_spg.get_Kabuka_oneday()

#tuples = [Tuple(x) for x in df_name.values]

for x in df_name.values:
    tuples = x

db.add_price_one_record(conn, cursor, 'tbl_codelist', tuples)

# DBクローズ
db.close_db(conn)