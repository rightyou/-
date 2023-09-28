import pandas as pd
from matplotlib import pyplot as plt
from pylab import *
import numpy as np
import networkx as nx
import time

from openpyxl.reader.excel import load_workbook

from .EVA import *
from .Param import *
from .Road_network import *
from .Car import *
from .ChargingStation import *
from .area import *

from .data_process import *


def montecarlo(path):
    param = Param()
    simulate_num = 1

    DATA = read_Road_data(param, '{}/Road.xlsx'.format(path))
    road = Road(DATA, param)
    DATA = read_ChargingStation_data(param, '{}/Charging station.xlsx'.format(path))
    cs = CS(DATA)  # 充电站信息
    DATA = read_area_data(param, '{}/area.xlsx'.format(path))
    area = Area(DATA)

    DICT = {
        'Param': param,
        'Road': road,
        'CS': cs,
        'area': area,
    }

    monte_carlo = {
        'EVA_ub': [],
        'EVA_lb': [],
        'EVA_P_char_max': [],
        'EVA_P_dischar_max': [],
        'EVA_C_out': [],
    }  # 记录蒙特卡罗仿真结果

    # with pd.ExcelWriter('Road_flow.xlsx') as writer:
    #     for i in range(DICT['Road'].Road_num):
    #         df = pd.DataFrame(DICT['Road'].Road_flow[i, :])
    #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)

    for k in range(simulate_num):
        start = time.time()

        data = {
            'EV_BUS': np.array([]),
            'EV_T_in': np.array([]),
            'EV_T_out': np.array([]),
            'EV_SOC_in': np.array([]),
            'EV_SOC_out': np.array([]),
            'EV_C_max': np.array([]),
            'EV_P_char_max': np.array([]),
            'EV_P_dischar_max': np.array([]),
            'EV_lambda_char': np.array([]),
        }

        DATA = read_Taxi_data(param, '{}/Taxi_example.xlsx'.format(path))
        taxi = Taxi(DATA)
        DATA = read_PrivateCar_data(param, '{}/PrivateCar_example.xlsx'.format(path))
        privatecar = PrivateCar(DATA)

        dict_ = {
            'Taxi': taxi,
            'PrivateCar': privatecar,
        }
        DICT.update(dict_)

        for t in range(DICT['Param'].TT):
            taxi.behavior(data, DICT, t)
            privatecar.behavior(data, DICT, t)
            if t != DICT['Param'].TT - 1:
                DICT['Road'].Road_flow[:, t + 1] = DICT['Road'].Road_flow[:, t]

        # book = load_workbook('Road_flow.xlsx')
        # with pd.ExcelWriter('Road_flow.xlsx') as writer:
        #     writer.book = book
        #     writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        #     for i in range(DICT['Road'].Road_num):
        #         df = pd.DataFrame(DICT['Road'].Road_flow[i, :])
        #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None, startrow=0, startcol=k)

        eva = EVA(data, param)
        monte_carlo['EVA_ub'].append(eva.EVA_ub)
        monte_carlo['EVA_lb'].append(eva.EVA_lb)
        monte_carlo['EVA_P_char_max'].append(eva.EVA_P_char_max)
        monte_carlo['EVA_P_dischar_max'].append(eva.EVA_P_dischar_max)
        monte_carlo['EVA_C_out'].append(eva.EVA_C_out)


        end = time.time()
        print(end - start)

        # t = np.arange(0, 96*2, 1)
        # plt.figure()
        # for i in range(8):
        #     plt.subplot(2, 4, i+1)
        #     plt.title('NUM{}'.format(i+1))
        #     plt.plot(t, eva.EVA_lb[i], t, eva.EVA_ub[i], drawstyle='steps')
        #     # plt.plot(t,EVA.EV_P[i])
        # plt.show()

    monte_carlo['EVA_num'] = len(monte_carlo['EVA_ub'][0])
    monte_carlo['EVA_BUS'] = np.arange(monte_carlo['EVA_num'])
    n = len(monte_carlo['EVA_ub'])

    d = np.array(monte_carlo['EVA_P_char_max'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    monte_carlo['EVA_P_char_max'] = fit[k]

    d = np.array(monte_carlo['EVA_P_dischar_max'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    monte_carlo['EVA_P_dischar_max'] = fit[k]

    d = np.array(monte_carlo['EVA_ub'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    monte_carlo['EVA_ub'] = fit[k]

    # with pd.ExcelWriter('EVA_ub.xlsx') as writer:
    #     df = pd.DataFrame(monte_carlo['EVA_ub'] * param.SB)
    #     df.to_excel(writer, sheet_name='fit', index=None)
    #     for i in range(len(d[0])):
    #         df = pd.DataFrame(d[:, i] * param.SB)
    #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)

    d = np.array(monte_carlo['EVA_lb'])
    fit = np.sort(d, axis=0)
    k = n - math.ceil(0.75 * n)
    monte_carlo['EVA_lb'] = fit[k]

    # with pd.ExcelWriter('EVA_lb.xlsx') as writer:
    #     df = pd.DataFrame(monte_carlo['EVA_lb'] * param.SB)
    #     df.to_excel(writer, sheet_name='fit', index=None)
    #     for i in range(len(d[0])):
    #         df = pd.DataFrame(d[:, i] * param.SB)
    #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)

    d = np.array(monte_carlo['EVA_C_out'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    monte_carlo['EVA_C_out'] = fit[k]

    monte_carlo['EVA_C'] = np.zeros((monte_carlo['EVA_num'], 96 * 2))
    disordered_charging = np.zeros((monte_carlo['EVA_num'], 96 * 2))
    for i in range(monte_carlo['EVA_num']):
        for j in range(96 * 2):
            # monte_carlo['EVA_C'][i, j] = sum(monte_carlo['EVA_P'][i,:j] - monte_carlo['EVA_C_out'][i, :j])
            disordered_charging[i, j] = monte_carlo['EVA_ub'][i, j] - monte_carlo['EVA_ub'][i, j - 1]

    # with pd.ExcelWriter('EVA_C_out.xlsx') as writer:
    #     df = pd.DataFrame(monte_carlo['EVA_C_out'] * param.SB)
    #     df.to_excel(writer, sheet_name='fit', index=None)
    #     for i in range(len(d[0])):
    #         df = pd.DataFrame(d[:, i] * param.SB)
    #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)

    return monte_carlo, eva


    pass