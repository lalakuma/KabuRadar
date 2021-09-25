#########################################
# 週末に実行する処理
# DBのopenにnullのあるレコードを削除
#########################################
import sqlight as db

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