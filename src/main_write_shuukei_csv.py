# 解析後に出力したCSVファイルを集計する
from numpy import empty
import pandas as pd
import os
import glob
import openpyxl as px
import copy

def shuukei_makeExl():
    fileShukei = "集計.xlsx"
#    path = "C:\\MorinoFolder\\Python\\KabuRadar\\analys\\"
    path = "E:\\KabuRadar\\analys\\"

    # フォルダ内の全ファイルを取得
    allFiles = glob.glob(path + "\*.csv") # 指定したフォルダーの全エクセルファイルを変数に代入します
    df = pd.DataFrame()
    list_ = []
    # フォルダ内のファイルを全て処理する
    for file_ in allFiles:
        df = pd.read_csv(file_, encoding="ms932", sep=",")    
        # 文字列「code」を検索
        poscode = file_.find("code")
        # 「code」がないファイルはパス
        if poscode == -1:
            continue
        code = file_[poscode+4:poscode+8]
        df["code"] = code
        list_.append(df)
    # 結合
    df_con = pd.concat(list_, join='inner') # joinをinnerに指定
    # NaNのある行を削除
    df_con = df_con.dropna(axis = 0, how = 'any')
    df_con = df_con.sort_values(['Index', 'code'])

    # 並べ替え
    df_con = df_con.reset_index()
#    df_con = df_con.set_index("Index").loc[:,["code","close","mark","buy","sell","buygain","sellgain","income"]]
    df_con = df_con.loc[:,["Index","code","close","mark","buy","sell","buygain","sellgain","income"]]
    #選別　（お試し用）
    df_renew = pd.DataFrame()
    daytotal = 0
    wktotal = 0
    predate = ""
    lst_data = []


    date = df_con.iat[0,0]
    cnt = 0
    samelen = 0
    lst_tdyBuy = []     # 当日購入リスト
    lst_PreBuy = []     # 前営業日購入リスト
    for row in range(len(df_con)):
        # 同一日付で処理済の行は読み飛ばす
        if samelen > 0:
            samelen -= 1
            continue
        # 日付が一致するものを抽出
        df_samedate = (df_con[df_con["Index"].str.contains(date[:10])])
        df_samedate = df_samedate.sort_values("close", ascending=False)    # 高額順

        # 同一日付内でループ
        for samerow in df_samedate.itertuples():
            if samerow.mark == "新買" or samerow.mark == "新売":
                # 現在値を加算していく
                wktotal += samerow.close                # 一時トータルに終値加算

                # トータル10000(買値が100万円)以内なら購入対象として追加
                if wktotal < 10000:                     # 一時トータルで比較
                    lst_tdyBuy.append(samerow.code)     # 当日購入リストにコードを追加
                    lst_data.append(samerow)            # データリストに追加
                    daytotal += samerow.close           # 正式トータルに追加
                
                wktotal = daytotal  # 一時トータル更新
        else:
                # 前日リストの中にcodeがあるか検索（前日購入済みの株かどうか）
                findcode = samerow.code in lst_PreBuy
                # 見つけたら集計リストに追加
                if findcode == True:
                    # 前日リストの中にcodeがあるか検索（前日購入済みの株かどうか）
                    tdyfindcode = samerow.code in lst_tdyBuy
                    # 既に購入リスト側に追加されている場合は重複になってしまうので追加しない
                    if tdyfindcode == False:
                        lst_data.append(samerow)

        #----------------------------------
        # 次の日付グループに向けての準備
        #----------------------------------
        # 当日購入リストを前日購入リストにコピー
        lst_PreBuy = copy.copy(lst_tdyBuy)        
        lst_tdyBuy.clear()
        daytotal = 0
        wktotal = 0
        samelen = len(df_samedate) - 1
        nextpos = row + samelen + 1
        # 終了判定
        if nextpos < len(df_con):
            # 次の日付をセット
            date = df_con.iat[nextpos, 0]
        else:
            break

    # エクセルに書き込み
    df_con.to_excel(path + fileShukei, sheet_name='全コード結合', encoding="shift_jis")

    dfreal = pd.DataFrame(lst_data)    
    with pd.ExcelWriter(path + fileShukei, engine="openpyxl", mode="a") as writer:
        dfreal.to_excel(writer, sheet_name='1日10000以下', index=False)

    # エクセルファイルの先頭行にフィルターをつける
    wb= px.load_workbook(path + fileShukei)
    ws = wb.active
    ws.column_dimensions['B'].width =22
    ws.auto_filter.ref = ws.dimensions
    ws1 = wb.worksheets[1]
    ws1.column_dimensions['B'].width =22
    ws1.auto_filter.ref = ws.dimensions
    wb.save(path + fileShukei)


def shuukei_toCsv():
    filelst = os.listdir(path='../analys')

    df = pd.DataFrame()

    wk_pf = 0.0
    #fl_pf = 0.0
    wk_pgain = 0
    total_pgain = 0
    total_mgain = 0
    wk_mgain = 0
    filecnt = 0
    cnt_win = 0
    cnt_lose = 0
    for fl in filelst:
        if fl[:4] == "code":
            arr = fl.split('_')
            wk_pf = float((arr[5])[2:]) 

            # 利益と損失を取得
            wk_pgain = int((arr[6])[2:])
            total_pgain += wk_pgain
            wk_mgain = abs(int(((arr[7])[:-4])[2:]))
            total_mgain += wk_mgain

            # win lose の累積件数を取得
            strwl = arr[2]
            lpos = strwl.find('L')
            cnt_win += int(strwl[1:lpos])
            cnt_lose += int(strwl[lpos + 1:])

            df = df.append({'code':arr[1], 
                'code':(arr[0])[4:], 
                'rsi':(arr[1])[3:], 
                'winlose':strwl, 
                'winPer':int((arr[3])[:-1]), 
                'incomes':int((arr[4])[3:]), 
                'pg':wk_pgain, 
                'mg':wk_mgain, 
                'pf':wk_pf}, 
                ignore_index=True)

    if len(df) > 0 :
        #日付をインデックスにして、必要なアイテム順に並び替え
        df = df.set_index("code").loc[:,["pf","pg","mg","incomes","winlose","winPer","rsi"]]
        strWinPer = "rate" + '{:.1f}'.format(df['winPer'].mean())
        print(strWinPer)
        strincome = "rieki" + '{:}'.format(int(df['incomes'].sum()))
        print(strincome)
        strpfall = "PF" + str(round(total_pgain / total_mgain, 2))

        #wlstr = "_prm" + strprm + "_rsi"+ str(dt.adopt_rsi) + "_W" + str(dt.win) + "L" + str(dt.lose) + "_" + str(dt.winrate) + "%_" + str(dt.income)
        strpath = "../analys/" + strpfall + "_" + "W" + str(cnt_win) + "L" + str(cnt_lose) + "_" + strWinPer + "_" + strincome + ".csv"
        df.to_csv(strpath, encoding="shift_jis")    
    
#shuukei_toCsv()
#shuukei_makeExl()