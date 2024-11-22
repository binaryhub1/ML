# -*- coding: utf-8 -*-
"""CatBoost.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dv5taknlNX2dVA4rcQK5QpqgPxIrpEwA

# **CatBoost Implementation**

**INSTALLING NECESSARY LIBRARIES**
"""

!pip install catboost

"""**IMPORTING LIBRARIES AND UPLOADING DATA**"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

df = pd.read_csv('/content/T1total_Cleaned (1).csv')
df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])

df

# Make sure the 'TimeStamp' is set as the index
df.set_index('TimeStamp', inplace=True)

# Extract features and target variable
X = df.drop(columns=['power'])
y = df['power']

#df.index
df.info()

"""**NORMALIZE FEATURES**"""

# Normalize features and target variable
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_normalized = scaler_X.fit_transform(X)
y_normalized = scaler_y.fit_transform(y.values.reshape(-1, 1))

# Combine the normalized features and target variable into a DataFrame
df_normalized = pd.DataFrame(
    np.concatenate([y_normalized, X_normalized], axis=1),
    columns=['power_normalized'] + X.columns.tolist(),
    index=df.index
)

# Define the look-back and forecast horizon
look_back = 144
horizon = 6

# Split the data into training and testing sets by date
split_date = df_normalized.index[int(len(df_normalized) * 0.8)]

train = df_normalized[df_normalized.index <= split_date]
test = df_normalized[df_normalized.index > split_date]

# Extract features and target variable for training set
X_train = train.drop(columns=['power_normalized'])
y_train = train['power_normalized']

# Extract features and target variable for testing set
X_test = test.drop(columns=['power_normalized'])
y_test = test['power_normalized']

X_train.shape

y_train.shape

train.shape

"""**IMPLEMENTING CATBOOST MODEL**"""

from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Build the CatBoost model
model = CatBoostRegressor(iterations=5000, depth=6, learning_rate=0.1, loss_function='RMSE', verbose=0)

# Train the model
model.fit(X_train.values, y_train.values, eval_set=(X_test.values, y_test.values), early_stopping_rounds=50, verbose=100)

# Make predictions on the test set
predictions = model.predict(X_test.values)

# Invert the scaling to get the actual power values
predicted_power = scaler_y.inverse_transform(predictions.reshape(-1, 1))
actual_power = scaler_y.inverse_transform(y_test.values.reshape(-1, 1))

# Calculate and print RMSE, MAE, MSE, and MAPE
rmse = np.sqrt(mean_squared_error(actual_power, predicted_power))
mae = mean_absolute_error(actual_power, predicted_power)
mse = mean_squared_error(actual_power, predicted_power)
mape = np.mean(np.abs((actual_power - predicted_power) / actual_power)) * 100

# Print metrics
print(f"RMSE: {rmse}, MAE: {mae}, MSE: {mse}, MAPE: {mape}%")