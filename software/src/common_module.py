import pandas as pd
import sqlight as db
import getConfig
import glob

############################################
# CODEの有効無効設定
# PF情報登録
############################################
def set_code_setting():
    path = getConfig.get_codeset_path()
    allFiles = glob.glob(path + "*.csv") # 指定したフォルダーの全エクセルファイルを変数に代入します
    filePath = allFiles[0]

    df_csv = pd.read_csv(filePath, encoding="ms932", sep=",")

    df_ena = pd.DataFrame(columns=['code', 'pf', 'Enable'])
    lstDisCode = []
    for row in df_csv.itertuples():
        if row.pf < 0.8:
            df_ena = df_ena.append({'code': row.code, 'pf': row.pf, 'Enable': '0'}, ignore_index=True)
#            lstDisCode.append(row.code)
        else:
            df_ena = df_ena.append({'code': row.code, 'pf': row.pf, 'Enable': '1'}, ignore_index=True)
   
    #----------------------------------------------
    # DBの該当コードのPFとEnable設定を登録する
    #----------------------------------------------
    conn, cursor = db.connect_db()      # DBに接続
    for enarow in df_ena.itertuples():
        # DB更新
        db.update_codeset(conn, cursor, "tbl_code_set", enarow)

    # DBクローズ
    db.close_db(conn)

#######################    
#  実行
#######################    
set_code_setting()
