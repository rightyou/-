from gurobipy import *
import numpy as np
from 需求响应.procedure.show import *


class DA_SP():
    def __init__(self, dict_):
        '''
            （1）功能解释：
            本函数旨在利用随即规划方法，解决日内不确定性优化问题
            对象：无拓扑约束下的1基础出力1空调集合1电动汽车集合1上层电网的经济调度问题
            （2）输入dict
            dict_['para_DG']-基础出力成本参数
            dict_['EDG_up_down']-基础出力上下限
            dict_['ERES_up']-光伏出力的上限，分为3个场景
            dict_['ACA_up_down']-空调负荷需求上下限
            dict_['EV_up_down']-电动汽车负荷需求上下限
            dict_['EVA_up_down']-电动汽车集群负荷需求上下限
            dict_['EDBase']-基础负荷需求
            dict_['SPrice']-向上层电网售电价格
            dict_['BPrice']-向上层电网购电价格
            数据类型全部为numpy的array形式或为数值
            （3）输出
            result_['EDG_']-实际基础出力
            result_['ESTG_']-向上层电网售电量
            result_['EBFG_']-向上层电网购电量
            result_['obj_']-总的期望成本
        '''

        # self.para_DG = dict_['para_DG']
        # self.EDG_up_down = dict_['EDG_up_down']
        # self.ACA_up_down = dict_['ACA_up_down']
        # self.EVA_up_down = dict_['EVA_up_down']
        # self.EDBase = dict_['EDBase']
        # self.SPrice = dict_['SPrice']
        # self.BPrice = dict_['BPrice']
        # self.EDG = np.zeros((1, 96))
        # self.ESTG = np.zeros((1, 96))
        # self.EBFG = np.zeros((1, 96))
        # self.RES = np.zeros((1, 96))
        # self.EVA = np.zeros((1, 96))

    def Solve(self, dict_):
        model = Model('SP')

        T = dict_['T']
        ED_ = dict_['EDBase']
        scenario_num = dict_['scenario_num']
        EDGPrice =dict_['EDGPrice']
        SPrice = dict_['SPrice']
        BPrice = dict_['BPrice']
        P = dict_['P']

        # 变量设置
        EDG_ = model.addVars(T, vtype=GRB.CONTINUOUS, lb=dict_['EDG_down'], ub=dict_['EDG_up'], name='EDG')
        EBFG_ = model.addVars(T, vtype=GRB.CONTINUOUS, lb=0, name='EBFG')
        ESTG_ = model.addVars(T, vtype=GRB.CONTINUOUS, lb=0, name='ESTG')
        RES_ = model.addVars(scenario_num, T, vtype=GRB.CONTINUOUS, lb=0, ub=dict_['RES_up'], name='RES')
        EVA_ = model.addVars(scenario_num, T, vtype=GRB.CONTINUOUS, lb=dict_['EVA_down'], ub=dict_['EVA_up'], name='EVA')

        # 约束设置
        for i in range(scenario_num):
            model.addConstrs((EDG_[j] + RES_[i, j] + EBFG_[j] - ESTG_[j] - EVA_[i, j] - ED_[i, j] == 0 for j in range(T)), name='power_balance')

        # 目标设置
        model.setObjective(quicksum((EDG_[j]**2)*EDGPrice[0, 0] + EDG_[j]*EDGPrice[0, 1] + EDGPrice[0, 2]
                                    + EBFG_[j]*BPrice[0, j] - ESTG_[j]*SPrice[0, j] for j in range(T)), GRB.MINIMIZE)

        # 模型求解
        model.write('out.lp')
        model.setParam("OutputFlag", 0)
        # model.setParam('Nonconvex', 2)
        model.setParam("MIPGap", 0)
        model.optimize()

        self.EDG = single_var(EDG_, T)
        self.ESTG = single_var(ESTG_, T)
        self.EBFG = single_var(EBFG_, T)
        self.RES = double_var(RES_, 1, T)
        self.EVA = double_var(EVA_, 1, T)

        result = {'EDG': self.EDG,
                  'EBFG': self.EBFG,
                  'ESTG': self.ESTG,
                  'RES': self.RES,
                  'EVA': self.EVA
                  }

        print(result)
