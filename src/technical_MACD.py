def macd(df, prmtype=1):
    if prmtype == 1:
        FastEMA_period = 8  # 短期EMAの期間
        SlowEMA_period = 18  # 長期EMAの期間
        SignalSMA_period = 6  # SMAを取る期間
    else:
        FastEMA_period = 12  # 短期EMAの期間
        SlowEMA_period = 26  # 長期EMAの期間
        SignalSMA_period = 9  # SMAを取る期間
        
    df["MACD"] = df["close"].ewm(span=FastEMA_period).mean() - df["close"].ewm(span=SlowEMA_period).mean()
    df["Signal"] = df["MACD"].rolling(SignalSMA_period).mean()
    return df