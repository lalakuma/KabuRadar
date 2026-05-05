import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import sqlight as db
import mplcursors # インタラクティブツールチップ用

# --- 1. 定数定義 ---
# find_peaks パラメータ設定
PEAK_DISTANCE = 10 # 例としてソースコード[4]の値を設定
PEAK_PROMINENCE_FACTOR = 0.25 # 例としてソースコード[4]の値をもとに設定

# --- 2. DBからデータ取得 ---
conn, cursor = db.connect_db()
table_name = "tbl_4980"
query = f"SELECT datetime, open, high, low, close, volume FROM {table_name} WHERE datetime >= '2022-01-01' ORDER BY datetime ASC"
df = pd.read_sql_query(query, conn, parse_dates=["datetime"])
conn.close()
df.set_index("datetime", inplace=True)

# --- 3. RSI (4日) をワイルダー式で計算 ---
def calculate_rsi_wilder(prices, window=4):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rsi = pd.Series(np.nan, index=prices.index)
    for i in range(window, len(prices)):
        if i == window:
            current_avg_gain = avg_gain.iloc[i]
            current_avg_loss = avg_loss.iloc[i]
        else:
            current_gain = gain.iloc[i]
            current_loss = loss.iloc[i]
            current_avg_gain = ((window - 1) * current_avg_gain + current_gain) / window
            current_avg_loss = ((window - 1) * current_avg_loss + current_loss) / window
        if current_avg_loss == 0:
            rsi.iloc[i] = 100
        else:
            rs = current_avg_gain / current_avg_loss
            rsi.iloc[i] = 100 - (100 / (1 + rs))
    return rsi

df['rsi4'] = calculate_rsi_wilder(df['close'], window=4)

# --- 4. 移動平均線の計算 ---
df['MA200'] = df['close'].rolling(window=200, min_periods=200).mean()
df['MA25'] = df['close'].rolling(window=25, min_periods=25).mean()

# --- 5. 出来高移動平均の計算（直近5日間） ---
df['vol_ma5'] = df['volume'].rolling(window=5, min_periods=5).mean()

# --- 6. 局所最小値（All Local Minima）の検出 ---
price = df["close"]
prominence_val = np.std(price) * PEAK_PROMINENCE_FACTOR # 定数を使用
distance_val = PEAK_DISTANCE # 定数を使用
min_indices, _ = find_peaks(-price.values, prominence=prominence_val, distance=distance_val)

# --- 7. 「深いカップ」の条件を適用 ---
deep_cup_minima = []
#drop_threshold = 0.05
#lookback_window = 20
drop_threshold = 0.05
lookback_window = 20
for idx in min_indices:
    candidate_price = price.values[idx]
    if idx - lookback_window >= 0:
        past_high = price.values[idx - lookback_window: idx].max()
        if (candidate_price / past_high) <= (1 - drop_threshold):
            deep_cup_minima.append(idx)

# --- 8. 買いシグナルの判定（RSI, 出来高, 過去のRim Date） ---
tolerance = 0.02
buy_signals = []
for idx in range(len(price)):
    current_date = price.index[idx]
    current_price = price.iloc[idx]
    current_rsi = df['rsi4'].iloc[idx]
    if current_rsi > 20:
        continue
    if idx >= 5 and df['volume'].iloc[idx] < 1.2 * df['vol_ma5'].iloc[idx]:
        continue
    # 過去の `Rim Date` のみ取得
    valid_rim_dates = [price.index[candidate_idx] for candidate_idx in deep_cup_minima if price.index[candidate_idx] < current_date]
    if not valid_rim_dates:
        continue
    rim_date = max(valid_rim_dates)
    rim_idx = price.index.get_loc(rim_date)
    rim_price = price.iloc[rim_idx]
    if (rim_price * (1 - tolerance)) <= current_price <= (rim_price * (1 + tolerance)):
        buy_signals.append((current_date, current_price, rim_date, rim_price))

# --- 9. プロット ---
fig, ax1 = plt.subplots(figsize=(14, 7))
ax1.plot(price.index, price.values, label="Close Price", color="black")
ax1.plot(df.index, df['MA200'], label="200-day MA", color="blue", linewidth=1.5)
ax1.plot(df.index, df['MA25'], label="25-day MA", color="green", linewidth=1.5)
ax2 = ax1.twinx()
ax2.bar(df.index, df['volume'], label="Volume", color="gray", alpha=0.3)
ax2.plot(df.index, df['vol_ma5'], label="5-day Vol MA", color="orange", linewidth=1.5)
scatter_minima = ax1.scatter(price.index[min_indices], price.values[min_indices], color='red', label='All Minima', marker='o', s=40)
scatter_deep_cup = ax1.scatter(price.index[deep_cup_minima], price.values[deep_cup_minima], color='green', label='Deep Cup Minima', marker='o', s=50)
scatter_buy = ax1.scatter([date for date, _, _, _ in buy_signals], [price for _, price, _, _ in buy_signals], color='purple', label='Buy Signals', marker='^', s=60)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
# --- 10. インタラクティブツールチップの設定 ---
cursor = mplcursors.cursor(scatter_buy, hover=True)
@cursor.connect("add")
def on_add(sel):
    idx = sel.index
    current_date, current_price, rim_date, rim_price = buy_signals[idx]
    sel.annotation.set(text=f"Rim Date: {rim_date.strftime('%Y-%m-%d')}\nRim Price: {rim_price:.2f}",
                       position=(0, 20),
                       anncoords="offset points")
plt.show()

# --- 11. シグナル一覧の表示 ---
signal_df = pd.DataFrame(buy_signals, columns=["Current Date", "Current Price", "Rim Date", "Rim Price"])
print("逆さカップの縁で、RSI(4日, Wilder式)が10以下、かつ出来高フィルタ・移動平均線と併用した買いシグナル:")
print(signal_df)