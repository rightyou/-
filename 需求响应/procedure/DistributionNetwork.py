import numpy as np
import pandas as pd
import math
from gurobipy import *
from 需求响应.procedure import show


class DISTR():
    def __init__(self):
        '''
        P_UP 配电网可调上边界
        P_LO 配电网可调下边界
        :param DICT:
        '''

        # T = DICT['Param'].T
        self.P_UP = None
        self.P_LO = None

        self.T_Adjust0 = 50  # 35
        self.T_Adjust1 = 60  # 65


    def AdjustableBoundaryAggregation(self, DICT, Monte_Carlo):
        '''
        配电网可调能力边界聚合模型
        :param DICT:
        :param Monte_Carlo:
        :return:
        T_Adjust 需求响应调度区间
        '''

        T = DICT['Param'].T

        ED_num = DICT['ED'].ED_num
        ED_BUS = DICT['ED'].ED_BUS
        ED = DICT['ED'].EDBase
        ED_avg = DICT['ED'].ED_avg

        EVA_num = Monte_Carlo['EVA_num']
        EVA_BUS = Monte_Carlo['EVA_BUS']
        EVA_lb = Monte_Carlo['EVA_lb']
        EVA_ub = Monte_Carlo['EVA_ub']
        EVA_P_dischar_max = Monte_Carlo['EVA_P_dischar_max']
        EVA_P_char_max = Monte_Carlo['EVA_P_char_max']
        EVA_C_out = Monte_Carlo['EVA_C_out']

        Branch_R = DICT['PowerFlow'].Branch_R
        Branch_X = DICT['PowerFlow'].Branch_X
        Branch_num = DICT['PowerFlow'].Branch_num
        Branch_BUS = DICT['PowerFlow'].Branch_BUS
        BUS_num = DICT['PowerFlow'].BUS_num


        model = Model('ABA')

        # 添加变量
        '''
        _UP 配电网可调上边界
        _LO 配电网可调下边界
        Us,Is 支路电压，电流平方变量
        P_input,Q_input 节点注入有功，无功
        P_branch,Q_branch 支路有功，无功变量
        EDG_ - 发电机发电功率
        eva - 电动汽车集合充电站实际充电功率（非电网进入充电站功率）
        '''
        Us_UP = model.addVars(int(BUS_num), T, vtype=GRB.CONTINUOUS, lb=9.5 ** 2, ub=10.5 ** 2, name='Us')
        Is_UP = model.addVars(int(Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, name='Is')
        P_UP_input = model.addVars(int(BUS_num), T, vtype=GRB.CONTINUOUS, name='P_input')
        Q_UP_input = model.addVars(int(BUS_num), T, vtype=GRB.CONTINUOUS, name='Q_input')
        P_UP_branch = model.addVars(int(Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, ub=float('inf'), name='P_branch')
        Q_UP_branch = model.addVars(int(Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, ub=float('inf'), name='Q_branch')

        Us_LO = model.addVars(int(BUS_num), T, vtype=GRB.CONTINUOUS, lb=9.5 ** 2, ub=10.5 ** 2, name='Us')
        Is_LO = model.addVars(int(Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, name='Is')
        P_LO_input = model.addVars(int(BUS_num), T, vtype=GRB.CONTINUOUS, name='P_input')
        Q_LO_input = model.addVars(int(BUS_num), T, vtype=GRB.CONTINUOUS, name='Q_input')
        P_LO_branch = model.addVars(int(Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, ub=float('inf'), name='P_branch')
        Q_LO_branch = model.addVars(int(Branch_num), T, vtype=GRB.CONTINUOUS, lb=0, ub=float('inf'), name='Q_branch')

        P_EVA_UP = model.addVars(EVA_num, T, vtype=GRB.CONTINUOUS, lb=EVA_P_dischar_max[:, :T], ub=EVA_P_char_max[:, :T], name='P_EVA')
        C_EVA_UP = model.addVars(EVA_num, T, vtype=GRB.CONTINUOUS, name='C_EVA')
        P_EVA_LO = model.addVars(EVA_num, T, vtype=GRB.CONTINUOUS, lb=EVA_P_dischar_max[:, :T], ub=EVA_P_char_max[:, :T], name='P_EVA')
        C_EVA_LO = model.addVars(EVA_num, T, vtype=GRB.CONTINUOUS, name='C_EVA')


        for t in range(T):
            # 电动汽车集合充电功率曲线约束
            for i in range(EVA_num):
                model.addConstr((C_EVA_UP[i, t] == quicksum(P_EVA_UP[i,k] - EVA_C_out[i,k] for k in range(t))), name='EVA_C')
                model.addConstr((C_EVA_UP[i, t] <= EVA_ub[i,t]), name='EVA_C_max')  # 电动汽车当天累计充电电量减去汽车离开时的所冲电量落在充电功率曲线中
                model.addConstr((quicksum(P_EVA_UP[i,k] - EVA_C_out[i,k] for k in range(t)) >= EVA_lb[i,t]), name='EVA_C_min')
            for i in range(EVA_num):
                model.addConstr((C_EVA_LO[i, t] == quicksum(P_EVA_LO[i,k] - EVA_C_out[i,k] for k in range(t))), name='EVA_C')
                model.addConstr(C_EVA_LO[i, t] <= EVA_ub[i,t], name='EVA_C_max')  # 电动汽车当天累计充电电量减去汽车离开时的所冲电量落在充电功率曲线中
                model.addConstr((quicksum(P_EVA_LO[i,k] - EVA_C_out[i,k] for k in range(t)) >= EVA_lb[i,t]), name='EVA_C_min')


            # 节点注入功率
            model.addConstrs((P_UP_input[i, t] ==
                              quicksum(P_EVA_UP[n, t] for n in range(EVA_num) if EVA_BUS[n] == i) +
                              quicksum(ED[n, t] for n in range(ED_num) if ED_BUS[n] == i)
                              for i in range(1, BUS_num)), name='P_input')  # 节点0与上层电网相连接
            model.addConstrs((P_LO_input[i, t] ==
                              quicksum(P_EVA_LO[n, t] for n in range(EVA_num) if EVA_BUS[n] == i) +
                              quicksum(ED[n, t] for n in range(ED_num) if ED_BUS[n] == i)
                              for i in range(1, BUS_num)), name='P_input')  # 节点0与上层电网相连接


            # 网络潮流约束
            model.addConstr(Us_UP[0, t] == 10.5 ** 2)
            model.addConstr(Us_LO[0, t] == 10.5 ** 2)
            model.addConstr(P_UP_input[0, t] == quicksum(P_EVA_UP[n, t] for n in range(EVA_num) if EVA_BUS[n] == 0) +
                            quicksum(ED[n, t] for n in range(ED_num) if ED_BUS[n] == 0) +
                            quicksum(P_UP_branch[m, t] for m in range(Branch_num) if Branch_BUS[m, 0] == 0))
            model.addConstr(P_LO_input[0, t] == quicksum(P_EVA_LO[n, t] for n in range(EVA_num) if EVA_BUS[n] == 0) +
                            quicksum(ED[n, t] for n in range(ED_num) if ED_BUS[n] == 0) +
                            quicksum(P_LO_branch[m, t] for m in range(Branch_num) if Branch_BUS[m, 0] == 0))

            for i in range(Branch_num):
                head = Branch_BUS[i, 0]
                back = Branch_BUS[i, 1]

                model.addConstr((Us_UP[back, t] == Us_UP[head, t] -
                                 2 * (Branch_R[i] * P_UP_branch[i, t] + Branch_X[i] * Q_UP_branch[i, t]) +
                                 Is_UP[i, t] * (Branch_R[i] ** 2 + Branch_X[i] ** 2)), name='Us')
                model.addConstr((Us_LO[back, t] == Us_LO[head, t] -
                                 2 * (Branch_R[i] * P_LO_branch[i, t] + Branch_X[i] * Q_LO_branch[i, t]) +
                                 Is_LO[i, t] * (Branch_R[i] ** 2 + Branch_X[i] ** 2)), name='Us')

                model.addConstr((P_UP_branch[i, t] == P_UP_input[back, t] + Is_UP[i, t] * Branch_R[i] +
                                 quicksum(P_UP_branch[m, t] for m in range(Branch_num) if Branch_BUS[m, 0] == back)), name='P_branch')
                model.addConstr((P_LO_branch[i, t] == P_LO_input[back, t] + Is_LO[i, t] * Branch_R[i] +
                                 quicksum(P_LO_branch[m, t] for m in range(Branch_num) if Branch_BUS[m, 0] == back)), name='P_branch')

                model.addConstr(Q_UP_branch[i, t] == Q_UP_input[back, t] + Is_UP[i, t] * Branch_X[i] +
                                quicksum(Q_UP_branch[m, t] for m in range(Branch_num) if Branch_BUS[m, 0] == back))
                model.addConstr(Q_LO_branch[i, t] == Q_LO_input[back, t] + Is_LO[i, t] * Branch_X[i] +
                                quicksum(Q_LO_branch[m, t] for m in range(Branch_num) if Branch_BUS[m, 0] == back))

                model.addConstr(4*P_UP_branch[i, t]**2 + 4*Q_UP_branch[i, t]**2 + (Is_UP[i, t] - Us_UP[head, t])**2 <= (Is_UP[i, t] + Us_UP[head, t])**2)
                model.addConstr(4*P_LO_branch[i, t]**2 + 4*Q_LO_branch[i, t]**2 + (Is_LO[i, t] - Us_LO[head, t])**2 <= (Is_LO[i, t] + Us_LO[head, t])**2)

        # 保证调度时段前运行方式保持一致
        model.addConstrs((P_UP_input[0, t_] - P_LO_input[0, t_] == 0 for t_ in range(self.T_Adjust0)), name='control')

        # 目标设置
        model.setObjective(quicksum( - P_LO_input[0, t_]*100 for t_ in range(self.T_Adjust0, self.T_Adjust1)), GRB.MAXIMIZE)

        # 模型求解
        try:
            model.write('out.lp')
            model.setParam("OutputFlag", 0)
            model.setParam('Nonconvex', 2)
            model.setParam("MIPGap", 0)
            model.optimize()
            P_UP_input_ = show.double_var(P_UP_input, EVA_num, T)
            P_LO_input_ = show.double_var(P_LO_input, EVA_num, T)
            self.P_UP = P_UP_input_[0]
            self.P_LO = P_LO_input_[0]
        except:
            model.computeIIS()
            model.write('model.ilp')
            pass

        pass