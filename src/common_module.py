import pandas as pd
import sqlight as db
import getConfig

############################################
# CODEの有効無効設定
# PF情報登録
############################################
def set_code_setting():
    path = getConfig.get_codeset_path()
    df_csv = pd.read_csv(path, encoding="ms932", sep=",")

    df_ena = pd.DataFrame(columns=['code', 'pf', 'Enable'])
    lstDisCode = []
    for row in df_csv.itertuples():
        if row.pf < 1.2:
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
