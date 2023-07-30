import numpy as np
from gurobipy import *
from gurobipy import Model
import copy
from matplotlib import pyplot as plt

from .show import *


class MAJOR():
    def __init__(self, DN_LIST, DATA, param):
        self.BUS_num = max(np.ravel(DATA['Branch_BUS']))+1  # 节点从0开始
        self.Branch_BUS = DATA['Branch_BUS']
        self.Branch_B = self.B_matrix(DATA['Branch_X'])
        self.Branch_num = len(self.Branch_BUS)
        self.Us_LB = 31.5
        self.Us_UB = 35
        self.EDG_P = None

        self.DistributionNetwork_BUS = DATA['DistributionNetwork_BUS']
        self.DistributionNetwork_num = len(self.DistributionNetwork_BUS)
        self.DistributionNetwork_P = None

        self.T = int(param.T)
        self.distr_UP = np.ones((self.DistributionNetwork_num, param.T)) * 500
        self.distr_LO = np.zeros((self.DistributionNetwork_num, param.T))
        for i in range(self.DistributionNetwork_num):
            self.distr_UP[i, :DN_LIST[i]['DISTR'].T_Adjust1] = DN_LIST[i]['DISTR'].P_UP
            self.distr_LO[i, :DN_LIST[i]['DISTR'].T_Adjust1] = DN_LIST[i]['DISTR'].P_LO

    def B_matrix(self, Branch_X):
        Branch_B = np.zeros((self.BUS_num, self.BUS_num))
        for index, [i, j] in enumerate(self.Branch_BUS):
            B = 1 / Branch_X[index]
            Branch_B[i, j] = B
            Branch_B[j, i] = B
            Branch_B[i, i] += B
            Branch_B[j, j] += B
        return Branch_B


    def circuit_set(self):
        bus = {}
        for i, j in self.Branch_BUS:
            if bus.get(i) is None:
                bus[i] = [j]
            else:
                bus[i].append(j)
            if bus.get(j) is None:
                bus[j] = [i]
            else:
                bus[j].append(i)

        circuit = [[0]]
        circuits = []
        while True:
            circuit_ = circuit.pop(0)
            i = circuit_[-1]
            for j in bus[i]:
                if j in circuit_:
                    m = circuit_.index(j)
                    circuits.append(circuit_[m:])
                    continue
                circuit.append(copy.deepcopy(circuit_))
                circuit[-1].append(j)
            if not len(circuit):
                break
        for i in copy.deepcopy(circuits):
            if len(i) < 3:
                circuits.remove(i)

        return circuits


    def DC_OPF(self, MN_DICT):
        model = Model('DC_OPF')

        # 变量
        '''
        EDG_ 发电机
        LOAD_ 负荷
        a,b,c 发电成本参数
        _UB 发电功率上界
        phase 节点电压相角
        P_input 节点注入功率
        P_Branch 支路有功
        '''
        EDG_num = MN_DICT['EDG'].EDG_num
        EDG_BUS = MN_DICT['EDG'].EDG_BUS
        EDGPrice_a = MN_DICT['EDG'].EDGPrice_a
        EDGPrice_b = MN_DICT['EDG'].EDGPrice_b
        EDGPrice_c = MN_DICT['EDG'].EDGPrice_c
        EDG_UB = np.expand_dims(MN_DICT['EDG'].EDG_UB, axis=1).repeat(self.T, axis=1)
        EDG_P = model.addVars(EDG_num, self.T, vtype=GRB.CONTINUOUS, lb=EDG_UB, ub=0, name='EDG_P')

        LOAD_P = model.addVars(int(self.DistributionNetwork_num), self.T, vtype=GRB.CONTINUOUS, lb=self.distr_LO, ub=self.distr_UP, name='LOAD_P')

        phase = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, lb=-360, ub=360, name='phase')
        P_input = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, lb=-1000000, ub=1000000, name='P_input')
        P_Branch = model.addVars(int(self.Branch_num), self.T, vtype=GRB.CONTINUOUS, lb=-1000000, ub=1000000, name='P_Branch')


        # 约束
        for t in range(self.T):
            model.addConstr(phase[0, t] == 0, name='slack bus')

            for i in range(self.BUS_num):
                # 节点注入功率
                model.addConstr(P_input[i, t] == quicksum(EDG_P[k, t] for k in range(EDG_num) if EDG_BUS[k] == i) +
                                    quicksum(LOAD_P[k, t] for k in range(self.DistributionNetwork_num) if self.DistributionNetwork_BUS[k] == i), name='input_P')

                model.addConstr(P_input[i, t] == quicksum(P_Branch[k, t] if self.Branch_BUS[k, 0] == i else -P_Branch[k, t] for k in range(self.Branch_num) if i in self.Branch_BUS[k]))

            # 直流潮流约束
            for index, [i, j] in enumerate(self.Branch_BUS):
                model.addConstr(P_Branch[index, t] == (phase[i, t] - phase[j, t]) * self.Branch_B[i, j], name='Branch_P')


        # 优化目标
        model.setObjective(quicksum(EDGPrice_a[i]*EDG_P[i, t]**2 - EDGPrice_b[i]*EDG_P[i, t] - EDGPrice_c[i] for t in range(self.T) for i in range(EDG_num)), GRB.MINIMIZE)


        try:
            model.write('out.lp')
            model.setParam("OutputFlag", 0)
            model.setParam('Nonconvex', 2)
            model.setParam("MIPGap", 0)
            model.optimize()
            self.EDG_P = double_var(EDG_P, EDG_num, self.T)
            self.DistributionNetwork_P = double_var(LOAD_P, int(self.DistributionNetwork_num), self.T)
        except:
            model.computeIIS()
            model.write('model.ilp')
            pass

        # t = np.arange(0, 96, 1)
        # plt.figure()
        # for i in range(8):
        #     plt.subplot(2, 4, i+1)
        #     plt.title('NUM{}'.format(i+1), fontsize=7)
        #     plt.xlabel('t', fontsize=5, loc='right')
        #     plt.ylabel('d_EVA', fontsize=5, loc='top')
        #     plt.xticks(fontsize=5)
        #     plt.yticks(fontsize=5)
        #     plt.plot(t, self.distr_LO[0], drawstyle='steps', label='可调下界')
        #     plt.plot(t, self.distr_UP[0], drawstyle='steps', label='EVA_ub')
        #     plt.plot(t, self.DistributionNetwork_P[0], drawstyle='steps', label='可调下界')
        #     plt.legend(loc='upper right', fontsize=5)
        # plt.show()



    def SP(self, MN_DICT):

        model = Model('MN')

        # 变量
        '''
        Us,phase 节点电压幅值，相角
        P_input,Q_input 节点注入有功，无功
        P_branch,Q_branch 支路有功，无功变量
        '''
        EDG_num = MN_DICT['EDG'].EDG_num
        EDG_BUS = MN_DICT['EDG'].EDG_BUS
        EDGPrice_a = MN_DICT['EDG'].EDGPrice_a
        EDGPrice_b = MN_DICT['EDG'].EDGPrice_b
        EDGPrice_c = MN_DICT['EDG'].EDGPrice_c
        EDG_UB = np.expand_dims(-MN_DICT['EDG'].EDG_UB, axis=1).repeat(self.T, axis=1)
        EDG_P = model.addVars(EDG_num, self.T, vtype=GRB.CONTINUOUS, lb=0, ub=EDG_UB, name='EDG')




        # LOAD_P = model.addVars(int(self.DistributionNetwork_num), self.T, vtype=GRB.CONTINUOUS, lb=self.distr_LO, ub=self.distr_UP*10, name='LOAD_P')
        # # LOAD_Q = model.addVars(int(self.DistributionNetwork_num), self.T, vtype=GRB.CONTINUOUS, name='LOAD_Q')
        #
        # Pi = model.addVars(int(self.BUS_num), self.T, lb=-1000000, ub=1000000, vtype=GRB.CONTINUOUS, name='Pi')
        # # Qi = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, name='Qi')
        # P_input = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, lb=-1000000, ub=1000000, name='P_input')
        # # Q_input = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, name='Q_input')
        # Us = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, lb=0, ub=self.Us_UB, name='Us')
        # phase = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, ub=360, name='phase')
        # cos = model.addVars(int(self.Branch_num)*2, self.T, vtype=GRB.CONTINUOUS, ub=1, name='cos')
        # sin = model.addVars(int(self.Branch_num)*2, self.T, vtype=GRB.CONTINUOUS, ub=1, name='sin')
        # delta = model.addVars(int(self.Branch_num)*2, self.T, vtype=GRB.CONTINUOUS, lb=-360, ub=360, name='delta')
        #
        #
        # for t in range(self.T):
        #     # 潮流约束
        #     model.addConstr(Us[0, t] == self.Us_UB, name='slack bus')
        #     model.addConstr(phase[0, t] == 0, name='slack bus')
        #
        #     for i in range(self.BUS_num):
        #         # 节点注入功率
        #         model.addConstr(P_input[i, t] == quicksum(EDG_P[k, t] for k in range(EDG_num) if EDG_BUS[k] == i) -
        #                             quicksum(LOAD_P[k, t] for k in range(self.DistributionNetwork_num) if self.DistributionNetwork_BUS[k] == i))
        #
        #         # 潮流约束
        #         js = np.where(i == self.Branch_BUS)
        #         Pi_ = 0
        #         # Qi_ = 0
        #         for k in js[0]:
        #             j = sum(self.Branch_BUS[k]) - i
        #             if i < j:
        #                 model.addConstr(delta[k, t] == phase[i, t]-phase[j, t])
        #                 model.addGenConstrCos(delta[k, t], cos[k, t])
        #                 model.addGenConstrSin(delta[k, t], sin[k, t])
        #                 Pi_ += Us[j, t] * (self.Branch_G[k]*cos[k, t] + self.Branch_B[k]*sin[k, t])
        #                 # Qi_ += Us[j, t] * (self.Branch_G[k]*sin[k, t] - self.Branch_B[k]*cos[k, t])
        #             else:
        #                 model.addConstr(delta[k+self.Branch_num, t] == phase[i, t] - phase[j, t])
        #                 model.addGenConstrCos(delta[k+self.Branch_num, t], cos[k+self.Branch_num, t])
        #                 model.addGenConstrSin(delta[k+self.Branch_num, t], sin[k+self.Branch_num, t])
        #                 Pi_ += Us[j, t] * (self.Branch_G[k] * cos[k+self.Branch_num, t] + self.Branch_B[k] * sin[k+self.Branch_num, t])
        #                 # Qi_ += Us[j, t] * (self.Branch_G[k] * sin[k+self.Branch_num, t] - self.Branch_B[k] * cos[k+self.Branch_num, t])
        #         model.addConstr(Pi[i, t] == Pi_)
        #         # model.addConstr(Qi[i, t] == Qi_)
        #         model.addConstr(P_input[i, t] == Us[i, t] * Pi[i, t], name='P_input')
        #         # model.addConstr(Q_input[i, t] == Us[i, t] * Qi[i, t], name='Q_input')
        #
        #
        # # 优化目标
        # model.setObjective(quicksum(EDGPrice_a[i]*EDG_P[i, t]**2 + EDGPrice_b[i]*EDG_P[i, t] + EDGPrice_c[i] for t in range(self.T) for i in range(EDG_num)), GRB.MINIMIZE)


        try:
            model.write('out.lp')
            model.setParam("OutputFlag", 0)
            model.setParam('Nonconvex', 2)
            model.setParam("MIPGap", 0)
            model.optimize()
            P = double_var(EDG_P, EDG_num, self.T)
        except:
            model.computeIIS()
            model.write('model.ilp')
            pass
