# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 16:44:22 2023

@author: wuyuf
"""

from gurobipy import *
import numpy as np
from tupledictToarray import *
'''
     （1）功能解释：
     本函数旨在实现考虑柔性负荷可调能力上的切负荷优化决策
     （2）输入dict
     dict_['branch_num'] #支路个数
     dict_['branch_innode'] #支路输入节点
     dict_['branch_outnode'] #支路流出节点
     dict_['branch_r'] #支路电阻
     dict_['branch_x'] #支路电抗
     dict_['node_num'] #节点个数
     dict_['node_P'] #节点有功
     dict_['node_Q'] #节点无功
     dict_['break_branch'] #故障支路
     dict_['break_branch_num'] #故障支路数
     dict_['node_DP'] #可调空间
     dict_['node_DP'] #电源点
'''

# %% 构建切负荷转供问题
class DOPF_():
    
    def __init__(self,dict_):
        self.branch_num = dict_['branch_num']
        self.branch_innode = dict_['branch_innode']
        self.branch_outnode = dict_['branch_outnode']
        self.branch_r = dict_['branch_r']
        self.branch_x = dict_['branch_x']
        self.node_num = dict_['node_num']
        self.node_P = dict_['node_P']
        self.node_Q = dict_['node_Q']
        self.power_source = dict_['power_source']
        self.branch_Pmax = dict_['branch_Pmax']
        self.branch_Qmax = dict_['branch_Qmax']
        self.Uref = 1.05**2
        self.Us_UB = dict_['Umax']
        self.Us_LB = dict_['Umin']
# %%%% 构建模型求解
    def model_solve(self):
# %%%%%% 创建模型
        model = Model('DOPF_model')
# %%%%%% 创建节点出力变量
        Pg = model.addVars(self.node_num,vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'Pg')
        Qg = model.addVars(self.node_num,vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'Qg')
# %%%%%% 创建节点负荷变量
        PL = model.addVars(self.node_num,vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'Pg')
        QL = model.addVars(self.node_num,vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'Qg')
# %%%%%% 创建节点净负荷变量
        P = model.addVars(self.node_num,vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'P')
        Q = model.addVars(self.node_num,vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'Q')
# %%%%%% 创建节点电压变量 Us = U^2
        Us = model.addVars(self.node_num,vtype = GRB.CONTINUOUS, lb = 0,name='Us')
# %%%%%% 创建支路潮流变量
        BP = model.addVars(self.branch_num,vtype = GRB.CONTINUOUS,lb = -GRB.INFINITY, name = 'BP')
        BQ = model.addVars(self.branch_num,vtype = GRB.CONTINUOUS,lb = -GRB.INFINITY, name = 'BQ')
# %%%%%% 创建支路电流变量 Is = I^2
        Is = model.addVars(self.branch_num,vtype = GRB.CONTINUOUS, lb = 0,name='Is')
# %%%%%% 潮流约束(二阶锥转化)
# %%%%%%%% 创建节点负荷约束
        model.addConstrs((PL[n] - Pg[n] == P[n]  for n in range(self.node_num)),name = '节点净负荷有功约束')
        model.addConstrs((QL[n] - Qg[n] == Q[n]  for n in range(self.node_num)),name = '节点净负荷无功约束')
        model.addConstrs((Pg[n] == 0  for n in range(self.node_num) if n in self.power_source),name = '节点净负荷有功约束')
        model.addConstrs((Qg[n] == 0  for n in range(self.node_num) if n in self.power_source),name = '节点净负荷无功约束')
        model.addConstrs((self.node_P[n] == P[n]  for n in range(self.node_num) if n not in self.power_source),name = '节点有功约束')
        model.addConstrs((self.node_Q[n] == Q[n]  for n in range(self.node_num) if n not in self.power_source),name = '节点无功约束')
# %%%%%%%% 节点电压约束
        model.addConstrs( (0.0  == -Us[self.branch_outnode[i]] + Us[self.branch_innode[i]] - 2*(self.branch_r[i]*BP[i]+self.branch_x[i]*BQ[i])
                         + (self.branch_r[i]**2 + self.branch_x[i]**2)*Is[i]  for i in range(self.branch_num)), name='电压降等效式')
        model.addConstrs((Us[i] == self.Uref for i in self.power_source),name='固定电源节点电压')
        model.addConstrs((Us[i] <= self.Us_UB for i in range(self.node_num)),name='节点电压上限约束')
        model.addConstrs((Us[i] >= self.Us_LB for i in range(self.node_num)),name='节点电压下限约束')
# %%%%%%%% 功率平衡约束
        model.addConstrs((quicksum(BP[b] for b in range(self.branch_num) if self.branch_innode[b] == j) + P[j] == 
                          quicksum(BP[b] - self.branch_r[b]*Is[b] for b in range(self.branch_num) if self.branch_outnode[b] == j) 
                          for j in range(self.node_num)), name='有功等式约束')
        model.addConstrs((quicksum(BQ[b] for b in range(self.branch_num) if self.branch_innode[b] == j) + Q[j] == 
                          quicksum(BQ[b] - self.branch_x[b]*Is[b] for b in range(self.branch_num) if self.branch_outnode[b] == j) 
                          for j in range(self.node_num)), name='无功等式约束')
# %%%%%%%% 潮流上下限约束
        model.addConstrs(BP[i]<=self.branch_Pmax[i] for i in range(self.branch_num))
        model.addConstrs(BP[i]>=-self.branch_Pmax[i] for i in range(self.branch_num))
        model.addConstrs(BQ[i]<=self.branch_Qmax[i] for i in range(self.branch_num))
        model.addConstrs(BQ[i]>=-self.branch_Qmax[i] for i in range(self.branch_num))
# %%%%%% 额外约束
        model.addConstrs((4*BP[i]*BP[i] + 4*BQ[i]*BQ[i] + 
                         (Is[i]-Us[self.branch_innode[i]])*(Is[i]-Us[self.branch_innode[i]]) 
                         <= (Is[i] + Us[self.branch_innode[i]]) * (Is[i]+Us[self.branch_innode[i]])
                             for i in range(self.branch_num)),name = '电流约束')
# %%%%%% 设置目标函数
        model.setObjective(quicksum(0.1 * P[n]**2 for n in self.power_source), GRB.MINIMIZE)
        model.setParam('OutputFlag', 0)
        model.write('DOPF.lp')
        model.setParam("MIPGap", 0)
        model.setParam("QCPDual", 0)
        model.optimize()
        if model.status == GRB.OPTIMAL:
            # 便利所有的节点功率平衡等式约束
            # for con in model.getConstrs():
            #     if '有功等式约束' in con.ConstrName:
            #         print(con.ConstrName, '----', con.pi)
            # for con in model.getQConstrs():
            #     if '电流约束' in con.QCName:
            #         print(con.QCName, '----', con.qcpi)
            result_ = {}
            result_['obj_'] = model.getObjective().getValue()
            result_['P'] = single_var(P,self.node_num)
            result_['Q'] = single_var(Q,self.node_num)
            result_['P_branch'] = single_var(BP,self.branch_num)
            result_['Q_branch'] = single_var(BQ,self.branch_num)
            result_['Us'] = single_var(Us,self.node_num)
            result_['Is'] = single_var(Is,self.branch_num)
            return result_
        else:
            model.computeIIS()
            model.write('DOPF.ilp')
        
        
        