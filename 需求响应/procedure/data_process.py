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


def read_PowerFlow_data(data_, file):
    data = pd.read_excel(file)
    data_['Branch_BUS'] = np.array((data['BUS1'],data['BUS2'])).T
    data_['Branch_R'] = np.array(data['R'])
    data_['Branch_X'] = np.array(data['X'])
    data_['Branch_B'] = np.array(data['B'])
    return data_


def read_EV_data(data_, file):
    data = pd.read_excel(file)
    data_['EV_BUS'] = np.array(data['BUS'])
    data_['EV_T_in'] = np.array(data['T_in'])
    data_['EV_T_out'] = np.array(data['T_out'])
    data_['EV_SOC_in'] = np.array(data['SOC_in'])
    data_['EV_SOC_out'] = np.array(data['SOC_out'])
    data_['EV_C_max'] = np.array(data['C_max'])
    data_['EV_P_char_max'] = np.array(data['P_char_max'])
    data_['EV_lambda_char'] = np.array(data['lambda_char'])
    return data_


def read_ED_data(data_, file):
    data = pd.read_excel(file)
    data_['ED_BUS'] = np.array(data['BUS'])
    data_['EDBase'] = np.array(data.T.tail(data_['T']).T)
    return data_


def read_Price_data(data_, file):
    data = pd.read_excel(file)
    data_['Price'] = np.array(data.values[0])
    return data_

def read_EDGub_data(data_, file):
    data = pd.read_excel(file)
    data_['EDG_BUS'] = np.array(data['BUS'])
    data_['EDG_ub'] = np.array(data.T.tail(data_['T']).T)
    return data_

def read_EDGlb_data(data_, file):
    data = pd.read_excel(file)
    data_['EDG_lb'] = np.array(data.T.tail(data_['T']).T)
    return data_

def read_EDGPrice_data(data_, file):
    data = pd.read_excel(file)
    data_['EDGPrice'] = np.array(data.T.tail(3).T)
    return data_