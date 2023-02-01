import numpy as np
import pandas as pd

from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.model_selection import train_test_split

import plotly.express as px


def transform_timeseries(df, feature_cols, label_col, x):
    """
    transform a df into x sets of features (x units of a timeseries) where y is the label set
    """
    n = df.shape[0]
    X, y = [], []
    for i in range(n-x):
        X.append(df[feature_cols].iloc[i:i+x].values)
        y.append(df[label_col].iloc[i+x])
    X, y = np.array(X), np.array(y)
    return X, y


def build_lstm(X, y):
    """
    build an LSTM network dynamicaly based on shape of X and y
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = Sequential()
    model.add(LSTM(32, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))
    
    return model, history

def plot_history(history):
    """
    helps evaluating model
    """
    fig = px.line(x=list(range(1, len(history.history['loss'])+1)), 
                  y=[history.history[metric] for metric in ['loss', 'val_loss', 'accuracy', 'val_accuracy']],
                  labels={'x': 'Epoch', 'y': 'Value'},
                  color=['loss', 'val_loss', 'accuracy', 'val_accuracy'],
                  title='Training and Validation Metrics')
    fig.update_layout(xaxis_title='Epoch', yaxis_title='Value')
    fig.show()
