import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import networkx as nx
import time

from openpyxl.reader.excel import load_workbook

from procedure.EVA import *
from procedure.ED import *
from procedure.RES import *
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
from procedure.MajorNetwork import MAJOR

from procedure.data_process import *
from procedure.Monte_Carlo import *



if __name__ == '__main__':
    DN_LIST = []
    param = Param()
    DATA = {
        'T': param.T,
        'TT': param.TT,
        'UB': param.UB,
        'SB': param.SB,
        'RB': param.RB,
    }

    DATA = read_PowerFlow_data(DATA, 'data/MajorNetwork/PowerFlow.xlsx')
    DATA = read_DistributionNetwork_data(DATA, 'data/MajorNetwork/DistributionNetwork.xlsx')
    major = MAJOR(DATA)

    DATA = read_EDG_data(DATA, 'data/MajorNetwork/EDG.xlsx')
    edg = EDG(DATA)

    MN_DICT = {
        'MAJOR': major,
        'EDG': edg,
    }

    for i in range(major.DistributionNetwork_num):
        Monte_Carlo(DN_LIST, 'data/DistributionNetwork{}'.format(i + 1), major, i)

    major.DC_OPF(MN_DICT)


    for i in range(major.DistributionNetwork_num):
        DN_LIST[i]['DISTR'].DistributionNetwork_DA(DN_LIST[i], major.DistributionNetwork_P[i])

    pass


    # # 日前调度
    # DA_EVA = DA()
    # DA_EVA.SP(DICT, Monte_Carlo)
    #
    # Monte_Carlo['EVA_C'] = np.zeros((len(Monte_Carlo['EVA_P']), 96*2))
    # disordered_charging = np.zeros((len(Monte_Carlo['EVA_P']), 96*2))
    # for i in range(len(Monte_Carlo['EVA_P'])):
    #     for j in range(96*2):
    #         Monte_Carlo['EVA_C'][i, j] = sum(Monte_Carlo['EVA_P'][i,:j] - Monte_Carlo['EVA_C_out'][i, :j])
    #         disordered_charging[i, j] = Monte_Carlo['EVA_ub'][i, j] - Monte_Carlo['EVA_ub'][i, j-1]
    #
    #
    # # df = pd.DataFrame(Monte_Carlo['EVA_C'] * param.SB)
    # # df.to_excel('EVA_C.xlsx', sheet_name='Sheet1', index=None)
    # # df = pd.DataFrame(np.stack(((disordered_charging.sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB, (Monte_Carlo['EVA_P'].sum(0)[:96] + DICT['ED'].EDBase.sum(0)[:96]) * param.SB)))
    # # df.to_excel('DA.xlsx', sheet_name='Sheet1', index=None)
    #
    #
    #
    # DICT['EVA'] = eva
    #
    # # 日内调度
    # id = ID()
    # # id.SP(DICT, Monte_Carlo)
    # for t in range(1, param.T*2-4):
    #     id.SP(t, DICT, Monte_Carlo)
    #
    # DICT['EVA'].EV_distribution(DICT)



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
    #
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
    #
    #
    #
    #
    pass
