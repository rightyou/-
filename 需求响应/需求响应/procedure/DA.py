from gurobipy import *
import numpy as np
from 需求响应.procedure import show

class DA_EVA():
    def __init__(self):
        pass

    def SP(self, dict_):
        model = Model('DA_SP')

        T = dict_['Param'].T
        Price = dict_['Price']
        ED = dict_['ED'].EDBase
        ED_avg = dict_['ED'].ED_avg
        EDG_lb = dict_['EDG'].EDG_lb
        EDG_ub = dict_['EDG'].EDG_ub
        EDGPrice = dict_['EDG'].EDGPrice
        EVA_num = dict_['EVA'].EVA_num
        EVA_BUS = dict_['EVA'].EVA_BUS
        EVA_lb = dict_['EVA'].EVA_lb
        EVA_ub = dict_['EVA'].EVA_ub
        EVA_P_char_max = dict_['EVA'].EVA_P_char_max
        EVA_C_out = dict_['EVA'].EVA_C_out

        # 添加变量
        '''
        Us,Is 支路电压，电流平方变量
        P_input,Q_input 节点注入有功，无功
        P_branch,Q_branch 支路有功，无功变量
        EDG_ - 发电机发电功率
        EVA_ - 电动汽车集合充电站实际充电功率（非电网进入充电站功率）
        k1,k2 - 求解峰谷差最小化目标函数参数
        '''
        Us_ = model.addVars(dict_['PowerFlow'].BUS_num, T, vtype=GRB.CONTINUOUS, lb=0.95**2, ub=1.05**2, name='Us')
        Is_ = model.addVars(dict_['PowerFlow'].Branch_num, T, vtype=GRB.CONTINUOUS, lb=0, name='Is')
        P_input = model.addVars(dict_['PowerFlow'].BUS_num, T, vtype=GRB.CONTINUOUS, name='P_input')
        Q_input = model.addVars(dict_['PowerFlow'].BUS_num, T, vtype=GRB.CONTINUOUS, name='Q_input')
        P_branch = model.addVars(dict_['PowerFlow'].Branch_num, T, vtype=GRB.CONTINUOUS, lb=P_branch_lb, ub=P_branch_ub, name='P_branch')
        Q_branch = model.addVars(dict_['PowerFlow'].Branch_num, T, vtype=GRB.CONTINUOUS, lb=Q_branch_lb, ub=Q_branch_ub, name='Q_branch')

        EDG_ = model.addVars(len(EDG_ub), T, vtype=GRB.CONTINUOUS, lb=EDG_lb, ub=EDG_ub, name='EDG')
        EVA_ = model.addVars(EVA_num, T, vtype=GRB.CONTINUOUS, ub=EVA_P_char_max, name='EVA')
        k1 = model.addVar(vtype=GRB.CONTINUOUS, name='k1')
        k2 = model.addVar(vtype=GRB.CONTINUOUS, name='k2')

        # 添加约束
        '''
        EVA_C - 电动汽车集合充电功率曲线约束
        PowerBalance - 功率平衡
        PowerFlow_constraint - 网络潮流约束
        Us_constraint 节点电压约束
        P_constraint 潮流上下限约束
        second_order_cone 二阶锥约束条件
        '''
        for j in range(T):

            # 电动汽车集合充电功率曲线约束
            for i in range(EVA_num):
                model.addConstr((quicksum(EVA_[i,k]-EVA_C_out[i,k] for k in range(j+1))<=EVA_ub[i,j]), name='EVA_C_max')  # 电动汽车当天累计充电电量减去汽车离开时的所冲电量落在充电功率曲线中
                model.addConstr((quicksum(EVA_[i,k]-EVA_C_out[i,k] for k in range(j+1))>=EVA_lb[i,j]), name='EVA_C_min')

            # 节点注入功率
            model.addConstrs(P_input[i, j] ==
                quicksum(EVA_[l, j] for l in range(EVA_num) if EVA_BUS[l] == i) +
                quicksum()
                for i in range(dict_['PowerFlow'].Branch_num + 1))  # 节点0与上层电网相连接

            # 功率平衡(待修改)
            model.addConstr((quicksum(EDG_[m,j] for m in range(len(EDG_ub)))-quicksum(EVA_[n,j] for n in range(EVA_num))-ED.sum(0)[j]==0),name='PowerBalance')

            # 网络潮流约束
            for i in range(dict_['PowerFlow'].Branch_num):
                head = dict_['PowerFlow'].Branch_BUS[i, 0]
                back = dict_['PowerFlow'].Branch_BUS[i, 1]

                model.addConstr(Us_[back, j] == Us_[head, j] -
                    2*(dict_['PowerFlow'].Branch_R[i, j]*P_branch[i, j] + dict_['PowerFlow'].Branch_X[i, j]*Q_branch[i, j]) +
                    Is_[i, j] * (dict_['PowerFlow'].Branch_R[i, j] ** 2 + dict_['PowerFlow'].Branch_X[i, j] ** 2))
                model.addConstr(Us_[0] == 1.05**2)

                model.addConstr(P_input[back, j] == P_branch[i, j] - Is_[i, j]**2 * dict_['PowerFlow'].Branch_R[i, j] -
                    quicksum(P_branch[m, j] for m in range(dict_['PowerFlow'].Branch_num) if back in dict_['PowerFlow'].Branch_BUS[m, 0]))

                model.addConstr(Q_input[back, j] == Q_branch[i, j] - Is_[i, j]**2 * dict_['PowerFlow'].Branch_X[i, j] -
                    quicksum(Q_branch[m, j] for m in range(dict_['PowerFlow'].Branch_num) if back in dict_['PowerFlow'].Branch_BUS[m, 0]))

                model.addConstr(4*P_branch[i]**2 + 4*Q_branch[i]**2 + (Is_[i] - Us_[head])**2 <= (Is_[i] + Us_[head])**2)

            # 最优化约束条件
            model.addConstr((k1 <= ED.sum(0)[j] + quicksum(EVA_[n, j] for n in range(EVA_num))), name='k1_constraint')
            model.addConstr((k2 >= ED.sum(0)[j] + quicksum(EVA_[n, j] for n in range(EVA_num))), name='k2_constraint')


        # 目标设置

        model.setObjective(k2-k1,GRB.MINIMIZE)


        # 模型求解
        # model.write('out.lp')
        model.setParam("OutputFlag", 0)
        model.setParam('Nonconvex', 2)
        model.setParam("MIPGap", 0)
        model.optimize()

        dict_['EDG'].EDG_P = show.double_var(EDG_, len(EDG_ub), T)
        dict_['EVA'].EVA_P = show.double_var(EVA_, EVA_num, T)

        pass




