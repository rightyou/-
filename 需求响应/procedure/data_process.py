import numpy as np
import pandas as pd


def rand_data(data, variance, number):
    # 将一组数据转化成按正态分布的多组数据
    # line = pd.read_excel(excel_name, header=0, index_col=0).values
    rand = []
    for i in range(len(data)):
        rand.append(np.random.normal(data[i], variance[i], number))

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

def read_Road_data(data_, file):
    data = pd.read_excel(file)
    data_['area_num'] = max(data['area_to'])
    data_['Road_network'] = np.stack((np.array(data['area_from']), np.array(data['area_to'])), 1)
    data_['Road_length'] = np.array(data['road_length'])
    data_['Road_grade'] = np.array(data['road_grade'])
    data_['Road_capacity'] = np.array(data['road_capacity'])
    return data_

def read_Taxi_data(data_, file):
    #  每例生成按正态分布的100组数据
    data = pd.read_excel(file)
    number = 100
    data_rand = None
    for i in range(data.shape[0]):
        rand = np.concatenate((

            np.rint(rand_data(
            [data['C_max'][i],data['P'][i],data['T_start'][i],data['T_end'][i],data['P_charge'][i],],
            [data['C_max_variance'][i],data['P_variance'][i],data['T_start_variance'][i],data['T_end_variance'][i],data['P_charge_variance'][i],],
            number)),

            np.around((rand_data([data['v'][i]],[data['v_variance'][i]], number)),1),
            np.random.choice(list(map(int,data['area_start'][i].split(','))),size=(number,1)),
            np.random.choice(list(map(float,data['SOC_start'][i].split(','))),size=(number,1)),
            np.array(([[data['SOC_warn'][i],data['SOC_baseline'][i]]]*100),),),
            axis=1)
        if i == 0:
            data_rand = rand
        else:
            data_rand = np.concatenate((data_rand,rand),0)
    df = pd.DataFrame(data_rand, columns=['C_max', 'P', 'T_start', 'T_end', 'P_charge', 'v',  'area_start', 'SOC_start', 'SOC_warn', 'SOC_baseline'])  # 按前面变量顺序排列
    df.to_excel('data/Taxi.xlsx', sheet_name='Sheet1', index=None)

    data = pd.read_excel('data/Taxi.xlsx')
    data_['Car_C_max'] = np.array(data['C_max'])
    data_['Car_P'] = np.array(data['P'])
    # data_['Car_type'] = data['type'].values
    data_['Car_area_start'] = np.array(data['area_start'])
    data_['Car_T_start'] = np.array(data['T_start'])
    data_['Car_P_charge'] = np.array(data['P_charge'])
    data_['Car_T_start'] = np.array(data['T_start'])
    data_['Car_v'] = np.array(data['v'])
    data_['Car_SOC_start'] = np.array(data['SOC_start'])
    data_['Car_SOC_warn'] = np.array(data['SOC_warn'])
    data_['Car_SOC_baseline'] = np.array(data['SOC_baseline'])
    # data_['Car_area_end'] = np.array(data['area_end'])
    data_['Car_T_end'] = np.array(data['T_end'])
    return data_
