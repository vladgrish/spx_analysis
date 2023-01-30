import yfinance as yf
import datetime
import numpy as np
import pandas as pd

data_df_min = pd.read_csv("./mydata/SPY_5min.csv")
data_df_min["Date"] = pd.to_datetime(data_df_min["Date"])
start_time = pd.to_datetime("09:30:00").time()
end_time = pd.to_datetime("15:55:00").time()
data_df_min = data_df_min[(data_df_min["Date"].dt.time >= start_time) & (data_df_min["Date"].dt.time <= end_time)]


list = []
data_df_min["Date"] = pd.to_datetime(data_df_min["Date"])
condition = data_df_min["Date"].dt.time == datetime.time(9, 30)
Open = data_df_min[condition]["Open"].tolist()
open_df = data_df_min[condition][["Date","Open"]].reset_index(drop=True)
condition = data_df_min["Date"].dt.time == datetime.time(15, 30)
Close = data_df_min[condition]["Close"].tolist()
close_df = data_df_min[condition][["Date","Close"]].reset_index(drop=True)
close_df['Date'] = close_df['Date'].dt.date
open_df['Date'] = open_df['Date'].dt.date
# open_df.to_csv("./mydata/open_df.csv",index=False)
# close_df.to_csv("./mydata/close_df.csv",index=False)


not_in_df1 = open_df[~open_df['Date'].isin(close_df['Date'])]
my_list = not_in_df1["Date"].values.tolist()
date_list = [d.strftime('%Y-%m-%d') for d in my_list]
for index, row in data_df_min.iterrows():
    list.append(row['Date'].strftime("%Y-%m-%d"))
data_df_min["Date"] = list
low = data_df_min.groupby("Date")["Low"].min()
high = data_df_min.groupby("Date")["High"].max()
data_df_min["Date"] = pd.to_datetime(data_df_min["Date"])
date_volume_sum = data_df_min.groupby("Date")["Volume"].sum()
volume = date_volume_sum.tolist()
result = pd.concat([high, low], axis=1)
result.reset_index(inplace=True)
result.columns = ["Date", "High", "Low"]
result.insert(1, "Open", Open)
result["Volume"] = volume
for i,row in result.iterrows():
    for i in date_list:
        if row["Date"] == date_list[0]:
            result = result[result['Date'] != i]
result.insert(4, "Close", Close)
result.to_csv("./mydata/filtered_downloaded_spy_data_daily.csv", index=False)

spy_data = result.copy()
# spy_data = spy_data.drop(columns=['Adj Close', 'Volume'])
# Create a new column 'Open_Pct_Change' that shows the percentage change between the open of the current day and the previous day's close
spy_data['Open_Pct_Change'] = (spy_data['Open'] - spy_data['Close'].shift(1)) * 100 / spy_data['Close'].shift(1)
spy_data["gap_threshold"] = ((spy_data["Open_Pct_Change"] >= 1) | (spy_data["Open_Pct_Change"] <= -1))
spy_data["gapped-up-or-down"] = np.where((spy_data["gap_threshold"] == True) & (spy_data["Open_Pct_Change"] > 0), "up",
                                            np.where((spy_data["gap_threshold"] == True) & (spy_data["Open_Pct_Change"] < 0), "down", np.nan))
spy_data['gap-filled'] = None
spy_data["gap-filled"] = np.where((spy_data["gapped-up-or-down"] == "up") & (spy_data["Low"] < 1.005*spy_data['Close'].shift(1)), "filled",
                                            np.where((spy_data["gapped-up-or-down"] == "down") & (spy_data["High"] > 0.995*spy_data['Close'].shift(1)), "filled", np.nan))

spy_data.insert(5, "prev_day_close", spy_data["Close"].shift(1), True)
spy_data.to_csv('./mydata/yahoo_spy_data_daily.vsc')
filtered_df = spy_data[spy_data['gap_threshold'] == True].copy()
true_rows = (filtered_df["gap-filled"] == "filled").sum()
print(true_rows)
print(len(filtered_df))
print(true_rows/len(filtered_df))

index_list = filtered_df.index.tolist()
# date_list = [x.strftime("%Y-%m-%d") for x in index_list]
prev_day_close_dict = {}
for index, row in filtered_df.iterrows():
    prev_day_close_dict[index] = row["prev_day_close"]
# prev_day_close_dict = {datetime_object.strftime("%Y-%m-%d"): value for datetime_object, value in prev_day_close_dict.items()}
filtered_df["percent_move_from_open_towards_gap"] = np.nan
#
# Use the mask to set the "percent_fill_gap" to the calculated value for rows where the "gapped-up-or-down" column is "up"
filtered_df.loc[filtered_df["gapped-up-or-down"] == "up", "percent_move_from_open_towards_gap"] = (filtered_df.loc[filtered_df["gapped-up-or-down"] == "up", "Open"] - filtered_df.loc[filtered_df["gapped-up-or-down"] == "up", "Low"])*100 / filtered_df.loc[filtered_df["gapped-up-or-down"] == "up", "Open"]
filtered_df.loc[filtered_df["gapped-up-or-down"] == "down", "percent_move_from_open_towards_gap"] = (filtered_df.loc[filtered_df["gapped-up-or-down"] == "down", "High"] - filtered_df.loc[filtered_df["gapped-up-or-down"] == "down", "Open"])*100 / filtered_df.loc[filtered_df["gapped-up-or-down"] == "down", "Open"]

filtered_df.to_csv('./mydata/filtered_downloaded_spy_data_daily.csv', index=False)
