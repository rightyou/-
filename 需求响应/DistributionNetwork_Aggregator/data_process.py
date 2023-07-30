import numpy as np
import pandas as pd


def read_DistributionNetwork_data(DATA, file):
    data = pd.read_excel(file)
    DATA['DistributionNetwork_BUS'] = np.array(data['BUS'])
    return DATA

def read_PowerFlow_data(param, file):
    data = pd.read_excel(file)
    DATA = {}
    DATA['Branch_BUS'] = np.array((data['BUS1'],data['BUS2'])).T
    DATA['Branch_R'] = np.array(data['R']) / param.RB
    DATA['Branch_X'] = np.array(data['X']) / param.RB
    DATA['Branch_B'] = np.array(data['B'])
    return DATA

def read_ED_data(param, file):
    data = pd.read_excel(file)
    DATA = {}
    DATA['ED_BUS'] = np.array(data['BUS'])
    DATA['EDBase'] = np.array(data.T.tail(param.T*2).T) / param.SB * 10  # ！！！
    return DATA

def read_EDG_data(DATA, file):
    data = pd.read_excel(file)
    DATA['EDG_BUS'] = np.array(data['BUS'])
    DATA['EDGPrice_a'] = np.array(data['a'])
    DATA['EDGPrice_b'] = np.array(data['b'])
    DATA['EDGPrice_c'] = np.array(data['c'])
    DATA['EDG_UB'] = -np.array(data['UB']) / DATA['SB']
    return DATA

def read_RES_data(param, file):
    data = pd.read_excel(file)
    DATA = {}
    DATA['RES_BUS'] = np.array(data['BUS'])
    DATA['P_RES'] = -np.array(data.T.tail(param.T*2).T) / param.SB
    return DATA

