import numpy as np
import pandas as pd


def rand_data(data, variance, number):
    # 将一组数据转化成按正态分布的多组数据
    # line = pd.read_excel(excel_name, header=0, index_col=0).values
    rand = []
    for i in range(len(data)):
        rand.append(np.random.normal(data[i], variance[i], number))

    DATA = np.stack(rand, 1)

    return DATA


def read_EV_data(param, file):
    DATA = {}
    data = pd.read_excel(file)
    DATA['EV_BUS'] = np.array(data['BUS'])
    DATA['EV_T_in'] = np.array(data['T_in'])
    DATA['EV_T_out'] = np.array(data['T_out'])
    DATA['EV_SOC_in'] = np.array(data['SOC_in'])
    DATA['EV_SOC_out'] = np.array(data['SOC_out'])
    DATA['EV_C_max'] = np.array(data['C_max']) / param.SB
    DATA['EV_P_char_max'] = np.array(data['P_char_max']) / param.SB
    DATA['EV_lambda_char'] = np.array(data['lambda_char'])
    return DATA

def read_Road_data(param, file):
    DATA = {}
    data = pd.read_excel(file)
    DATA['area_num'] = max(data['area_to'])
    DATA['Road_network'] = np.stack((np.array(data['area_from']), np.array(data['area_to'])), 1)
    DATA['Road_length'] = np.array(data['road_length'])
    DATA['Road_grade'] = np.array(data['road_grade'])
    DATA['Road_capacity'] = np.array(data['road_capacity'])
    return DATA

def read_ChargingStation_data(param, file, Price):
    DATA = {}
    data = pd.read_excel(file)
    DATA['CS_BUS'] = np.array(data['BUS'])
    DATA['CS_area'] = np.array(data['area'])
    DATA['CS_charging_pile_num'] = np.array(data['charging_pile_num'])
    CS_Price = np.zeros([len(DATA['CS_BUS']), param.T])
    for i in range(len(DATA['CS_BUS'])):
        CS_Price[i] = Price[DATA['CS_BUS'][i]]
    DATA['CS_Price'] = CS_Price
    return DATA

def read_Taxi_data(param, file):
    DATA = {}
    #  每例生成按正态分布的100组数据
    data = pd.read_excel(file)
    number = 100
    DATArand = None
    for i in range(data.shape[0]):
        rand = np.concatenate((

            np.rint(rand_data(
                [data['C_max'][i],data['T_start'][i],data['T_end'][i],],
                [data['C_max_variance'][i],data['T_start_variance'][i],data['T_end_variance'][i],],
                number)),

            np.around((rand_data(
                [data['SOC_start'][i],data['v'][i],data['P'][i],data['P_charge'][i],data['P_discharge'][i],],
                [data['SOC_start_variance'][i],data['v_variance'][i],data['P_variance'][i],data['P_charge_variance'][i],data['P_discharge_variance'][i],],
                number)), 1),

            np.random.choice(list(map(int,data['area_start'][i].split(','))),size=(number,1)),
            np.random.choice(list(map(float,data['SOC_end'][i].split(','))),size=(number,1)),
            np.array(([[data['SOC_warn'][i], data['P_charge_lambda'][i]]] * number), ),
            ),axis=1)
        if i == 0:
            DATArand = rand
        else:
            DATArand = np.concatenate((DATArand,rand),0)
    df = pd.DataFrame(DATArand, columns=['C_max', 'T_start', 'T_end', 'SOC_start', 'v', 'P', 'P_charge', 'P_discharge', 'area_start', 'SOC_end', 'SOC_warn', 'P_charge_lambda'])  # 按前面变量顺序排列
    name = file.replace('_example', '')
    df.to_excel(name, sheet_name='Sheet1', index=None)

    data = pd.read_excel(name)
    DATA['Car_C_max'] = np.array(data['C_max']) / param.SB
    DATA['Car_P'] = np.array(data['P']) / param.SB
    # DATA['Car_type'] = data['type'].values
    DATA['Car_area_start'] = np.array(data['area_start'])
    DATA['Car_T_start'] = np.array(data['T_start'])
    DATA['Car_P_charge'] = np.array(data['P_charge']) / param.SB * 24 / param.TT
    DATA['Car_P_discharge'] = -np.array(data['P_discharge']) / param.SB * 24 / param.TT
    DATA['Car_T_start'] = np.array(data['T_start'])
    DATA['Car_v'] = np.array(data['v']) * 24 / param.TT
    DATA['Car_SOC_start'] = np.array(data['SOC_start'])
    DATA['Car_SOC_end'] = np.array(data['SOC_end'])
    DATA['Car_SOC_warn'] = np.array(data['SOC_warn'])
    DATA['P_charge_lambda'] = np.array(data['P_charge_lambda'])
    # DATA['Car_area_end'] = np.array(data['area_end'])
    DATA['Car_T_end'] = np.array(data['T_end'])
    return DATA

def read_PrivateCar_data(param, file):
    DATA = {}
    #  每例生成按正态分布的100组数据
    data = pd.read_excel(file)
    number = 10
    DATArand = None
    for i in range(data.shape[0]):
        rand = np.concatenate((

            np.rint(rand_data(
                [data['C_max'][i],data['T_start'][i],data['T_end'][i],],
                [data['C_max_variance'][i],data['T_start_variance'][i],data['T_end_variance'][i],],
                number)),

            np.around((rand_data(
                [data['SOC_start'][i],data['v'][i],data['P'][i],data['P_charge'][i],data['P_discharge'][i],],
                [data['SOC_start_variance'][i],data['v_variance'][i],data['P_variance'][i],data['P_charge_variance'][i],data['P_discharge_variance'][i],],
                number)),1),

            np.random.choice(list(map(int,data['area_start'][i].split(','))),size=(number,1)),
            np.random.choice(list(map(float,data['SOC_end'][i].split(','))),size=(number,1)),
            np.array(([[data['SOC_warn'][i], data['P_charge_lambda'][i]]] * number),),
            np.random.choice(list(map(float,data['Car_area_end'][i].split(','))),size=(number,1)),),
            axis=1)
        if i == 0:
            DATArand = rand
        else:
            DATArand = np.concatenate((DATArand,rand),0)
    df = pd.DataFrame(DATArand, columns=['C_max', 'T_start', 'T_end', 'SOC_start', 'v', 'P', 'P_charge', 'P_discharge', 'area_start', 'SOC_end', 'SOC_warn', 'P_charge_lambda', 'Car_area_end'])  # 按前面变量顺序排列
    name = file.replace('_example', '')
    df.to_excel(name, sheet_name='Sheet1', index=None)

    data = pd.read_excel(name)
    DATA['Car_C_max'] = np.array(data['C_max']) / param.SB
    DATA['Car_P'] = np.array(data['P']) / param.SB
    # DATA['Car_type'] = data['type'].values
    DATA['Car_area_start'] = np.array(data['area_start'])
    DATA['Car_T_start'] = np.array(data['T_start'])
    DATA['Car_P_charge'] = np.array(data['P_charge']) / param.SB * 24 / param.TT
    DATA['Car_P_discharge'] = -np.array(data['P_discharge']) / param.SB * 24 / param.TT
    DATA['Car_T_start'] = np.array(data['T_start'])
    DATA['Car_v'] = np.array(data['v']) * 24 / param.TT
    DATA['Car_SOC_start'] = np.array(data['SOC_start'])
    DATA['Car_SOC_end'] = np.array(data['SOC_end'])
    DATA['Car_SOC_warn'] = np.array(data['SOC_warn'])
    DATA['P_charge_lambda'] = np.array(data['P_charge_lambda'])
    DATA['Car_area_end'] = np.array(data['Car_area_end'])
    # DATA['Car_area_end'] = np.array(data['area_end'])
    DATA['Car_T_end'] = np.array(data['T_end'])
    return DATA

def read_area_data(param, file):
    DATA = {}
    data = pd.read_excel(file)
    DATA['BUS'] = np.array(data['BUS'])
    DATA['area'] = np.array(data['area'])
    DATA['destination_probability'] = np.array(data.T.tail(96))
    return DATA