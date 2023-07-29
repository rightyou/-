from gurobipy import *
import numpy as np
from 需求响应.procedure import show
from matplotlib import pyplot as plt

class ID():
    def __init__(self):
        pass

    def SP(self, t, DICT, Monte_Carlo):
        model = Model('ID')

        T = int(DICT['Param'].T / 24)
        Price = DICT['Price']

        ED_num = DICT['ED'].ED_num
        ED_BUS = DICT['ED'].ED_BUS
        ED = DICT['ED'].EDBase[:, t:t+T]
        ED_avg = DICT['ED'].ED_avg

        EDG_lb = DICT['EDG'].EDG_lb
        EDG_ub = DICT['EDG'].EDG_ub
        EDGPrice = DICT['EDG'].EDGPrice

        EVA_num = DICT['EVA'].EVA_num
        EVA_BUS = DICT['EVA'].EVA_BUS
        EVA_lb = DICT['EVA'].EVA_lb[:, t:t+T]
        EVA_ub = DICT['EVA'].EVA_ub[:, t:t+T]
        EVA_P_dischar_max = DICT['EVA'].EVA_P_dischar_max[:, t-1:t+T-1]
        EVA_P_char_max = DICT['EVA'].EVA_P_char_max[:, t-1:t+T-1]
        EVA_C_out = DICT['EVA'].EVA_C_out[:, t-1:t+T-1]
        EVA_C_initial = DICT['EVA'].EVA_C[:, t-1]


        # 添加变量
        '''
        Us,Is 支路电压，电流平方变量
        P_input,Q_input 节点注入有功，无功
        P_branch,Q_branch 支路有功，无功变量
        EDG_ - 发电机发电功率
        eva - 电动汽车集合充电站实际充电功率（非电网进入充电站功率）
        '''
        Us_ = model.addVars(int(DICT['PowerFlow'].BUS_num), T, vtype=GRB.CONTINUOUS, lb=9.5 ** 2, ub=10.5 ** 2, name='Us')
        Is_ = model.addVars(int(DICT['PowerFlow'].Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, name='Is')
        P_input = model.addVars(int(DICT['PowerFlow'].BUS_num), T, vtype=GRB.CONTINUOUS, name='P_input')
        Q_input = model.addVars(int(DICT['PowerFlow'].BUS_num), T, vtype=GRB.CONTINUOUS, name='Q_input')
        P_branch = model.addVars(int(DICT['PowerFlow'].Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, ub=float('inf'), name='P_branch')
        Q_branch = model.addVars(int(DICT['PowerFlow'].Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, ub=float('inf'), name='Q_branch')

        # EDG_ = model.addVars(len(EDG_ub), T, vtype=GRB.CONTINUOUS, lb=EDG_lb, ub=EDG_ub, name='EDG')
        EVA_ = model.addVars(EVA_num, T, vtype=GRB.CONTINUOUS, lb=EVA_P_dischar_max, ub=EVA_P_char_max, name='EVA')
        EVA_C = model.addVars(EVA_num, T, vtype=GRB.CONTINUOUS, name='EVA_C')

        # 添加约束
        '''
        EVA_C - 电动汽车集合充电功率曲线约束
        PowerBalance - 功率平衡
        PowerFlow_constraint - 网络潮流约束
        Us_constraint 节点电压约束
        P_constraint 潮流上下限约束
        second_order_cone 二阶锥约束条件
        '''
        for t_ in range(T):

            # 电动汽车集合充电功率曲线约束

            for i in range(EVA_num):
                model.addConstr((EVA_C[i, t_] == EVA_C_initial[i] + quicksum(EVA_[i, k] - EVA_C_out[i, k] for k in range(t_+1))), name='EVA_C')
                model.addConstr((EVA_C[i, t_] <= EVA_ub[i, t_]), name='EVA_C_max')  # 电动汽车当天累计充电电量减去汽车离开时的所冲电量落在充电功率曲线中
                model.addConstr((EVA_C[i, t_] >= EVA_lb[i, t_]), name='EVA_C_min')

            # 节点注入功率
            model.addConstrs((P_input[i, t_] ==
                              quicksum(EVA_[n, t_] for n in range(EVA_num) if EVA_BUS[n] == i) +
                              quicksum(ED[n, t_] for n in range(ED_num) if ED_BUS[n] == i)
                              for i in range(1, DICT['PowerFlow'].BUS_num)), name='P_input')  # 节点0与上层电网相连接

            # 网络潮流约束
            model.addConstr(Us_[0, t_] == 10.5 ** 2)
            model.addConstr(P_input[0, t_] == quicksum(EVA_[n, t_] for n in range(EVA_num) if EVA_BUS[n] == 0) +
                            quicksum(ED[n, t_] for n in range(ED_num) if ED_BUS[n] == 0) +
                            quicksum(P_branch[m, t_] for m in range(DICT['PowerFlow'].Branch_num) if DICT['PowerFlow'].Branch_BUS[m, 0] == 0))
            for i in range(DICT['PowerFlow'].Branch_num):
                head = DICT['PowerFlow'].Branch_BUS[i, 0]
                back = DICT['PowerFlow'].Branch_BUS[i, 1]

                model.addConstr((Us_[back, t_] == Us_[head, t_] -
                                 2 * (DICT['PowerFlow'].Branch_R[i] * P_branch[i, t_] + DICT['PowerFlow'].Branch_X[i] * Q_branch[i, t_]) +
                                 Is_[i, t_] * (DICT['PowerFlow'].Branch_R[i] ** 2 + DICT['PowerFlow'].Branch_X[i] ** 2)), name='Us')

                model.addConstr((P_branch[i, t_] == P_input[back, t_] + Is_[i, t_] * DICT['PowerFlow'].Branch_R[i] +
                                 quicksum(P_branch[m, t_] for m in range(DICT['PowerFlow'].Branch_num) if DICT['PowerFlow'].Branch_BUS[m, 0] == back)), name='P_branch')

                model.addConstr(Q_branch[i, t_] == Q_input[back, t_] + Is_[i, t_] * DICT['PowerFlow'].Branch_X[i] +
                                quicksum(Q_branch[m, t_] for m in range(DICT['PowerFlow'].Branch_num) if DICT['PowerFlow'].Branch_BUS[m, 0] == back))

                model.addConstr(4 * P_branch[i, t_] ** 2 + 4 * Q_branch[i, t_] ** 2 + (Is_[i, t_] - Us_[head, t_]) ** 2 <= (Is_[i, t_] + Us_[head, t_]) ** 2)



        # 目标设置

        model.setObjective(quicksum((EVA_C[i, t_] - Monte_Carlo['EVA_C'][i, t+t_]) ** 2 for i in range(EVA_num) for t_ in range(T)), GRB.MINIMIZE)



        # 模型求解
        try:
            model.write('out.lp')
            model.setParam("OutputFlag", 0)
            model.setParam('Nonconvex', 2)
            model.setParam("MIPGap", 0)
            model.optimize()

            # DICT['EDG'].EDG_P = show.double_var(EDG_, len(EDG_ub), T)
            DICT['EVA'].EVA_P[:, t-1] = show.double_var(EVA_, EVA_num, T)[:, 0]
            DICT['EVA'].EVA_C[:, t] = show.double_var(EVA_C, EVA_num, T)[:, 0]

        except:
            model.computeIIS()
            model.write('model.ilp')
            pass

        pass




