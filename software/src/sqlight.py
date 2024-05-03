#%%
import sqlite3
from typing import List, Tuple
from numpy import true_divide
from numpy.lib.function_base import append
import pandas as pd
import datetime
import getConfig as conf

##########################################################################
#   DBに接続する
##########################################################################
def connect_db():
    dbname = conf.get_config(conf.CONF_SEC_DATABASE, conf.CONF_KEY_PATH_DB)
    conn = sqlite3.connect(dbname, isolation_level=None)#データベースを作成、自動コミット機能ON

    cursor = conn.cursor() #カーソルオブジェクトを作成

    return conn, cursor
##########################################################################
#   DBに接続する
##########################################################################
def connect_db2(dbname):
    conn = sqlite3.connect(dbname, isolation_level=None)#データベースを作成、自動コミット機能ON

    cursor = conn.cursor() #カーソルオブジェクトを作成

    return conn, cursor

##########################################################################
#   トレード結果履歴テーブルを作成する
##########################################################################
def create_tradehist(conn, cursor):
    """ create a table in the SQLite database"""
    sql = """CREATE TABLE IF NOT EXISTS TradeHist (
            "Index" DATE,
            "code" INTEGER,
            "open" INTEGER,
            "close" INTEGER,
            "PF" REAL,
            "mark" TEXT,
            "buygain" INTEGER,
            "sellgain" INTEGER,
            "latent" INTEGER,
            "income" INTEGER,
            "name" TEXT,
            "sangyou" TEXT
        ); """
    cursor.execute(sql)
    conn.commit()

##########################################################################
#   銘柄リストテーブルを作成する
#   (既に存在する場合は作成しない)
##########################################################################
def create_codelisttbl(conn, cursor):
    """
    ・create table テーブル名（作成したいデータカラム）というSQL文でテーブルを宣言
    　　※SQL命令は大文字でも小文字でもいい
    ・今回はtestテーブルに「id,name,date」カラム(列名称)を定義する※今回dateは生年月日という列
    ・「if not exists」はエラー防止の部分。すでに同じテーブルが作成されてるとエラーになる為
    ・カラム型は指定しなくても特には問題ない
    　　※NULL, INTEGER(整数), REAL(浮動小数点), TEXT(文字列), BLOB(バイナリ)の5種類
    """
    sql = 'create table if not exists tbl_codelist(code text PRIMARY KEY, Name text NOT NULL, Sijou text, Sangyou text, Sisuu text)'
    cursor.execute(sql)#executeコマンドでSQL文を実行
    
    conn.commit()

##########################################################################
#   銘柄毎の設定情報テーブルを作成する
#   (既に存在する場合は作成しない)
##########################################################################
def create_codesettbl(conn, cursor):
    sql = 'create table if not exists tbl_code_set(code text PRIMARY KEY, PF real, Enable integer)'
    cursor.execute(sql)#executeコマンドでSQL文を実行
    
    conn.commit()

##########################################################################
#   全テーブルのリストを取得
##########################################################################
def get_tablelist(conn, cursor):
    # ['日付', '始値', '高値', '安値', '現値', '出来高']
    sql = 'select name from sqlite_master where type="table"'

    cursor.execute(sql)#for文で作成した全テーブルを確認していく
    tpl_tbl = cursor.fetchall()

    lst_tbl = []
    for tpl in tpl_tbl:
        lst_tbl.append(tpl[0])

    return lst_tbl
    
##########################################################################
#   個別株価情報テーブルを作成する
#   (既に存在する場合は作成しない)
##########################################################################
def create_nametbl(conn, cursor, code):
    """
    ・create table テーブル名（作成したいデータカラム）というSQL文でテーブルを宣言
    　　※SQL命令は大文字でも小文字でもいい
    ・「if not exists」はエラー防止の部分。すでに同じテーブルが作成されてるとエラーになる為
    ・カラム型は指定しなくても特には問題ない
    　　※NULL, INTEGER(整数), REAL(浮動小数点), TEXT(文字列), BLOB(バイナリ)の5種類
    """
    # ['日付', '始値', '高値', '安値', '現値', '出来高']
    sql = 'create table if not exists tbl_' + code + '(datetime text PRIMARY KEY, open real, high real, low real, close real, volume integer)'

    cursor.execute(sql)#executeコマンドでSQL文を実行
    
    conn.commit()

##########################################################################
#   テーブル名を読みだす
##########################################################################
def read_tblname(conn, cursor):
    sql = """SELECT name FROM sqlite_master WHERE TYPE='table'"""
    pd.read_sql_query('SELECT name FROM sqlite_master WHERE TYPE="table"', conn)

    for t in cursor.execute(sql):#for文で作成した全テーブルを確認していく
        print(t)

##########################################################################
#   指定レコードの存在チェック
##########################################################################
def exist_data(cursor, tbl, clm, joken):
    """
    SELECT EXISTS(SELECT * テーブル名 WHERE カラム名 = ’条件’)
    """
    sql = 'SELECT EXISTS(SELECT * FROM ' + tbl + ' WHERE ' + clm + ' = "' + joken + '")'

    #命令を実行
    cursor.execute(sql)

    result=cursor.fetchone()#データを1行抽出
    if result[0] == 0:
        return False
    else:
        return True

##########################################################################
#   テーブルに1レコードを追加する
##########################################################################
#def add_price_one_record(conn, cursor, tbl, data):
#    """
#    レコードを追加する場合はinsert文を使う。
#    SQLインジェクションという不正SQL命令への脆弱性対策でpythonの場合は「？」を使用して記載するのが基本。
#    """
#    sql = 'INSERT INTO ' + tbl + ' VALUES(?, ?, ?, ?, ?, ?, ?, ?)'      #?は後で値を受け取るよという意味#

#    cursor.execute(sql, data)#executeコマンドでSQL文を実行
#    conn.commit()#コミットする

##########################################################################
#   1レコードを更新
##########################################################################
#def update_record(conn, cursor, tbl, data):

# # ?=['日付', 'コード', '始値', '高値', '安値', '現値', '計算現値', '出来高']
#    sql = 'UPDATE ' + tbl + ' VALUES(?, ?, ?, ?, ?, ?, ?, ?)'      #?は後で値を受け取るよという意味

#    cursor.execute(sql, data)#executeコマンドでSQL文を実行

#    sql = 'UPDATE ' + tbl + ' SET name=""Bobby"", date=""19880116"" WHERE id=0'
#    cursor.execute(sql)#executeコマンドでSQL文を実行
#    conn.commit()#コミットする

##########################################################################
#   コード設定テーブルに1レコードを追加する(DF版)
#   既にレコードがある場合は削除してから追加する
##########################################################################
def add_settbl_record(conn, df):
    # データベースに追加
    # code, Enable
    print(df)
    df.to_sql('tbl_code_set', conn, if_exists = 'append')

##########################################################################
#   コード設定テーブルのPF設定を更新
##########################################################################
def update_codeset(conn, cursor, tbl, df):
    sql = 'UPDATE ' + tbl + ' SET PF=' + str(df.pf) + ', Enable=' + df.Enable + ' WHERE code=' + str(df.code)
    cursor.execute(sql)#executeコマンドでSQL文を実行
    conn.commit()#コミットする

##########################################################################
#   マージ (codelist)
##########################################################################
def marge_codelist_1record(conn, cursor, tbl, data):
    if data is None:
        return

    sql = 'INSERT INTO ' + tbl + \
    ' VALUES("' + str(data[0]) + '","' + data[1] + '","' + data[2] + '","'+ data[3] + '","' + data[4] + '")' + \
    ' on conflict (code) DO UPDATE SET' + \
    ' code="' + str(data[0]) + '"' + \
    ',Name="' + data[1] + '"' + \
    ',Sijou="' + data[2] + '"' + \
    ',Sangyou="' + data[3] + '"' + \
    ',Sisuu="' + data[4] + '"' + ';'
    
    print(sql)
    #命令を実行
    conn.execute(sql)
    conn.commit()#コミットする

##########################################################################
#   マージ (price)
##########################################################################
def marge_price_1record(conn, cursor, tbl, data):

    sql = 'INSERT INTO ' + tbl + \
    ' VALUES("' + data[0] + '","' + data[1] + '","' + data[2] + '","' + data[3] + '","' + data[4] + '","' + data[5] + '")' + \
    ' on conflict (datetime) DO UPDATE SET' + \
    ' datetime="' + data[0] + '"' + \
    ',open="' + data[1] + '"' + \
    ',high="' + data[2] + '"' + \
    ',low="' + data[3] + '"' + \
    ',close="' + data[4] + '"' + \
    ',volume="' + data[5] + '"' + ';'
 
    print(sql)
    #命令を実行
    conn.execute(sql)
    conn.commit()#コミットする


##########################################################################
#   テーブルに複数レコードを追加する
##########################################################################
def add_records(conn, code, lst_price):
    sql = 'INSERT INTO tbl_' + code + ' (datetime, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)'
    conn.executemany(sql, lst_price)

##########################################################################
#   テーブルに1レコードを追加する(DF版)
#   既にレコードがある場合は削除してから追加する
##########################################################################
def one_marge_df_records(conn, cursor, code, df):

    idx = df.index[-1]
    str_date = str(idx)
#    str_date = str(idx.date())

    # 同一日付のレコードをデータベースから削除
    del_price_one_rec(conn, cursor, code, str_date)

    # データベースに追加
    # datetime, open, high, low, close, volume
    df.to_sql('tbl_' + code, conn, if_exists = 'append')

##########################################################################
#   テーブルにレコードをまとめて追加する(DF版)
##########################################################################
def add_df_records(conn, code, df):
    # データベースに追加
    # datetime, open, high, low, close, volume
    df.to_sql('tbl_' + code, conn, if_exists = 'append')

##########################################################################
#   銘柄テーブルを置き換える(DF版)
##########################################################################
def replace_df_records(conn, code, df):    
    # datetime, open, high, low, close, volume
    df.to_sql('tbl_' + code, conn, if_exists = 'replace')

##########################################################################
#   指定した期間の株価データを読みだす
##########################################################################
def read_rec_period(conn, cursor, code, start, end):
#    sql = 'SELECT * FROM tbl_' + code
#    sql = 'SELECT * FROM tbl_' + code + ' WHERE datetime >= "' + start +'" AND datetime <= "' + end + '"';
    sql = 'SELECT * FROM tbl_' + code + ' WHERE datetime BETWEEN "' + start +'" AND "' + end + '"';

    df = pd.read_sql(sql, conn)
    return df

##########################################################################
#   全レコードを読みだす
##########################################################################
def read_rec_all(conn, cursor, tbl):
    """
    select * ですべてのデータを参照し、fromでどのテーブルからデータを呼ぶのか指定
    fetchallですべての行のデータを取り出す
    """
    sql = 'SELECT * FROM ' + tbl
#    cursor.execute(sql)
#    print(cursor.fetchall())#全レコードを取り出す
    df = pd.read_sql(sql, conn)

    return df

##########################################################################
#   指定Codeのレコードを読みだす
##########################################################################
def read_code_record(conn, cursor, code):
    """
    select * ですべてのデータを参照し、fromでどのテーブルからデータを呼ぶのか指定
    fetchallですべての行のデータを取り出す
    """
    sql = 'SELECT * FROM ' + 'tbl_codelist ' + 'WHERE ' + 'Code = ' + '"' + str(code) + '"'
    cursor.execute(sql)
    #df = pd.read_sql(sql, conn)
    for cd in cursor.fetchall():
        name = cd[1]
        sangyou = cd[3]
#    coderec = [cd[0] for cd in cursor.fetchall()]
    return name, sangyou

##########################################################################
#   全銘柄コードリスト取得
##########################################################################
def read_code_all(cursor, tbl):
    """
    select * ですべてのデータを参照し、fromでどのテーブルからデータを呼ぶのか指定
    fetchallですべての行のデータを取り出す
    """
    sql = 'SELECT * FROM ' + '"' + tbl + '"'
    cursor.execute(sql)
    #result = cursor.fetchall() #全レコードを取り出す
    codes = [cd[0] for cd in cursor.fetchall()]
#    print(codes)

    return codes

##########################################################################
#   テーブル内の全レコードを1行ずつ取り出す
##########################################################################
def insert_data_from_df_to_db(conn, df):
    """ insert data from dataframe to the SQLite database"""
    df.to_sql('TradeHist', conn, if_exists='append', index=False)

##########################################################################
#   テーブル内の全レコードを1行ずつ取り出す
##########################################################################
def read_rec_fetchone(cursor):
    select_sql = """SELECT * FROM tbl_kabudata"""
    cursor.execute(select_sql)

    while True:
        result=cursor.fetchone()#データを1行抽出
        if result is None :#ループ離脱条件(データを抽出しきって空になったら)
            break #breakでループ離脱

        print(result)

##########################################################################
#   NULLのあるレコードを削除する
##########################################################################
def delete_all_records(conn, table_name):
    """ delete all records from the specified table """
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table_name}")
        conn.commit()
        print("All records deleted successfully from " + table_name)
    except sqlite3.OperationalError as e:
        print(e)
##########################################################################
#   NULLのあるレコードを削除する
##########################################################################
def del_null_rec(conn, cursor, code):

    sql = 'delete from tbl_' + code + ' WHERE open IS NULL';
    cursor.execute(sql)
    conn.commit()

##########################################################################
#   レコードを削除する
##########################################################################
def del_price_one_rec(conn, cursor, code, date):

    sql = 'delete from tbl_' + code + ' WHERE datetime LIKE "' + date +'%"';

    cursor.execute(sql)
    conn.commit()

##########################################################################
#   指定日以降のレコードを削除する
##########################################################################
def del_price_after_date(conn, cursor, code, date):

    sql = 'delete from tbl_' + code + ' WHERE datetime >= "' + date +'"';

    cursor.execute(sql)
    conn.commit()

##########################################################################
#   テーブル名称を変更する
##########################################################################
def chg_tblname(conn):
    """
    ALTER TABLE 変更前のテーブル名 RENAME TO 変更後のテーブル名
    """
    sql = """ALTER TABLE test RENAME TO test1"""

    #命令を実行
    conn.execute(sql)
    conn.commit()#コミットする

##########################################################################
#   テーブルを削除する
##########################################################################
def delete_tbl(conn, tbl):
    """
    DROP if exists TABLE 削除テーブル名
    """
    sql = 'DROP TABLE if exists ' + tbl

    #命令を実行
    conn.execute(sql)
    conn.commit()#コミットする

##########################################################################
#   データベースのコネクション(接続)を遮断する
##########################################################################
def close_db(conn):
    #作業完了したらDB接続を閉じる
    conn.close()
