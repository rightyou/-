import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import networkx as nx
import time

from openpyxl.reader.excel import load_workbook

from procedure.data_process import *
from procedure.EVA import *
from procedure.ED import *
from procedure.Param import *
from procedure.DistributionNetwork import *
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


    Monte_Carlo = {
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
            'EV_P_dischar_max': np.array([]),
            'EV_lambda_char': np.array([]),
        }
        DATA.update(data)

        DATA = read_Taxi_data(DATA, 'data/Taxi_example.xlsx')
        taxi = Taxi(DATA)
        DATA = read_PrivateCar_data(DATA, 'data/PrivateCar_example.xlsx')
        privatecar = PrivateCar(DATA)

        d = {
            'Taxi': taxi,
            'PrivateCar': privatecar,
        }
        DICT.update(d)


        for t in range(DICT['Param'].TT):
            taxi.behavior(DATA, DICT, t)
            privatecar.behavior(DATA, DICT, t)
            if t != DICT['Param'].TT-1:
                DICT['Road'].Road_flow[:, t + 1] = DICT['Road'].Road_flow[:, t]

        # book = load_workbook('Road_flow.xlsx')
        # with pd.ExcelWriter('Road_flow.xlsx') as writer:
        #     writer.book = book
        #     writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        #     for i in range(DICT['Road'].Road_num):
        #         df = pd.DataFrame(DICT['Road'].Road_flow[i, :])
        #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None, startrow=0, startcol=k)


        eva = EVA(DATA)
        Monte_Carlo['EVA_ub'].append(eva.EVA_ub)
        Monte_Carlo['EVA_lb'].append(eva.EVA_lb)
        Monte_Carlo['EVA_P_char_max'].append(eva.EVA_P_char_max)
        Monte_Carlo['EVA_P_dischar_max'].append(eva.EVA_P_dischar_max)
        Monte_Carlo['EVA_C_out'].append(eva.EVA_C_out)
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


    Monte_Carlo['EVA_num'] = len(Monte_Carlo['EVA_ub'][0])
    Monte_Carlo['EVA_BUS'] = np.arange(Monte_Carlo['EVA_num'])
    n = len(Monte_Carlo['EVA_ub'])

    d = np.array(Monte_Carlo['EVA_P_char_max'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    Monte_Carlo['EVA_P_char_max'] = fit[k]

    d = np.array(Monte_Carlo['EVA_P_dischar_max'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    Monte_Carlo['EVA_P_dischar_max'] = fit[k]

    d = np.array(Monte_Carlo['EVA_ub'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    Monte_Carlo['EVA_ub'] = fit[k]

    # with pd.ExcelWriter('EVA_ub.xlsx') as writer:
    #     df = pd.DataFrame(Monte_Carlo['EVA_ub'] * param.SB)
    #     df.to_excel(writer, sheet_name='fit', index=None)
    #     for i in range(len(d[0])):
    #         df = pd.DataFrame(d[:, i] * param.SB)
    #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)

    d = np.array(Monte_Carlo['EVA_lb'])
    fit = np.sort(d, axis=0)
    k = n - math.ceil(0.75 * n)
    Monte_Carlo['EVA_lb'] = fit[k]

    # with pd.ExcelWriter('EVA_lb.xlsx') as writer:
    #     df = pd.DataFrame(Monte_Carlo['EVA_lb'] * param.SB)
    #     df.to_excel(writer, sheet_name='fit', index=None)
    #     for i in range(len(d[0])):
    #         df = pd.DataFrame(d[:, i] * param.SB)
    #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)

    d = np.array(Monte_Carlo['EVA_C_out'])
    fit = np.sort(d, axis=0)
    k = math.ceil(0.75 * n) - 1
    Monte_Carlo['EVA_C_out'] = fit[k]

    Monte_Carlo['EVA_C'] = np.zeros((9, 96*2))
    disordered_charging = np.zeros((9, 96*2))
    for i in range(9):
        for j in range(96*2):
            # Monte_Carlo['EVA_C'][i, j] = sum(Monte_Carlo['EVA_P'][i,:j] - Monte_Carlo['EVA_C_out'][i, :j])
            disordered_charging[i, j] = Monte_Carlo['EVA_ub'][i, j] - Monte_Carlo['EVA_ub'][i, j-1]

    # with pd.ExcelWriter('EVA_C_out.xlsx') as writer:
    #     df = pd.DataFrame(Monte_Carlo['EVA_C_out'] * param.SB)
    #     df.to_excel(writer, sheet_name='fit', index=None)
    #     for i in range(len(d[0])):
    #         df = pd.DataFrame(d[:, i] * param.SB)
    #         df.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)



    # 配电网可调能力边界聚合模型
    distr = DISTR()
    distr.AdjustableBoundaryAggregation(DICT, Monte_Carlo)

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


    # 日前调度
    DA_EVA = DA()
    DA_EVA.SP(DICT, Monte_Carlo)

    Monte_Carlo['EVA_C'] = np.zeros((len(Monte_Carlo['EVA_P']), 96*2))
    disordered_charging = np.zeros((len(Monte_Carlo['EVA_P']), 96*2))
    for i in range(len(Monte_Carlo['EVA_P'])):
        for j in range(96*2):
            Monte_Carlo['EVA_C'][i, j] = sum(Monte_Carlo['EVA_P'][i,:j] - Monte_Carlo['EVA_C_out'][i, :j])
            disordered_charging[i, j] = Monte_Carlo['EVA_ub'][i, j] - Monte_Carlo['EVA_ub'][i, j-1]


    # df = pd.DataFrame(Monte_Carlo['EVA_C'] * param.SB)
    # df.to_excel('EVA_C.xlsx', sheet_name='Sheet1', index=None)
    # df = pd.DataFrame(np.stack(((disordered_charging.sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, (Monte_Carlo['EVA_P'].sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB)))
    # df.to_excel('DA.xlsx', sheet_name='Sheet1', index=None)



    DICT['EVA'] = eva

    # 日内调度
    id = ID()
    # id.SP(DICT, Monte_Carlo)
    for t in range(1, param.T*2-4):
        id.SP(t, DICT, Monte_Carlo)

    DICT['EVA'].EV_distribution(DICT)



    # with pd.ExcelWriter('evaID.xlsx') as writer:
    #     for i in range(DICT['EVA'].EVA_num):
    #         df = pd.DataFrame(np.stack((Monte_Carlo['EVA_lb'][i,:96] * param.SB, Monte_Carlo['EVA_ub'][i,:96] * param.SB, DICT['EVA'].EVA_lb[i,:96] * param.SB, DICT['EVA'].EVA_ub[i,:96] * param.SB)))
    #         df.to_excel(writer, sheet_name='EVAb{}'.format(i), index=None)
    #         df = pd.DataFrame(np.stack((Monte_Carlo['EVA_C'][i, :96] * param.SB, DICT['EVA'].EVA_C[i, :96] * param.SB)))
    #         df.to_excel(writer, sheet_name='EVA_C{}'.format(i), index=None)
    #
    # df = [[] for x in range(DICT['EVA'].EVA_num)]
    # for i in range(DICT['EVA'].EV_num):
    #     df[DICT['EVA'].EV_BUS[i]].append(DICT['EVA'].EV_P[i, :96])
    #
    # with pd.ExcelWriter('EV.xlsx') as writer:
    #     for i in range(DICT['EVA'].EVA_num):
    #         di = pd.DataFrame(df[i])
    #         di.to_excel(writer, sheet_name='Sheet{}'.format(i), index=None)


    #
    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i+1)
    #     plt.title('NUM{}'.format(i+1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, Monte_Carlo['EVA_lb'][i,:96] * param.SB, drawstyle='steps', label='EVA_lb')
    #     plt.plot(t, Monte_Carlo['EVA_ub'][i,:96] * param.SB, drawstyle='steps', label='EVA_ub')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure1.svg', dpi=300)
    #
    # t = np.arange(0, 96, 1)
    # plt.figure()
    # # plt.title('', fontsize=7)
    # plt.xlabel('t', fontsize=5, loc='right')
    # plt.ylabel('Demand', fontsize=5, loc='top')
    # plt.xticks(fontsize=5)
    # plt.yticks(fontsize=5)
    # plt.plot(t, (disordered_charging.sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, drawstyle='steps', label='disordered_charging')
    # plt.plot(t, (Monte_Carlo['EVA_P'].sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, drawstyle='steps', label='ordered_charging')
    # plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure2.svg', dpi=300)
    #
    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i+1)
    #     plt.title('NUM{}'.format(i+1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, Monte_Carlo['EVA_lb'][i,:96] * param.SB, drawstyle='steps', label='EVA_lb')
    #     plt.plot(t, Monte_Carlo['EVA_ub'][i,:96] * param.SB, drawstyle='steps', label='EVA_ub')
    #     plt.plot(t, Monte_Carlo['EVA_C'][i,:96] * param.SB, drawstyle='steps', label='EVA_C')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure3.svg', dpi=300)
    #
    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i+1)
    #     plt.title('NUM{}'.format(i+1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, Monte_Carlo['EVA_lb'][i,:96] * param.SB, drawstyle='steps', label='DA_EVA_lb')
    #     plt.plot(t, Monte_Carlo['EVA_ub'][i,:96] * param.SB, drawstyle='steps', label='DA_EVA_ub')
    #     plt.plot(t, DICT['EVA'].EVA_lb[i,:96] * param.SB, drawstyle='steps', label='ID_EVA_lb')
    #     plt.plot(t, DICT['EVA'].EVA_ub[i,:96] * param.SB, drawstyle='steps', label='ID_EVA_ub')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure4.svg', dpi=300)
    #
    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i + 1)
    #     plt.title('NUM{}'.format(i + 1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('Demand', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, (Monte_Carlo['EVA_C'][i, :96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, drawstyle='steps', label='DA')
    #     plt.plot(t, (DICT['EVA'].EVA_C[i, :96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, drawstyle='steps', label='ID')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure5.svg', dpi=300)
    #
    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i + 1)
    #     plt.title('NUM{}'.format(i + 1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    #     plt.plot(t, Monte_Carlo['EVA_C'][i, :96] * param.SB, drawstyle='steps', label='DA')
    #     plt.plot(t, DICT['EVA'].EVA_C[i, :96] * param.SB, drawstyle='steps', label='ID')
    #     plt.legend(loc='upper right', fontsize=5)
    # plt.show()
    # # plt.savefig('figure6.svg', dpi=300)

    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(9):
    #     plt.subplot(2, 5, i + 1)
    #     plt.title('NUM{}'.format(i + 1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    # for i in range(DICT['EVA'].EV_num):
    #     plt.subplot(2, 5, DICT['EVA'].EV_BUS[i]+1)
    #     plt.plot(t, DICT['EVA'].EV_P[i, :96], drawstyle='steps')
    # plt.show()
    # # plt.savefig('figure8.svg', dpi=300)
    #
    # t = np.arange(0, 96, 1)
    # plt.figure()
    # for i in range(8):
    #     plt.subplot(2, 4, i + 1)
    #     plt.title('NUM{}'.format(i + 1), fontsize=7)
    #     plt.xlabel('t', fontsize=5, loc='right')
    #     plt.ylabel('d_EVA', fontsize=5, loc='top')
    #     plt.xticks(fontsize=5)
    #     plt.yticks(fontsize=5)
    # for i in range(DICT['EVA'].EV_num):
    #     if DICT['EVA'].EV_BUS[i] == 0:
    #         continue
    #     plt.subplot(2, 4, DICT['EVA'].EV_BUS[i])
    #     plt.plot(t, DICT['EVA'].EV_P[i, :96], drawstyle='steps')
    # plt.show()
    # # plt.savefig('figure7.svg', dpi=300)




    pass
