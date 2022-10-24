import numpy as np
import pandas as pd


def rand_data(data, variance, number):
    # 将一组数据转化成按正态分布的多组数据
    # line = pd.read_excel(excel_name, header=0, index_col=0).values
    rand = []
    for i in range(len(data)):
        rand.append(np.random.normal(data[i], variance, number))

    data_ = np.stack(rand, 1)

    return data_


def read_EV_data(dict_, file):
    data = pd.read_excel(file)
    dict_['EV_BUS'] = np.array(data['BUS'])
    dict_['EV_T_in'] = np.array(data['T_in'])
    dict_['EV_T_out'] = np.array(data['T_out'])
    dict_['EV_SOC_in'] = np.array(data['SOC_in'])
    dict_['EV_SOC_out'] = np.array(data['SOC_out'])
    dict_['EV_C_max'] = np.array(data['C_max'])
    dict_['EV_P_char_max'] = np.array(data['P_char_max'])
    dict_['EV_lambda_char'] = np.array(data['lambda_char'])
    return dict_
