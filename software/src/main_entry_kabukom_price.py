####################################################################
# ① データベースのtbl_nameから銘柄コードを読みだす
# ② au Kabukomu のApiを使用して読み出した銘柄コードの株価情報を取得する
# ③ 取得した株価情報をデータベースに保存する（銘柄毎にテーブルを作成）
####################################################################
import pandas as pd
import KabukomApi.kabusapi_token as token
import KabukomApi.kabusapi_board as board
import KabukomApi.kabusapi_unregisterall as unregiall
import sqlight as db

#--------------------------------------
# DBから全銘柄コードを取得
#--------------------------------------
# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

#--------------------------------------
# KabukomApiで価格情報を取得
#--------------------------------------
# APIにてトークン取得
tkn = token.getToken('morino12345')

for code in codes:
    # 登録銘柄全削除（レジスト数エラー対策）
    unregiall.unregisterall(tkn["Token"])
    # APIにて現時点の板情報を取得する
    content = board.get_board(tkn["Token"], code)

     # ['日付', 'コード', '始値', '高値', '安値', '終値', '終値調整', '出来高']を抽出
    lst_price = []
    date = content["CurrentPriceTime"]
    if date != None:
        lst_price += [date[0:10]]      
        lst_price += [code]      
        lst_price += [str(content["OpeningPrice"])]      
        lst_price += [str(content["HighPrice"])]      
        lst_price += [str(content["LowPrice"])]      
        lst_price += [str(content["CurrentPrice"])]      
        lst_price += [str(content["CalcPrice"])]      
        lst_price += [str(content["TradingVolume"])]      

        # 個別株価情報テーブルを作成
        db.create_nametbl(conn, cursor, code)
        # 株価情報をデータベースに保存
        db.marge_price_1record(conn, cursor, "tbl_" + code, lst_price)     # マージ
        print()
        # API実行回数エラーにならないようにスリープを入れる
#        time.sleep(100/1000)    



