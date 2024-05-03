####################################################################
# ① エクセル(銘柄コード.xlsx)から銘柄コードを読み込む
# ② 読み込んだコードに対して株探サイトからスクレイピングして情報を取得
# ③ 取得した情報をデータベースに格納する
####################################################################
import pandas as pd
from pyquery import PyQuery
import time
import sqlight as db

####################################################################
# 関数：株探サイトから銘柄情報を取得する
####################################################################
def get_brand(code):
    url='https://kabutan.jp/stock/?code={:04}'.format(code)
    q=PyQuery(url)
    
    if len(q.find('span.market'))==0:
        return None
    
    try:
#        name = q.find('div.company_block >h3')[0].text
        market=q.find('span.market').text()
        short_name = q.find('.si_i1_1').remove('span').remove('time').text()
        sector=q.find('#stockinfo_i2 a')[0].text
#        unit_str=q.find('#stockinfo_i2 :eq(2) >dd').text()
#        unit=int(unit_str.replace('株','').replace(',',''))
        
        return code,short_name,market,sector
    
    except ValueError:
        return None


####################################################################
# 関数：メイン
####################################################################
def entry_codelist():
    #--------------------------------------
    # エクセルから銘柄コードを読み込む
    #--------------------------------------
    df = pd.read_excel('../../Input/XLS/銘柄コード.xlsx',index_col=0)
    print(df)

    # DBに接続
    conn, cursor = db.connect_db()
    # コードリストテーブル作成（既にある場合は作成しない）
    db.create_codelisttbl(conn, cursor)  
    # コード設定テーブル作成（既にある場合は作成しない）
    db.create_codesettbl(conn, cursor)  
    #--------------------------------------
    # 銘柄情報を取得してデータベースに書き込む
    #--------------------------------------
    # エクセルから取得したコード分すべて回す

    for code, value in df.iterrows():
        # コードリストテーブルに指定コードが既にDBに存在するかチェックする
        exi = db.exist_data(cursor, 'tbl_codelist', 'code', str(code))
        # 未登録の場合に処理を行う
        if exi == False:
            # 銘柄情報をスクレイピング
            brand = get_brand(code)
            newbrand = brand + (value[1],)
            print(newbrand)
            # DBに1レコード追加
            db.marge_codelist_1record(conn, cursor, "tbl_codelist", newbrand) 

        # コード設定テーブルに指定コードが既にDBに存在するかチェックする
        exi = db.exist_data(cursor, 'tbl_code_set', 'code', str(code))
        # 未登録の場合に処理を行う
        if exi == False:
            # コードと有効設定を登録（登録時は無効。後で有益性をチェックしてから有効にする為）
            df_ena = pd.DataFrame(columns=['code', 'Enable', 'PF'])
            df_ena = df_ena.append({'code': code, 'Enable': '1', 'PF': '0'}, ignore_index=True)
            df_ena = df_ena.set_index('code')
            # DBに1レコード追加
            db.add_settbl_record(conn, df_ena) 

        # サーバに負荷をかけないように休止
        #time.sleep(1)

    # DBクローズ
    db.close_db(conn)

    
#######################    
#  実行
#######################    
entry_codelist()

