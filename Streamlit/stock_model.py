# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 19:57:42 2024

@author: Mohamed Tharif
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, BatchNormalization, Dropout
from datetime import datetime, timedelta
import keras_tuner as kt
import warnings

warnings.filterwarnings("ignore")

# Define parameters
prediction_days = 120

start_date = datetime.now() - timedelta(days=365)
end_date = datetime.today()

#function to make sequence of calling
def stock_prediction(stock_data):
    model=predict(stock_data)
    prediction = predict_model(stock_data,model)
    return prediction
#model_bulding for prediction
def predict(stock_data):
        
    # Prepare training data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(stock_data['Close'].values.reshape(-1, 1))
    
    x_train = []
    y_train = []
    
    for x in range(prediction_days, len(scaled_data)):
        x_train.append(scaled_data[x - prediction_days:x, 0])
        y_train.append(scaled_data[x, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    
    
    # Set up Keras Tuner
    tuner = kt.Hyperband(build_model,
                         objective='val_loss',
                         max_epochs=25,
                         hyperband_iterations=2,
                         directory='my_dir',
                         project_name='stock_price_tuning')
    
    
    # Split the data for validation
    split = int(0.8 * len(x_train))
    x_train_split, x_val_split = x_train[:split], x_train[split:]
    y_train_split, y_val_split = y_train[:split], y_train[split:]
    
    
    # Search for the best hyperparameters
    tuner.search(x_train_split, y_train_split,
                 epochs=25,
                 batch_size=32,
                 validation_data=(x_val_split, y_val_split))
    
    # Retrieve the best hyperparameters
    best_hyperparameters = tuner.get_best_hyperparameters()[0]
    
    # Build and compile the best model
    best_model = build_model(best_hyperparameters,x_train)
    
    # Train the best model on the full training data
    best_model.fit(x_train, y_train, epochs=25, batch_size=32)
    
    return best_model


# Define the model building function
def build_model(hp,x_train):
    
    model = Sequential()
    #using Long Short
    model.add(LSTM(units=hp.Int('units_1', min_value=50, max_value=100, step=10),
                   return_sequences=True,
                   input_shape=(x_train.shape[1], 1)))
    model.add(BatchNormalization())
    model.add(Dropout(hp.Float('dropout_1', min_value=0.1, max_value=0.5, step=0.1)))
    
    model.add(LSTM(units=hp.Int('units_2', min_value=50, max_value=100, step=10),
                   return_sequences=True))
    model.add(BatchNormalization())
    model.add(Dropout(hp.Float('dropout_2', min_value=0.1, max_value=0.5, step=0.1)))
    
    model.add(LSTM(units=hp.Int('units_3', min_value=50, max_value=100, step=10)))
    model.add(Dropout(hp.Float('dropout_3', min_value=0.1, max_value=0.5, step=0.1)))
    
    model.add(Dense(units=25, activation='relu'))
    model.add(Dense(units=1))
    
    model.compile(optimizer=hp.Choice('optimizer', values=['adam', 'rmsprop']),
                  loss='mean_squared_error')
     
    # Move Model to GPU
    #device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #model.to(device)
    
    return model
#
def predict_model(stock_data, model):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(stock_data['Close'].values.reshape(-1, 1))
    
    # Normalize training data
    scaled_train_data = scaler.fit_transform(stock_data['Close'].values.reshape(-1, 1))

    # Prepare model inputs as before
    model_inputs = scaled_train_data[len(scaled_train_data) - prediction_days:].reshape(-1, 1)

    # Prepare x_test for prediction (same as before)
    x_test = [model_inputs[-prediction_days:]]
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    # Make predictions
    predicted_prices = model.predict(x_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)

    return predicted_prices[0][0]


 