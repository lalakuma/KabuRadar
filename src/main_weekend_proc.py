#########################################
# 週末に実行する処理
# DBのopenにnullのあるレコードを削除
#########################################
####################################################
#   ヤフーファイナンスAPI株価を取得する
#   取得した株価をデータベースに登録する
# 　但し、既にテーブルが存在する場合は差し替える 
####################################################
import sqlight as db
import get_yahoo_api as yahoo
import time

# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

# 銘柄コードリストに登録されている全コードに対して処理を行う
for code in codes:
    # nullレコードの削除
    db.del_null_rec(conn, cursor, code)

# DBクローズ
db.close_db(conn)