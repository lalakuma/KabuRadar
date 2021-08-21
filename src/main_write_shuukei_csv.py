# 解析後に出力したCSVファイルを集計する
from numpy import empty
import pandas as pd
import os

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

        print(df)
        strWinPer = "rate" + '{:.1f}'.format(df['winPer'].mean())
        print(strWinPer)
        strincome = "rieki" + '{:}'.format(int(df['incomes'].sum()))
        print(strincome)
        strpfall = "PF" + str(round(total_pgain / total_mgain, 2))

        #wlstr = "_prm" + strprm + "_rsi"+ str(dt.adopt_rsi) + "_W" + str(dt.win) + "L" + str(dt.lose) + "_" + str(dt.winrate) + "%_" + str(dt.income)
        strpath = "../analys/" + strpfall + "_" + "W" + str(cnt_win) + "L" + str(cnt_lose) + "_" + strWinPer + "_" + strincome + ".csv"
        df.to_csv(strpath, encoding="shift_jis")    
    
#shuukei_toCsv()