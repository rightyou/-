from matplotlib import pyplot as plt
import numpy as np
import networkx as nx
import time

from procedure.data_process import *
from procedure.EVA import *
from procedure.ED import *
from procedure.Param import *
from procedure.DA import *
from procedure.ID import *
from procedure.PowerFlow import *
from procedure.EDG import *
from procedure.Road_network import *
from procedure.Car import *
from procedure.ChargingStation import *
from procedure.area import *


if __name__ == '__main__':
    param = Param()

    DATA = {
        'T': param.T,
        'TT': param.TT,
        'UB': param.UB,
        'SB': param.SB,
        'RB': param.RB,
    }
    DATA = read_PowerFlow_data(DATA, 'data/PowerFlow.xlsx')
    powerflow = PowerFlow(DATA)
    DATA = read_Price_data(DATA, 'data/Price.xlsx')
    DATA = read_ED_data(DATA, 'data/EDBase.xlsx')
    ed = ED(DATA)
    DATA = read_EDGub_data(DATA, 'data/EDGub.xlsx')
    DATA = read_EDGlb_data(DATA, 'data/EDGlb.xlsx')
    DATA = read_EDGPrice_data(DATA, 'data/EDGPrice.xlsx')
    edg = EDG(DATA)
    DATA = read_Road_data(DATA, 'data/Road.xlsx')
    road = Road(DATA)
    DATA = read_ChargingStation_data(DATA, 'data/Charging station.xlsx')
    cs = CS(DATA)  # 充电站信息
    DATA = read_area_data(DATA, 'data/area.xlsx')
    area = Area(DATA)

    DICT = {
        'Param': param,
        'Price': DATA['Price'],
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

    for k in range(10):
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
        DATA.update(data)

        DATA = read_Taxi_data(DATA, 'data/Taxi_example.xlsx')
        Taxi_ = Taxi(DATA)
        DATA = read_PrivateCar_data(DATA, 'data/PrivateCar_example.xlsx')
        PrivateCar_ = PrivateCar(DATA)

        d = {
            'Taxi': Taxi_,
            'PrivateCar': PrivateCar_,
        }
        DICT.update(d)


        for t in range(DICT['Param'].TT):
            Taxi_.behavior(DATA, DICT, t)
            PrivateCar_.behavior(DATA, DICT, t)
            if t != DICT['Param'].TT-1:
                DICT['Road'].Road_flow[:, t + 1] = DICT['Road'].Road_flow[:, t]
            # else:
            #     DICT['Road'].Road_flow = np.zeros((DICT['Road'].Road_num, DATA['TT']))

        eva = EVA(DATA)
        L['EVA_ub'].append(eva.EVA_ub)
        L['EVA_lb'].append(eva.EVA_lb)
        L['EVA_P_char_max'].append(eva.EVA_P_char_max)
        L['EVA_C_out'].append(eva.EVA_C_out)
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
        #     plt.plot(t, eva.EVA_lb[i], t, eva.EVA_ub[i], drawstyle='steps')
        #     # plt.plot(t,EVA.EV_P[i])
        # plt.show()



    L['EVA_ub'] = np.mean(np.asarray(L['EVA_ub']), axis=0)
    L['EVA_lb'] = np.mean(np.asarray(L['EVA_lb']), axis=0)
    L['EVA_P_char_max'] = np.mean(np.asarray(L['EVA_P_char_max']), axis=0)
    L['EVA_C_out'] = np.mean(np.asarray(L['EVA_C_out']), axis=0)
    L['EVA_num'] = len(L['EVA_ub'])
    L['EVA_BUS'] = np.arange(L['EVA_num'])


    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(4):
    #     plt.subplot(2, 2, i+1)
    #     plt.title('NUM{}'.format(i+1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, L['EVA_lb'][i,:96] * param.SB, drawstyle='steps', label='EVA_lb')
    #     plt.plot(t, L['EVA_ub'][i,:96] * param.SB, drawstyle='steps', label='EVA_ub')
    #     plt.legend(loc='upper right', fontsize=5)
    # # plt.show()
    # plt.savefig('figure1.svg', dpi=300)


    # 日前调度
    DA_EVA = DA()
    DA_EVA.SP(DICT, L)

    L['EVA_C'] = np.zeros((len(L['EVA_P']), 96*2))
    disordered_charging = np.zeros((len(L['EVA_P']), 96*2))
    for i in range(len(L['EVA_P'])):
        for j in range(96*2):
            # L['EVA_C_out_'] = sum(L['EVA_C_out'][i,:j])
            L['EVA_C'][i, j] = sum(L['EVA_P'][i,:j] - L['EVA_C_out'][i,:j])
            disordered_charging[i, j] = L['EVA_ub'][i, j] - L['EVA_ub'][i, j-1]


    # t = np.arange(0, 96, 1)
    # plt.figure()
    # # plt.title('', fontsize=7)
    # plt.xlabel('t', fontsize=5, loc='right')
    # plt.ylabel('Demand', fontsize=5, loc='top')
    # plt.xticks(fontsize=5)
    # plt.yticks(fontsize=5)
    # plt.plot(t, (disordered_charging.sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, drawstyle='steps', label='disordered_charging')
    # plt.plot(t, (L['EVA_P'].sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, drawstyle='steps', label='ordered_charging')
    # plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure2.svg', dpi=300)

    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(4):
    #     plt.subplot(2, 2, i+1)
    #     plt.title('NUM{}'.format(i+1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, L['EVA_lb'][i,:96] * param.SB, drawstyle='steps', label='EVA_lb')
    #     plt.plot(t, L['EVA_ub'][i,:96] * param.SB, drawstyle='steps', label='EVA_ub')
    #     plt.plot(t, L['EVA_C'][i,:96] * param.SB, drawstyle='steps', label='EVA_C')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure3.svg', dpi=300)


    DICT['EVA'] = eva
    # 日内调度
    id = ID()
    id.SP(DICT, L)

    DICT['EVA'].EV_distribution(DICT)

    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i+1)
    #     plt.title('NUM{}'.format(i+1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, L['EVA_lb'][i,:96] * param.SB, drawstyle='steps', label='DA_EVA_lb')
    #     plt.plot(t, L['EVA_ub'][i,:96] * param.SB, drawstyle='steps', label='DA_EVA_ub')
    #     plt.plot(t, DICT['EVA'].EVA_lb[i,:96] * param.SB, drawstyle='steps', label='ID_EVA_lb')
    #     plt.plot(t, DICT['EVA'].EVA_ub[i,:96] * param.SB, drawstyle='steps', label='ID_EVA_ub')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure3.svg', dpi=300)

    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i + 1)
    #     plt.title('NUM{}'.format(i + 1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, L['EVA_P'][i, :96] * param.SB, drawstyle='steps', label='DA')
    #     plt.plot(t, DICT['EVA'].EVA_P[i, :96] * param.SB, drawstyle='steps', label='ID')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure3.svg', dpi=300)

    t = np.arange(0, 96, 1)
    plt.figure()
    for i in range(8):
        plt.subplot(2, 4, i + 1)
        plt.title('NUM{}'.format(i + 1), fontsize=7)
        plt.xlabel('t', fontsize=5, loc='right')
        plt.ylabel('d_EVA', fontsize=5, loc='top')
        plt.xticks(fontsize=5)
        plt.yticks(fontsize=5)
        plt.plot(t, L['EVA_C'][i, :96] * param.SB, drawstyle='steps', label='DA')
        plt.plot(t, DICT['EVA'].EVA_C[i, :96] * param.SB, drawstyle='steps', label='ID')
        plt.legend(loc='upper right', fontsize=5)
    plt.show()
    # plt.savefig('figure3.svg', dpi=300)

    t = np.arange(0, 96, 1)
    plt.figure()
    for i in range(DICT['EVA'].EV_num):
        plt.subplot(2, 5, DICT['EVA'].EV_BUS[i]+1)
        plt.title('NUM{}'.format(i + 1), fontsize=7)
        plt.xlabel('t', fontsize=5, loc='right')
        plt.ylabel('d_EVA', fontsize=5, loc='top')
        plt.xticks(fontsize=5)
        plt.yticks(fontsize=5)
        plt.plot(t, DICT['EVA'].EV_P[i, :96] * param.SB, drawstyle='steps')
    plt.show()
    # plt.savefig('figure3.svg', dpi=300)




    pass
