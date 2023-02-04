import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.metrics import accuracy_score

# Load the data into a pandas dataframe
df = pd.read_csv("./mydata/normalized_spy_data_daily_for_gap_continuation.csv")
df.dropna(inplace=True)
# Prepare the input and output data
X = df.drop(['Date', 'continued','High','Low'], axis=1)
y = df['continued']
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Convert data to suitable format for LSTM
X_train = np.array(X_train).reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = np.array(X_test).reshape((X_test.shape[0], X_test.shape[1], 1))

# Train the model
model = Sequential()
model.add(LSTM(50, input_shape=(X_train.shape[1], 1)))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=100, batch_size=32)

# Make predictions on the test set
y_pred = model.predict(X_test)
y_pred = [round(x[0]) for x in y_pred]

# Evaluate the model's performance
acc = accuracy_score(y_test, y_pred)
print("Accuracy: {:.2f}%".format(acc * 100))