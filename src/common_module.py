import pandas as pd
import sqlight as db
############################################
# CODEの有効無効設定
############################################
def set_code_enable():
    targetfile = "PF1.33_W8465L6908_rate54.5_rieki6457900.csv"
    #path = "C:\MorinoFolder\Python\KabuRadar\同日の両建てはなしバージョン\\1.analys_PF2.73_W1767L1066_rate61.9_rieki4662900_bb2 of1.5\\"
    path = "C:\MorinoFolder\Python\KabuRadar\\analys_PF1.33_W8465L6908_rate54.5_rieki6457900_買のみブレイクのみ_安定\\"
    dirname = path + targetfile
    df_csv = pd.read_csv(dirname, encoding="ms932", sep=",")    

    df_ena = pd.DataFrame(columns=['code', 'Enable'])
    lstDisCode = []
    for row in df_csv.itertuples():
        if row.pf < 1.2:
            df_ena = df_ena.append({'code': row.code, 'Enable': '0'}, ignore_index=True)
#            lstDisCode.append(row.code)
        else:
            df_ena = df_ena.append({'code': row.code, 'Enable': '1'}, ignore_index=True)
   
    #----------------------------------------------
    # DBの該当コードのEnable設定を無効(0)に設定する
    #----------------------------------------------
    conn, cursor = db.connect_db()      # DBに接続
    for enarow in df_ena.itertuples():
        # DB更新
        db.update_codelist_enable(conn, cursor, "tbl_code_set", enarow)

    # DBクローズ
    db.close_db(conn)

set_code_enable()