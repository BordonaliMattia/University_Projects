# -*- coding: UTF-8 -*-

import random
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from utils import process_dad_data, build_random_LS_VS, scale_data, point_scores, plot_point_forecasts, \
    plot_point_metrics

# ------------------------------------------------------------------------------------------------------------------
# PARAMETERS
# ------------------------------------------------------------------------------------------------------------------

k1 = 11 # 0 or 11
k2 = 80 # 95 or 80
output_dim = k2 - k1 + 1
model_name = 'GBR' #
n_estimators = 800
max_depth = 5
learning_rate = 1e-2
VS_days = 15

# ------------------------------------------------------------------------------------------------------------------
# DATA
# ------------------------------------------------------------------------------------------------------------------
df_inputs, df_target_pv = process_dad_data(k1=k1, k2=k2)

# ------------------------------------------------------------------------------------------------------------------
# DAD FORECASTER
# ------------------------------------------------------------------------------------------------------------------

print('%s model k1 = %s k2 = %s n_estimators = %s lr = %s max_depth = %s' % (model_name, k1, k2, n_estimators, learning_rate, max_depth))

# Build a random pair of LS/VS
df_VS_inputs, df_LS_inputs, df_LS_targets, df_VS_targets = build_random_LS_VS(df_inputs=df_inputs,
                                                                              df_target_pv=df_target_pv, VS_days=VS_days,
                                                                              random_state=1)
# Reshape for GBR inputs from (nb_days, 2*output_dim) to (nb_days * output_dim, 2)
df_input_LS_reshaped = pd.concat([pd.DataFrame(data=df_LS_inputs.values[:, :output_dim].reshape(df_LS_inputs.shape[0] * output_dim)), pd.DataFrame(data=df_LS_inputs.values[:, output_dim:].reshape(df_LS_inputs.shape[0] * output_dim))], axis=1, join='inner')
df_input_VS_reshaped = pd.concat([pd.DataFrame(data=df_VS_inputs.values[:, :output_dim].reshape(df_VS_inputs.shape[0] * output_dim)), pd.DataFrame(data=df_VS_inputs.values[:, output_dim:].reshape(df_VS_inputs.shape[0] * output_dim))], axis=1, join='inner')

#####################
# Single output model
####################
# Reshape GBR targets from (nb_days, output_dim) to (nb_days * output_dim,)
df_LS_targets_reshaped = df_LS_targets.values.reshape(df_LS_targets.shape[0] * output_dim)
df_VS_targets_reshaped = df_VS_targets.values.reshape(df_VS_targets.shape[0] * output_dim)

# ------------------------------------------------------------------------------------------------------------------
# FIXME: start of student part
# Scale the inputs, implement the model, fit it, and reshape predictions

# Scale the inputs
# TODO
df_LS_scaled, df_VS_scaled = scale_data(df_input_LS_reshaped,df_input_VS_reshaped)
# Build GBR model
# TODO
model = GradientBoostingRegressor(max_depth = max_depth, n_estimators = n_estimators, learning_rate = learning_rate)
# Fit model
# TODO
model.fit(df_LS_scaled, df_LS_targets_reshaped)
model.score(df_LS_scaled, df_LS_targets_reshaped)
# Compute Predictions on VS
pred = model.predict(df_VS_scaled)
# Show results
plt.plot(df_VS_targets_reshaped)
plt.plot(pred)
plt.show()
# WARNING !!! predictions must be of shape (VS_days, output_dim) -> reshape the predictions
# TODO
predictions = pred.reshape((VS_days,output_dim))

# FIXME: end of student part
# ------------------------------------------------------------------------------------------------------------------
df_predictions = pd.DataFrame(data=predictions, index=df_VS_targets.index, columns=df_VS_targets.columns).sort_index()

# Create folder
dirname = 'export/'+model_name+'/forecasts/'
if not os.path.isdir(dirname):  # test if directory exist
    os.makedirs(dirname)
df_predictions.to_csv(dirname + 'dad_point_' + model_name + '_' + str(k1) + '_' + str(k2) + '.csv')

# ------------------------------------------------------------------------------------------------------------------
# COMPUTE NMAE and NRMSE
# ------------------------------------------------------------------------------------------------------------------
df_scores = point_scores(y_true=df_VS_targets.values, y_pred=df_predictions.values, k1=k1, k2=k2)
print(df_scores.mean())

dirname = 'export/'+model_name+'/scores/'
if not os.path.isdir(dirname):  # test if directory exist
    os.makedirs(dirname)
df_scores.to_csv(dirname + 'point_scores_' + model_name + '_' + str(k1) + '_' + str(k2) + '.csv')

plot_point_metrics(df_scores=df_scores, dir=dirname, model_name=model_name, k1=k1, k2=k2)


# ------------------------------------------------------------------------------------------------------------------
# PLOTS
# ------------------------------------------------------------------------------------------------------------------

# Create folder
dirname = 'export/'+model_name+'/figures/'
if not os.path.isdir(dirname):  # test if directory exist
    os.makedirs(dirname)

plot_point_forecasts(df_predictions=df_predictions, df_target=df_VS_targets, dir=dirname, model_name=model_name, k1=k1, k2=k2)
