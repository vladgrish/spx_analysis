import yfinance as yf
import datetime
import pandas as pd
stock = "SPY"
interval = "5m"
start = "2023-01-01"
end = "2023-01-31"

spy_data = yf.download(stock, start=start, end=end, interval=interval)
spy_data = spy_data.drop(columns=['Adj Close', 'Volume'])
df = pd.read_csv("data/spx_data.vsc")
counter = 0
date_origin = "09:30:00"
for index, row in spy_data.iterrows():
    date = pd.to_datetime(df.iloc[counter]["Date"]).strftime("%Y-%m-%d")
    prev_close = df.iloc[counter]["prev_day_close"]
    gap_up_or_down = df.iloc[counter]["gapped-up-or-down"]
    if gap_up_or_down == "up" and row["Low"] <= 1.003 * prev_close and str(index).startswith(date):
        time_open = pd.to_datetime(date + " " + date_origin + "-05:00")
        time_fill = pd.to_datetime(index)
        time_diff = time_fill - time_open
        counter += 1
    elif gap_up_or_down == "down" and row["High"] >= .997 * prev_close and str(index).startswith(date):
        time_open = pd.to_datetime(date + " " + date_origin + "-05:00")
        time_fill = pd.to_datetime(index)
        time_diff = time_fill - time_open
        print(time_diff.lstrip("0 days "))
        counter += 1
    if counter == len(df):
        break




# spy_data.to_csv("./spy_intraday.csv")