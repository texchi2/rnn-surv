'''
    TODO:
    4. calculate C-Index from final predictions
    5. set up hyperparam tuning
'''

import os
import json
import numpy as np
import pandas as pd
from os.path import dirname as up
from src.models.rnnsurv import get_data, DataGenerator, create_model

MODELNAME = 'model-002'

print('Getting Data...')
BASEPATH = up(up(up(__file__)))
DATAPATH = os.path.join(BASEPATH, 'data', 'processed')
XT = get_data(path_to_file=DATAPATH, filename='rain_X_train.csv', nrows=10000)
YT = get_data(path_to_file=DATAPATH, filename='rain_y_train.csv', nrows=10000)
XV = get_data(path_to_file=DATAPATH, filename='rain_X_val.csv', nrows=4000)
YV = get_data(path_to_file=DATAPATH, filename='rain_y_val.csv', nrows=4000)

N_FEATURES = XT.shape[1] - 1 

MODEL_PARAMS = {
    'dense_sizes': (20, 10),
    'lstm_sizes': (30, 30),
    'dropout_prob': 0.5,
    'max_length': 200,
    'pad_token': -999,
    'optimizer': 'adam',
    'loss_weights': {"y_hat": 1.0, "r_out": 1.0}
}

print('Creating model...')
MODEL = create_model(N_FEATURES, **MODEL_PARAMS)

PARAMS = {
    'max_timesteps': MODEL_PARAMS['max_length'],
    'padding_token': MODEL_PARAMS['pad_token'],
    'max_batch_size': 128,
    'min_batch_size': 32,
    'shuffle': True,
}

TRAIN_GENERATOR = DataGenerator(XT, YT, **PARAMS)
VAL_GENERATOR = DataGenerator(XV, YV, validation=True, **PARAMS)

print('Training model...')
MODEL.fit(TRAIN_GENERATOR, validation_data=VAL_GENERATOR, epochs=9)

MODELPATH = os.path.join(BASEPATH, 'models')

# serialize model to JSON
MODEL_JSON = MODEL.to_json()
with open(os.path.join(MODELPATH, f"{MODELNAME}.json"), "w") as json_file:
    json_file.write(MODEL_JSON)

with open(os.path.join(MODELPATH, f"{MODELNAME}_data_params.json"), "w") as json_file:
    json_file.write(json.dumps(PARAMS))

# serialize weights to HDF5
MODEL.save_weights(os.path.join(MODELPATH, f"{MODELNAME}.h5"))
print("Saved model to disk")

