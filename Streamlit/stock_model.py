# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 19:57:42 2024

@author: Mohamed Tharif
"""

import numpy as np
import pandas as pd
import yfinance as yf
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler




def model_train(stock_data,test_data):
    
    
    
    model = load_model('stock_prediction_model.h5')

    # Prepare training data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(stock_data['Close'].values.reshape(-1, 1))
   

    prediction_days=120
   
    actual_prices = test_data['Close'].values
    
    total_dataset = pd.concat((stock_data['Close'], test_data['Close']), axis=0)
    model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
    model_inputs = model_inputs.reshape(-1, 1)
    model_inputs = scaler.transform(model_inputs)
    
    x_test = []
    for x in range(prediction_days, len(model_inputs)):
        x_test.append(model_inputs[x - prediction_days:x, 0])
    
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    
    # Make predictions
    predicted_prices = model.predict(x_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)
    
    # Get the last prediction
    real_data = model_inputs[-prediction_days:].reshape(1, prediction_days, 1)
    prediction = model.predict(real_data)
    prediction = scaler.inverse_transform(prediction)
    
    return actual_prices[-1],prediction[0][0]
    

