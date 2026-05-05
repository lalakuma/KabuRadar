

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from collections import namedtuple
import datetime
import pandas

class BtmSrch:
    class Peek:
        currMinidx = 0     # カレント底インデックス
        currMinval = 0     # カレント底値
        preMinval = 0      # １つ前の底値
        
        currMaxidx = 0     # カレント天井インデックス
        currMaxval = 0     # カレント天井値
        preMaxval = 0      # １つ前の天井値

    MAX = 0
    MIN = 1

    maxid = []
    minid = []
    margeid = []
    lstmin = []
    srch1Btm = 0                            # 1番底フラグ
    srch2Btm = 0                            # 1番底フラグ
    DownbtmCnt = 0                          # ダウンボトムカウント
    conUpBtmCnt = 0                         # アップボトムカウント
    tplMaxsize = 0
    tplMinsize = 0
    MostMaxVal = 0
    #****************************
    # 初期処理
    #****************************
    def __init__(self, x, y):
        self.x = np.array(x)        
        self.y = np.array(y)        

        #ピーク値のインデックスを取得
        self.maxid = signal.argrelmax(self.y, order=1)    # プラスピーク値取得
        self.minid = signal.argrelmin(self.y, order=1)    # マイナスピーク値取得
        self.margeid = []

        self.tplMaxsize = len(self.maxid[0])                  # プラスピーク値の数
        self.tplMinsize = len(self.minid[0])                  # マイナスピーク値の数
        self.tplMargesize = self.tplMaxsize + self.tplMinsize # 合計サイズ

        self.lstmin.clear()
        maxcnt = 0
        mincnt = 0
        # maxidとminidをマージする。種別を追加して2次元とし、maxは1、minは0を付加する。
        # [0]=index, [1]=0:min/1:max, [2]値
        for allcnt in range(self.tplMargesize):
            if maxcnt == self.tplMaxsize:
                strdt = self.x[self.minid[0][mincnt]]
                self.margeid.append([self.minid[0][mincnt], 0, self.y[self.minid[0][mincnt]], strdt])
                if mincnt < self.tplMinsize:
                    mincnt += 1
            elif mincnt == self.tplMinsize:
                strdt = self.x[self.maxid[0][maxcnt]]
                self.margeid.append([self.maxid[0][maxcnt], 1, self.y[self.maxid[0][maxcnt]], strdt])
                if maxcnt < self.tplMaxsize:
                    maxcnt += 1
            else:
                if(self.maxid[0][maxcnt] < self.minid[0][mincnt]):
                    strdt = self.x[self.maxid[0][maxcnt]]
                    self.margeid.append([self.maxid[0][maxcnt], 1, self.y[self.maxid[0][maxcnt]], strdt])
                    if maxcnt < self.tplMaxsize:
                        maxcnt += 1
                else:
                    strdt = self.x[self.minid[0][mincnt]]
                    self.margeid.append([self.minid[0][mincnt], 0, self.y[self.minid[0][mincnt]], strdt])
                    if mincnt < self.tplMinsize:
                        mincnt += 1
#        print(self.margeid)


    def clear(self):
        self.maxid = []
        self.minid = []
        self.lstmin = []
        self.srch1Btm = 0                            # 1番底値
        self.srch2Btm = 0                            # 2番底値
        self.DownbtmCnt = 0                          # ダウンボトムカウント
        self.conUpBtmCnt = 0                         # アップボトムカウント
        self.tplsize = 0

    def getCount(self):
        size = self.tplMinsize
        if self.tplMaxsize > self.tplMinsize:
            size = self.tplMaxsize
        return size 

    #################################################################
    # 2ndと3rdボトムによる売買シグナルが発生しているかを判定する
    # 引数：mode        (MODE_BUY=買い、MODE_SELL=売り)
    #     : dfrsi       データフレーム
    #     : period      期間
    # 戻り値：True=シグナル検出
    #       ：False=シグナルではない
    #################################################################
    def make2nd3rdBottom(self):
        currMinval = 0
        currMaxval = 0
        currMinidx = 0
        currMaxidx = 0
        preMinval = 0
        preMaxval = 0

        for cnt in range(self.tplMargesize - 1):# マイナスピーク値の数分繰り返す
            
            if self.margeid[cnt][1] == 0:
                preMinval = currMinval
                currMinidx = self.margeid[cnt][0] 
                currMinval = self.margeid[cnt][2]
            else:
                preMaxval = currMaxval
                currMaxidx = self.margeid[cnt][0] 
                currMaxval = self.margeid[cnt][2]
                # 最大値チェック
                if self.MostMaxVal < currMaxval:             # 最高値と現在値を比較
                    self.MostMaxVal = currMaxval             # 最高値の入れ替え
                    self.srch1Btm = 0
                    self.srch2Btm = 0
                    self.DownbtmCnt = 0
                continue
            
            # 頂点、底が設定されないうちはcontinue
            if currMinval == 0 or currMaxval == 0:
                continue

            # 浅すぎるくぼみは無視
            if (currMaxval - currMinval) < (currMaxval * 0.02):
#                print(self.x[currMinidx])

                continue
            
            # 1番底検出前の時
            if self.srch1Btm == 0:
                # 最高値から10%以上下がった時
                if currMinval < (self.MostMaxVal - (self.MostMaxVal * 0.1)): 
                    self.srch1Btm = currMinval
            
            # 現在値が最高値の10%引きより高い場合は初期化    
            if self.srch1Btm > 0:
                if currMinval > (self.MostMaxVal - (self.MostMaxVal * 0.1)):      
                    self.srch1Btm = 0
                    self.srch2Btm = 0
                    self.DownbtmCnt = 0
                    self.MostMaxVal = 0
#                    print(self.x[currMinidx])
                    continue

            # 1番底検出済みの時        
            if self.srch1Btm > 0 and self.srch2Btm == 0:
                # 現在ポイントが前回ポイントよりも高い時
                if currMinval > self.srch1Btm:
                    # 2番底のポイントを格納
                    self.lstmin.append(currMinidx)
#                    print(self.x[currMinidx])
                    self.srch2Btm = currMinval
                    continue
                else:
                    #1番底更新
                    self.srch1Btm = currMinval

                        
            # 2番底検出済みの時        
            if self.srch2Btm > 0:
                # 現在ポイントが前回ポイントよりも高い時
                if currMinval > preMinval:
                    # 3番底のポイントを格納
                    self.lstmin.append(currMinidx)
#                    print(self.x[currMinidx])
                    self.DownbtmCnt = 0
                self.srch1Btm = 0
                self.srch2Btm = 0

        #タプルに変換して戻す
        self.minid = np.array(self.lstmin)

        # if len(self.lstmin) > 0:
        #     plt.plot(self.x,self.y,'k-',label='元系列')
        #     plt.plot(self.x[self.minid], self.y[self.minid],'bo',label='ピーク値（最小）')
        #     plt.legend()
        #     plt.show()
        #     print(self.lstmin)
    #################################################################
    # 引数の指定日が2ndまたは3rdボトムからの上昇中(下記図の2重線)であるかを判定する
    # 引数：predate   (チェック対象指定日)
    #
    #   │
    #   │
    #   │                   ∥￣│
    #   │           ∥￣│＿∥
    #   │  │￣│＿∥     ↑3番底
    #   │＿│    ↑2番底
    #     ↑2番底
    #
    # 戻り値：True=シグナル検出
    #       ：False=シグナルではない
    #################################################################
    def jdg_2nd3rdBottom(self, date):
        search = False
        dt = date
        
        btm2ndDtSta = datetime.datetime.max
        btm2ndDtEnd = datetime.datetime.max
        btm3rdDtSta = datetime.datetime.max
        btm3rdDtEnd = datetime.datetime.max

        for mincnt in range(len(self.minid)):                        
            for mrgcnt in range(len(self.margeid)):
                if self.margeid[mrgcnt][0] == self.minid[mincnt]:
                    if mincnt == 0:
                        btm2ndDtSta = self.margeid[mrgcnt][3]
                    else:
                        btm3rdDtSta = self.margeid[mrgcnt][3]

                    if mrgcnt < len(self.margeid) - 1:
                        if mincnt == 0:
                            btm2ndDtEnd = self.margeid[mrgcnt + 1][3]
                        else:
                            btm3rdDtEnd = self.margeid[mrgcnt + 1][3]
        
        if  btm2ndDtSta <= dt < btm2ndDtEnd:
            print(btm2ndDtSta, dt, btm2ndDtEnd)
            search = True
            
        if  btm3rdDtSta <= dt < btm3rdDtEnd:
            print(btm3rdDtSta, dt, btm3rdDtEnd)
            search = True



        # for cnt in range(len(self.minid)):
        #     mindt = self.x[self.minid[cnt]]
        #     dt = np.datetime64(date)
        #     if dt == mindt:
        #         search = True
        #         print(dt)
        #         break
        
        return search