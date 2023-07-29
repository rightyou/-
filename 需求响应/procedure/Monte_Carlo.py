import pandas as pd
from matplotlib import pyplot as plt
from pylab import *
import numpy as np
import networkx as nx
import time

from openpyxl.reader.excel import load_workbook

from 需求响应.procedure.EVA import *
from 需求响应.procedure.ED import *
from 需求响应.procedure.RES import *
from 需求响应.procedure.Param import *
from 需求响应.procedure.DistributionNetwork import *
from 需求响应.procedure.DA import *
from 需求响应.procedure.ID import *
from 需求响应.procedure.PowerFlow import *
from 需求响应.procedure.EDG import *
from 需求响应.procedure.Road_network import *
from 需求响应.procedure.Car import *
from 需求响应.procedure.ChargingStation import *
from 需求响应.procedure.area import *

from 需求响应.procedure.data_process import *


def Monte_Carlo(LIST, path, major, BUS):
    param = Param()
    DATA = {
        'T': param.T,
        'TT': param.TT,
        'UB': param.UB,
        'SB': param.SB,
        'RB': param.RB,
    }

    DATA = read_PowerFlow_data(DATA, '{}/PowerFlow.xlsx'.format(path))
    powerflow = PowerFlow(DATA)
    DATA = read_Price_data(DATA, '{}/Price.xlsx'.format(path))
    DATA = read_ED_data(DATA, '{}/EDBase.xlsx'.format(path))
    ed = ED(DATA)
    # DATA = read_EDGub_data(DATA, '{}/EDGub.xlsx'.format(path))
    # DATA = read_EDGlb_data(DATA, '{}/EDGlb.xlsx'.format(path))
    # DATA = read_EDGPrice_data(DATA, '{}/EDGPrice.xlsx'.format(path))
    # edg = EDG(DATA)
    DATA = read_RES_data(DATA, '{}/RES.xlsx'.format(path))
    res = RES(DATA)
    DATA = read_Road_data(DATA, '{}/Road.xlsx'.format(path))
    road = Road(DATA)
    DATA = read_ChargingStation_data(DATA, '{}/Charging station.xlsx'.format(path))
    cs = CS(DATA)  # 充电站信息
    DATA = read_area_data(DATA, '{}/area.xlsx'.format(path))
    area = Area(DATA)

    DICT = {
        'Param': param,
        'Price': DATA['Price'],
        'PowerFlow': powerflow,
        'ED': ed,
        'RES': res,
        # 'EDG': edg,
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

    for k in range(1):
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
        DATA.update(data)

        DATA = read_Taxi_data(DATA, '{}/Taxi_example.xlsx'.format(path))
        taxi = Taxi(DATA)
        DATA = read_PrivateCar_data(DATA, '{}/PrivateCar_example.xlsx'.format(path))
        privatecar = PrivateCar(DATA)

        dict_ = {
            'Taxi': taxi,
            'PrivateCar': privatecar,
        }
        DICT.update(dict_)

        for t in range(DICT['Param'].TT):
            taxi.behavior(DATA, DICT, t)
            privatecar.behavior(DATA, DICT, t)
            if t != DICT['Param'].TT - 1:
                DICT['Road'].Road_flow[:, t + 1] = DICT['Road'].Road_flow[:, t]

        # book = load_workbook('Road_flow.xlsx')
        # with pd.ExcelWriter('Road_flow.xlsx') as writer:
        #     writer.book = book
        #     writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        #     for i in range(DICT['Road'].Road_num):
        #         df = pd.DataFrame(DICT['Road'].Road_flow[i, :])
        #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None, startrow=0, startcol=k)

        eva = EVA(DATA)
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

    # 配电网可调能力边界聚合模型
    distr = DISTR(monte_carlo)
    distr.AdjustableBoundaryAggregation(DICT)
    DICT['DISTR'] = distr


    LIST.append(DICT)

    # t = np.arange(0, 96, 1)
    # plt.figure()
    # plt.xlabel('t', fontsize=15, loc='right')
    # plt.ylabel('Demand', fontsize=15, loc='top')
    # plt.xticks(fontsize=15)
    # plt.yticks(fontsize=15)
    # plt.plot(t, (disordered_charging.sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]), drawstyle='steps', label='disordered_charging')
    # plt.plot(t, distr.P_LO, drawstyle='steps', label='LO')
    # plt.plot(t, distr.P_UP, drawstyle='steps', label='UP')
    # plt.legend(loc='upper right', fontsize=15)
    # plt.show()


    major.distr_UP[BUS, :distr.T_Adjust1] = distr.P_UP
    major.distr_LO[BUS, :distr.T_Adjust1] = distr.P_LO



    pass