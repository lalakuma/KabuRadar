####################################################
#   HYPER SBIから出力したCSVファイルより株価を取得する
#   既にテーブルが存在する場合は削除して再登録 
#   1ファイルでも複数ファイルでもOK
#   ファイル名はこんな感じにしておく→ TimeChart1321.csv
#   登録したいcsvをentryフォルダに格納してから実行し、
#   完了するとcompフォルダに移動される。
####################################################
import pandas as pd
import numpy  as np
import sqlight as db
import glob
import shutil
import pathlib

def csv_get_all():
    # DBに接続
    conn, cursor = db.connect_db()
    # 全銘柄コードリスト取得
    codes = db.read_code_all(cursor, "tbl_codelist")

    # entryフォルダからcsvファイルのリストを作成
    files = glob.glob("../../Input/CSV/entry/*.csv")
    #files = pathlib.Path('../../Input/CSV/entry').glob('*.csv')
    # 検出したファイル数分繰り返す
    for file in files:
        pos = file.find('TimeChart') + 9
        # ファイル名から銘柄コードを抽出
        csv_code = file[pos:pos + 4]
        print(csv_code)

        # CSVファイル読み込み
        csv_input = pd.read_csv(filepath_or_buffer="..\..\Input\CSV\entry\TimeChart" + csv_code + ".csv", encoding="utf-8-sig", sep=",")

        # 必要な項目をリストに追加
        lst_price = []
        # 必要な項目のみ抽出してリストを作成
        for i, row in csv_input.iterrows():
            dt = str(row["日付"])[0:4] + "-" + str(row["日付"])[5:7] + "-" + str(row["日付"])[8:10]
#            dt = str(row["日付"])[0:4] + "-" + str(row["日付"])[4:6] + "-" + str(row["日付"])[6:8]
#            opn = str(int(row["始値"]))
            opn = str(float(str(row["始値"]).replace(",", "")))
            hi = str(float(str(row["高値"]).replace(",", "")))
            low = str(float(str(row["安値"]).replace(",", "")))
            cur = str(float(str(row["終値"]).replace(",", "")))
            vol = str(int(str(row["出来高"]).replace(",", "")))
            tpl = (dt, opn, hi, low, cur, vol)
            lst_price.append(tpl)

        isFind = False
        # 既にDBに登録されているコードを検索して一致するものがあるかチェック
        for code in codes:
            # 同一コードがある場合
            if code == csv_code:
                # テーブル削除
                db.delete_tbl(conn, "tbl_" + code)
                break

        # テーブルを作成
        db.create_nametbl(conn, cursor, csv_code)
        # 全レコード登録 (0番目の要素をキーとして昇順にソート)
        lst_price.sort(key=lambda x: x[0])
        db.add_records(conn, csv_code, lst_price)

        # 登録の終わったcsvファイルを完了フォルダに移動する
        shutil.move(file, '../../Input/CSV/comp/')

    # DBクローズ
    db.close_db(conn)


csv_get_all()