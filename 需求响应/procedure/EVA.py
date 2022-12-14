import numpy as np
import pandas as pd
import math
from gurobipy import *
from 需求响应.procedure import show


class EVA():
    def __init__(self, data_):
        self.EVA_P = None
        self.EV_BUS = data_['EV_BUS']
        self.EV_T_in = data_['EV_T_in']
        self.EV_T_out = data_['EV_T_out']
        self.EV_SOC_in = data_['EV_SOC_in']
        self.EV_SOC_out = data_['EV_SOC_out']
        self.EV_C_max = data_['EV_C_max']
        self.EV_P_char_max = data_['EV_P_char_max']
        self.EV_lambda_char = data_['EV_lambda_char']
        self.EVA_BUS = np.unique(self.EV_BUS)

        EVA_ub = np.zeros((len(self.EVA_BUS), data_['T']))
        EVA_lb = np.zeros((len(self.EVA_BUS), data_['T']))
        EVA_P_char_max = np.zeros((len(self.EVA_BUS), data_['T']))
        EVA_C_out = np.zeros((len(self.EVA_BUS), data_['T']))  # 电动汽车离开时带走的电量
        for i in range(len(self.EV_BUS)):
            P = self.EV_lambda_char[i]*self.EV_P_char_max[i]
            EVA_P_char_max[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]:self.EV_T_out[i]+1] += P
            delta_T = math.ceil(self.EV_C_max[i]*(self.EV_SOC_out[i]-self.EV_SOC_in[i])/P)
            if self.EV_T_out[i]-self.EV_T_in[i] < delta_T:
                for j in range(self.EV_T_out[i]-self.EV_T_in[i]):
                    EVA_ub[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]+j+1:self.EV_T_out[i]+1] += P  # 实际时间与索引序号差一
                EVA_lb[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]+1:self.EV_T_out[i]+1] = EVA_ub[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]+1:self.EV_T_out[i]+1]
                EVA_C_out[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]),self.EV_T_out[i]+1] += P*(self.EV_T_out[i]-self.EV_T_in[i])
            else:
                for j in range(delta_T):
                    EVA_ub[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]+j+1:self.EV_T_in[i]+delta_T+1] += P
                    EVA_ub[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i] + delta_T+1:self.EV_T_out[i]+1] += P
                    EVA_lb[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_out[i]:self.EV_T_out[i]-j-1:-1] += P
                EVA_C_out[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_out[i]+1] += EVA_lb[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_out[i]]
        self.EVA_ub = EVA_ub
        self.EVA_lb = EVA_lb
        self.EVA_P_char_max = EVA_P_char_max
        self.EVA_C_out = EVA_C_out

    def EV_distribution_consist(self, dict_):
        SOC = 1-self.EV_SOC_in
        T = dict_['Param'].T
        self.EV_P = np.zeros((len(self.EV_BUS),T))
        for i in range(len(self.EVA_BUS)):
            for j in range(T):
                # 能量缓冲系数一致性
                model = Model('EV_distribution')
                num = []
                for m in range(len(self.EV_BUS)):
                    if self.EV_BUS[m]==self.EVA_BUS[i] and self.EV_T_in[m]<=j<=self.EV_T_out[m]:
                        num.append(m)

                EV_ = model.addVars(len(num), vtype=GRB.CONTINUOUS, name='EV_P')
                lambda_ = model.addVar(vtype=GRB.CONTINUOUS,name='lambda')

                model.addConstr((quicksum(EV_[k]*SOC[num[k]] for k in range(len(EV_)))==lambda_*len(EV_)),name='A')
                model.addConstr((quicksum(EV_[k] for k in range(len(EV_)))==self.EVA_P[i,j]),name='B')

                model.setObjective(quicksum((EV_[k]*SOC[num[k]]-lambda_)**2 for k in range(len(EV_))),GRB.MINIMIZE)

                # model.write('out.lp')
                model.setParam("OutputFlag", 0)
                model.setParam('Nonconvex', 2)
                model.setParam("MIPGap", 0)
                model.optimize()

                EV_P = show.single_var(EV_, len(EV_))
                for k in range(len(EV_)):
                    SOC[num[k]] -= EV_P[k]/self.EV_C_max[num[k]]
                    self.EV_P[num[k],j] = EV_P[k]


    # 改进一致性算法
    def EV_distribution(self, dict_):
        T = dict_['Param'].T

        EV_P_max = self.EV_lambda_char * self.EV_P_char_max
        EV_lb = np.zeros((len(self.EV_BUS),T))  # 确定完成电动汽车需求的最小充电曲线边界，考虑最大充电功率和电网实际供电量
        for i in range(len(self.EV_BUS)):
            delta_T = math.ceil(self.EV_C_max[i] * (self.EV_SOC_out[i] - self.EV_SOC_in[i]) / EV_P_max[i])
            if self.EV_T_out[i] - self.EV_T_in[i] < delta_T:
                EV_lb[i, self.EV_T_out[i]] = (self.EV_T_out[i] - self.EV_T_in[i]) * EV_P_max[i]
            else:
                EV_lb[i,self.EV_T_out[i]] = self.EV_C_max[i]*(self.EV_SOC_out[i]-self.EV_SOC_in[i])
            for j in range(1,self.EV_T_out[i]-self.EV_T_in[i]):
                EV_lb[i,self.EV_T_out[i]-j] = max(EV_lb[i,self.EV_T_out[i]-j+1]-EV_P_max[i], EV_lb[i,self.EV_T_out[i]-j+1]-self.EVA_P[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]),self.EV_T_out[i]-j+1])

        SOC = 1 - self.EV_SOC_in
        self.EV_P = np.zeros((len(self.EV_BUS), T))
        for i in range(len(self.EVA_BUS)):
            for j in range(T):
                # 能量缓冲系数一致性
                model = Model('EV_distribution')


                num = []
                for m in range(len(self.EV_BUS)):
                    if self.EV_BUS[m] == self.EVA_BUS[i] and self.EV_T_in[m] <= j <= self.EV_T_out[m]:
                        num.append(m)

                EV_ = model.addVars(len(num), vtype=GRB.CONTINUOUS, lb=EV_lb[num[:],j]-np.sum(self.EV_P[num[:],:j],1), name='EV_P')
                lambda_ = model.addVar(vtype=GRB.CONTINUOUS, name='lambda')

                model.addConstr((quicksum(EV_[k] * SOC[num[k]] for k in range(len(EV_))) == lambda_ * len(EV_)),name='A')
                model.addConstr((quicksum(EV_[k] for k in range(len(EV_))) == self.EVA_P[i, j]), name='B')

                model.setObjective(quicksum((EV_[k] * SOC[num[k]] - lambda_) ** 2 for k in range(len(EV_))),GRB.MINIMIZE)


                # model.write('out.lp')
                model.setParam("OutputFlag", 0)
                model.setParam('Nonconvex', 2)
                model.setParam("MIPGap", 0)
                model.optimize()

                ######## 未将电动汽车充电曲线转化为电网实际供电量（除以充电效率）
                EV_P = show.single_var(EV_, len(EV_))
                for k in range(len(EV_)):
                    SOC[num[k]] -= EV_P[k] / self.EV_C_max[num[k]]
                    self.EV_P[num[k], j] = EV_P[k]




        pass