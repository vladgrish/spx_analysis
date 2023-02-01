import yfinance as yf
import datetime
import numpy as np

# Define the start and end date for the data
end = datetime.datetime.now()
start = "2023-01-01"

# Download the historical data for SPY ETF
spy_data = yf.download("SPY", start=start, end=end)
spy_data.columns= spy_data.columns.str.lower()
spy_data = spy_data.drop(columns=['adj close', 'volume'])
# Create a new column 'Open_Pct_Change' that shows the percentage change between the open of the current day and the previous day's close
spy_data['open_pct_change'] = (spy_data['open'] - spy_data['close'].shift(1)) *100/ spy_data['close'].shift(1)
spy_data["gap_threshold"] = ((spy_data["open_pct_change"] > 0.5) | (spy_data["open_pct_change"] < -0.5))
spy_data["gapped_up_or_down"] = np.where((spy_data["gap_threshold"] == True) & (spy_data["open_pct_change"] > 0), "up",
                                            np.where((spy_data["gap_threshold"] == True) & (spy_data["open_pct_change"] < 0), "down", np.nan))
spy_data['gap_filled'] = None
spy_data["gap_filled"] = np.where((spy_data["gapped_up_or_down"] == "up") & (spy_data["low"] < 1.003*spy_data['close'].shift(1)), True,
                                            np.where((spy_data["gapped_up_or_down"] == "down") & (spy_data["high"] > 0.997*spy_data['close'].shift(1)), True, np.nan))
spy_data.insert(4, "prev_day_close", spy_data["close"].shift(1), True)
spy_data.to_csv('./data/spx_data_raw.vsc')
spy_data = spy_data[spy_data["gap_threshold"] == True]
true_rows = (spy_data["gap_filled"] == True).sum()

# print(true_rows/len(spy_data))
spy_data = spy_data[spy_data["gap_filled"] == True]
index_list = spy_data.index.tolist()
date_list = [x.strftime("%Y-%m-%d") for x in index_list]
prev_day_close_dict = {}
for index, row in spy_data.iterrows():
    prev_day_close_dict[index] = row["prev_day_close"]
prev_day_close_dict = {datetime_object.strftime("%Y-%m-%d"): value for datetime_object, value in prev_day_close_dict.items()}

spy_data.to_csv('./data/spx_data.csv')
