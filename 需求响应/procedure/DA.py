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
        EVA_lb = dict_['EVA'].EVA_lb
        EVA_ub = dict_['EVA'].EVA_ub
        EVA_P_char_max = dict_['EVA'].EVA_P_char_max
        EVA_C_out = dict_['EVA'].EVA_C_out

        # 添加变量
        '''
        EDG_ - 发电机发电功率
        EVA_ - 电动汽车集合充电站实际充电功率（非电网进入充电站功率）
        '''
        EDG_ = model.addVars(len(EDG_ub), T, vtype=GRB.CONTINUOUS, lb=EDG_lb, ub=EDG_ub, name='EDG')
        EVA_ = model.addVars(len(EVA_ub), T, vtype=GRB.CONTINUOUS, ub=EVA_P_char_max, name='EVA')

        # 添加约束
        '''
        EVA_C - 电动汽车集合充电功率曲线约束
        PowerBalance - 功率平衡
        PowerFlow_constraint - 网络潮流约束
        '''
        for i in range(len(EVA_ub)):
            for j in range(T):
                model.addConstr((quicksum(EVA_[i,k]-EVA_C_out[i,k] for k in range(j+1))<=EVA_ub[i,j]), name='EVA_C_max')  # 电动汽车当天累计充电电量减去汽车离开时的所冲电量落在充电功率曲线中
        for i in range(len(EVA_ub)):
            for j in range(T):
                model.addConstr((quicksum(EVA_[i,k]-EVA_C_out[i,k] for k in range(j+1))>=EVA_lb[i,j]), name='EVA_C_min')
        for j in range(T):
            model.addConstr((quicksum(EDG_[m,j] for m in range(len(EDG_ub)))-quicksum(EVA_[n,j] for n in range(len(EVA_ub)))-ED.sum(0)[j]==0),name='PowerBalance')

        # 目标设置
        model.setObjective(quicksum((quicksum(EVA_[n,j] for n in range(len(EVA_ub)))+ED.sum(0)[j]-ED_avg)**2 for j in range(T)),GRB.MINIMIZE)


        # 模型求解
        # model.write('out.lp')
        model.setParam("OutputFlag", 0)
        model.setParam('Nonconvex', 2)
        model.setParam("MIPGap", 0)
        model.optimize()

        dict_['EDG'].EDG_P = show.double_var(EDG_, len(EDG_ub), T)
        dict_['EVA'].EVA_P = show.double_var(EVA_, len(EVA_ub), T)

        pass


