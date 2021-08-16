import mpl_finance
import matplotlib.pyplot as plt
from pandas_datareader import data
import pandas as pd 
import numpy as np
 
# 株価データを取得
df = data.DataReader('7203.JP', 'stooq')
print(df)
# 日付の古い順に並び替え
df.sort_index(inplace=True)

df["SMA5"] = df["close"].rolling(window=5).mean()
df["SMA25"] = df["close"].rolling(window=25).mean()

# チャート定義
fig, ax = plt.subplots(figsize=(20, 10))
 
# ローソク足チャートをプロット
mpl_finance.candlestick_ohlc(ax, df.values, width=0.5, colorup='r', colordown='b')

df.insert(0,"index",[x for x in range(len(df))])

# 移動平均線をプロット
ax.plot(df["index"], df["SMA5"], label="SMA5")
ax.plot(df["index"], df["SMA25"], label="SMA25")
 
# X軸を調整
plt.xticks([x for x in range(len(df))], [x.strftime('%Y-%m-%d') for x in df.index])
fig.autofmt_xdate()
 
# 凡例表示
plt.legend()
 
# グリッド表示
plt.grid()
 
# グラフを表示
plt.show()