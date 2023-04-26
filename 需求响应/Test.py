from matplotlib import pyplot as plt
import numpy as np
import networkx as nx
import time

from procedure.data_process import *
from procedure.EVA import *
from procedure.ED import *
from procedure.Param import *
from procedure.DA import *
from procedure.PowerFlow import *
from procedure.EDG import *
from procedure.Road_network import *
from procedure.Car import *
from procedure.ChargingStation import *
from procedure.area import *


if __name__ == '__main__':
    param = Param()
    UB = 10
    SB = 10000
    RB = 1

    data_ = {
        'T': param.T,
        'TT': param.TT,
        'UB':UB,
        'SB':SB,
        'RB':RB
    }
    data_ = read_PowerFlow_data(data_, 'data/PowerFlow.xlsx')
    powerflow = PowerFlow(data_)
    data_ = read_Price_data(data_, 'data/Price.xlsx')

    # data_ = read_EV_data(data_, 'data/EVA.xlsx')
    # EVA = EVA(data_)
    data_ = read_ED_data(data_, 'data/EDBase.xlsx')
    ed = ED(data_)
    data_ = read_EDGub_data(data_, 'data/EDGub.xlsx')
    data_ = read_EDGlb_data(data_, 'data/EDGlb.xlsx')
    data_ = read_EDGPrice_data(data_, 'data/EDGPrice.xlsx')
    edg = EDG(data_)
    data_ = read_Road_data(data_, 'data/Road.xlsx')
    road = Road(data_)
    data_ = read_ChargingStation_data(data_, 'data/Charging station.xlsx')
    cs = CS(data_)  # 充电站信息
    data_ = read_area_data(data_, 'data/area.xlsx')
    area = Area(data_)

    dict_ = {
        'Param': param,
        'Price': data_['Price'],
        'PowerFlow': powerflow,
        'ED': ed,
        'EDG': edg,
        'Road': road,
        'CS': cs,
        'area': area,
    }


    L = {
        'EVA_ub': [],
        'EVA_lb': [],
        'EVA_P_char_max': [],
        'EVA_C_out': [],
    }
    for k in range(3):
        start = time.time()

        data = {
            'EV_BUS': np.array([]),
            'EV_T_in': np.array([]),
            'EV_T_out': np.array([]),
            'EV_SOC_in': np.array([]),
            'EV_SOC_out': np.array([]),
            'EV_C_max': np.array([]),
            'EV_P_char_max': np.array([]),
            'EV_lambda_char': np.array([]),
        }
        data_.update(data)

        data_ = read_Taxi_data(data_, 'data/Taxi_example.xlsx')
        Taxi_ = Taxi(data_)
        data_ = read_PrivateCar_data(data_, 'data/PrivateCar_example.xlsx')
        PrivateCar_ = PrivateCar(data_)

        d = {
            'Taxi': Taxi_,
            'PrivateCar': PrivateCar_,
        }
        dict_.update(d)


        for t in range(dict_['Param'].TT):
            Taxi_.behavior(data_, dict_, t)
            PrivateCar_.behavior(data_,dict_, t)
            if t != dict_['Param'].TT-1:
                dict_['Road'].Road_flow[:, t+1] = dict_['Road'].Road_flow[:, t]
            else:
                dict_['Road'].Road_flow = np.zeros((dict_['Road'].Road_num, data_['TT']))

        EVA_ = EVA(data_)
        L['EVA_ub'].append(EVA_.EVA_ub)
        L['EVA_lb'].append(EVA_.EVA_lb)
        L['EVA_P_char_max'].append(EVA_.EVA_P_char_max)
        L['EVA_C_out'].append(EVA_.EVA_C_out)
        end = time.time()
        print(end - start)


        # G = nx.Graph()
        # for node in range(1, 30):
        #     G.add_node(str(node))
        # for i in range(29):
        #     for j in range(i):
        #         if Road.road_network[i, j] != 0:
        #             G.add_edge(str(i + 1), str(j + 1), length=Road.road_network[i, j])
        # nx.draw(G, with_labels=True, node_color='y')
        # plt.show()


        # t = np.arange(0, 96*2, 1)
        # plt.figure()
        # for i in range(8):
        #     plt.subplot(2, 4, i+1)
        #     plt.title('NUM{}'.format(i+1))
        #     plt.plot(t, EVA_.EVA_lb[i], t, EVA_.EVA_ub[i], drawstyle='steps')
        #     # plt.plot(t,EVA.EV_P[i])
        # plt.show()



    L['EVA_ub'] = np.mean(np.asarray(L['EVA_ub']), axis=0)
    L['EVA_lb'] = np.mean(np.asarray(L['EVA_lb']), axis=0)
    L['EVA_P_char_max'] = np.mean(np.asarray(L['EVA_P_char_max']), axis=0)
    L['EVA_C_out'] = np.mean(np.asarray(L['EVA_C_out']), axis=0)
    L['EVA_num'] = len(L['EVA_ub'])
    L['EVA_BUS'] = np.arange(L['EVA_num'])


    t = np.arange(0, 96*2, 1)
    plt.figure()
    for i in range(8):
        plt.subplot(2, 4, i+1)
        plt.title('NUM{}'.format(i+1))
        plt.plot(t, L['EVA_lb'][i], t, L['EVA_ub'][i], drawstyle='steps')
        # plt.plot(t,EVA.EV_P[i])
    plt.show()


    DA_EVA = DA_SP()
    DA_EVA.SP(dict_, L)

    L['EVA_C'] = np.zeros((len(L['EVA_P']), 96*2))
    for i in range(len(L['EVA_P'])):
        for j in range(96*2):
            L['EVA_C_out_'] = sum(L['EVA_C_out'][i,:j])
            L['EVA_C'][i, j] = sum(L['EVA_P'][i,:j]) - L['EVA_C_out_']


    t = np.arange(0, 96 * 2, 1)
    plt.figure()
    for i in range(8):
        plt.subplot(2, 4, i + 1)
        plt.title('NUM{}'.format(i + 1))
        plt.plot(t, L['EVA_ub'][i]+dict_['ED'].EDBase[i], t, L['EVA_C'][i]+dict_['ED'].EDBase[i], drawstyle='steps')
        # plt.plot(t,EVA.EV_P[i])
    plt.show()

    t = np.arange(0, 96*2, 1)
    plt.figure()
    for i in range(8):
        plt.subplot(2, 4, i+1)
        plt.title('NUM{}'.format(i+1))
        plt.plot(t, L['EVA_lb'][i], t, L['EVA_ub'][i], t, L['EVA_C'][i], drawstyle='steps')
        # plt.plot(t,EVA.EV_P[i])
    plt.show()



    pass
