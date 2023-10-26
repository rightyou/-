# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 16:55:06 2023

@author: wuyuf
"""

# %% 导入库
import numpy as np
import pandas as pd
from gurobipy import *
import DOPF
from tupledictToarray import *
from EVA_SecneGeneration import *

global result_P
global result_Us
global result_i
global result_variance

'''
此代码为构建启发式算法的适应度计算过程
包括：
（1）电价对负荷的影响，
        如Calculation类中的Load函数所示，后续需要子然进行更新，
        输入为电价和基础负荷、网架信息，输出为节点负荷
（2）计算最优潮流下的台区的平衡情况，
        由Calculation类中的DOPF_Cycle函数和func1、func2组成
        需要特别关注fun1、2中的参数设置
        其中fun1、2输入为电价，输出为不同节点、不同时间的台区电压、负荷大小的方差。
'''
# %% 定义问题
class Calculation():
# %%%% 初始化问题输入
    def __init__(self,dict_):
        self.dict_DOPF = {}
        self.dict_DOPF['branch_num'] = dict_['branch_num']
        self.dict_DOPF['branch_innode'] = dict_['branch_innode']
        self.dict_DOPF['branch_outnode'] = dict_['branch_outnode']
        self.dict_DOPF['branch_r'] = dict_['branch_r']
        self.dict_DOPF['branch_x'] = dict_['branch_x']
        self.dict_DOPF['node_num'] = dict_['node_num']
        self.dict_DOPF['power_source'] = dict_['power_source']
        self.dict_DOPF['branch_Pmax'] = dict_['branch_Pmax']
        self.dict_DOPF['branch_Qmax'] = dict_['branch_Qmax']
        self.dict_DOPF['Uref'] = dict_['Uref']
        self.dict_DOPF['Umax'] = dict_['Umax']
        self.dict_DOPF['Umin'] = dict_['Umin']
        self.dict_DOPF['Load'] = dict_['Load']
        self.dict_DOPF['Price'] = dict_['Price']
        self.dict_DOPF['time'] = dict_['time']
# %%%% 负荷变化生成，此处定义为每个用户有能力调整负荷，子然后续要把这个换成出行模拟的程序
    def Load(self):
        # 电动汽车运行场景生成
        montecarlo, eva = EVA_SG.montecarlo('data/DistributionNetwork', self.dict_DOPF['Price'])

        EVA_num = montecarlo['EVA_num']
        EVA_BUS = montecarlo['EVA_BUS']
        EVA_lb = montecarlo['EVA_lb'][:,:96]
        EVA_ub = montecarlo['EVA_ub'][:,:96]
        EVA_P_dischar_max = montecarlo['EVA_P_dischar_max'][:,:96]
        EVA_P_char_max = montecarlo['EVA_P_char_max'][:,:96]
        EVA_C_out = montecarlo['EVA_C_out'][:,:96]


# %%%%%% 创建模型
        model = Model('Load_change')
# %%%%%% 创建节点负荷变量
        P = model.addVars(self.dict_DOPF['node_num'],self.dict_DOPF['time'],vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'P')
        Q = model.addVars(self.dict_DOPF['node_num'],self.dict_DOPF['time'],vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY, name = 'Q')
        EVA_P = model.addVars(EVA_num, self.dict_DOPF['time'], vtype=GRB.CONTINUOUS, lb=EVA_P_dischar_max, ub=EVA_P_char_max, name='EVA_P')

# %%%%%% 创建节点调整约束
        model.addConstrs((P[n,t] <= 100*self.dict_DOPF['Load'][n][t]
                         for n in range(self.dict_DOPF['node_num'])
                         for t in range(self.dict_DOPF['time']) if self.dict_DOPF['Load'][n][t]>=0),name='可调上界约束')
        model.addConstrs((P[n,t] >= 0.1*self.dict_DOPF['Load'][n][t] if self.dict_DOPF['Load'][n][t]>=0 else P[n,t] >= 5*self.dict_DOPF['Load'][n][t]
                         for n in range(self.dict_DOPF['node_num'])
                         for t in range(self.dict_DOPF['time'])),name='可调下界约束')
        # model.addConstrs((quicksum(P[n,t] for t in range(self.dict_DOPF['time'])) ==
        #                  quicksum(self.dict_DOPF['Load'][n][t] for t in range(self.dict_DOPF['time']))
        #                  for n in range(self.dict_DOPF['node_num'])),name='总负荷守恒约束')
        model.addConstrs((0.32868*P[n,t] == Q[n,t] 
                         for n in range(self.dict_DOPF['node_num']) 
                         for t in range(self.dict_DOPF['time'])),name='功率因素约束')

        # 电动汽车集合充电功率曲线约束
        for i in range(EVA_num):
            model.addConstrs((quicksum(EVA_P[i, k] - EVA_C_out[i, k] for k in range(t)) <= EVA_ub[i, t] for t in range(self.dict_DOPF['time'])), name='EVA_C_max')  # 电动汽车当天累计充电电量减去汽车离开时的所冲电量落在充电功率曲线中
            model.addConstrs((quicksum(EVA_P[i, k] - EVA_C_out[i, k] for k in range(t)) >= EVA_lb[i, t] for t in range(self.dict_DOPF['time'])), name='EVA_C_min')
        # 节点注入功率
        model.addConstrs((P[n, t] == self.dict_DOPF['Load'][n][t] +
                          quicksum(EVA_P[i, t] for i in range(EVA_num) if EVA_BUS[i] == n)
                          for n in range(1, self.dict_DOPF['node_num'])
                          for t in range(self.dict_DOPF['time'])), name='P_input')  # 节点0与上层电网相连接

        # %%%%%% 定义目标函数
        model.setObjective(quicksum(self.dict_DOPF['Price'][n][t] * P[n,t] 
                                    for n in range(self.dict_DOPF['node_num']) 
                                    for t in range(self.dict_DOPF['time'])), GRB.MINIMIZE)
        try:
            model.setParam('OutputFlag', 0)
            model.write('Load_change.lp')
            model.optimize()
            model.setParam("MIPGap", 0)
            result_ = {}
            result_['obj_'] = model.getObjective().getValue()
            result_['P'] = double_var(P,self.dict_DOPF['node_num'],self.dict_DOPF['time'])
            result_['Q'] = double_var(Q,self.dict_DOPF['node_num'],self.dict_DOPF['time'])
            # model.setParam("QCPDual", 1)
        except:
            model.computeIIS()
            model.write('model.ilp')
            pass
        return result_
# %%%% 设计调用DOPF程序进行循环计算
    def DOPF_Cycle(self,result):
        Us = []
        P = []
        for t in range(self.dict_DOPF['time']):
            # print(t)
            dict_DOPF_ = self.dict_DOPF
            dict_DOPF_['node_P'] = result['P'][:,t]
            dict_DOPF_['node_Q'] = result['Q'][:,t]
            DOPF_ = DOPF.DOPF_(dict_DOPF_)
            # print(dict_DOPF_['node_P'])
            # print(dict_DOPF_['node_P'].sum())
            result_DOPF = DOPF_.model_solve()
            # print(result_DOPF['P_branch'])
            Us.append([result_DOPF['Us'][i] for i in range(len(result_DOPF['Us'])) if i not in self.dict_DOPF['power_source']])
            P.append([result_DOPF['P'][i] for i in range(len(result_DOPF['P'])) if i not in self.dict_DOPF['power_source']])
        return Us,P
# %%%% 目标函数1
def func1(x):
    global result_P
    global result_Us
    global result_i
    global result_variance
    '''
    这一部分的参数是需要动态去更新的，照例应该是放置在函数外部，但是由于其中需要作为其他算法的调用，无法直接写出去，暂时定为手写更新
    其中需要关注下面主要需要调整的参数
    '''
# %%%% 主要需要调整的参数
    dict_ = {}
    # path_topu = 'data/Test.xlsx'
    path_topu = 'data/DistributionNetwork/PowerFlow.xlsx'
    path_load = 'data/DistributionNetwork/EDBase.xlsx'
    dict_['time'] = 96 # 调控时间窗口
# %%%% 标幺化参数设置
    V_base = 10# kV 33:12.66/ 94:11.40
    S_base = 2  # MVA 33:5.68/ 94:5.68
    R_base = V_base**2 / S_base
# %%%% 构建联络线路的拓扑信息
    branch = pd.read_excel(path_topu,header=0,index_col=None).values
    dict_['branch_num'] = len(branch) # 线路数量
    dict_['branch_innode'] = (branch[:,0]).astype(np.int) # 注入节点
    dict_['branch_outnode'] = (branch[:,1]).astype(np.int) # 流出节点
    dict_['branch_r'] = branch[:,2] / R_base /20 # 支路电阻，不能设置太大
    dict_['branch_x'] = branch[:,3] / R_base /20 # 支路电抗，不能设置太大
    dict_['branch_Pmax'] = 100*np.ones(dict_['branch_num']) # 线路有功容量
    dict_['branch_Qmax'] = 100*np.ones(dict_['branch_num']) # 线路无功容量
# %%%% 构建节点负荷信息
    load = pd.read_excel(path_load,header=0,index_col=0).values[:,1:97] # 节点负荷信息
    dict_['node_num'] = len(load) # 节点数量
    dict_['Load'] = load / S_base / 1000 # 节点负荷标幺值
    dict_['power_source'] = np.arange(1).astype(int) # 电源节点
    dict_['Uref'] = 1.05**2 # 电源节点电压
    dict_['Umax'] = 1.05**2 # 节点电压上限
    dict_['Umin'] = 0.8**2 # 节点电压下限（松弛）
    x = x.reshape(dict_['node_num'],dict_['time'])
    dict_['Price'] = x # 依于变量设置电价
# %%%% 计算特定电价下的节点负荷变化
    CA = Calculation(dict_)
    result = CA.Load()
# %%%% 计算非供电节点台区电压的不平衡度
    Us,P = CA.DOPF_Cycle(result)
    Us = np.array(Us)
    variance1 = np.var(Us)
    P = abs(np.array(P))
    variance2 = np.var(P)

    result_P[result_i] = P
    result_Us[result_i] = Us
    result_variance[result_i] = variance1
    result_i = (result_i+1)%5

    return variance1, variance2
# %%%% 目标函数2
def func2(x):
    '''
    这一部分的参数是需要动态去更新的，照例应该是放置在函数外部，但是由于其中需要作为其他算法的调用，无法直接写出去，暂时定为手写更新
    其中需要关注下面主要需要调整的参数
    '''
# %%%% 主要需要调整的参数
    dict_ = {}
    # path_topu = 'data/Test.xlsx'
    path_topu = 'data/DistributionNetwork/PowerFlow.xlsx'
    path_load = 'data/DistributionNetwork/EDBase.xlsx'
    dict_['time'] = 96 # 调控时间窗口
# %%%% 标幺化参数设置
    V_base = 10# kV 33:12.66/ 94:11.40
    S_base = 2  # MVA 33:5.68/ 94:5.68
    R_base = V_base**2 / S_base
# %%%% 构建联络线路的拓扑信息
    branch = pd.read_excel(path_topu,header=0,index_col=None).values
    dict_['branch_num'] = len(branch) # 线路数量
    dict_['branch_innode'] = (branch[:,0]).astype(np.int) # 注入节点
    dict_['branch_outnode'] = (branch[:,1]).astype(np.int) # 流出节点
    dict_['branch_r'] = branch[:,2] / R_base /30 # 支路电阻，不能设置太大
    dict_['branch_x'] = branch[:,3] / R_base /30 # 支路电抗，不能设置太大
    dict_['branch_Pmax'] = 10.3*np.ones(dict_['branch_num']) # 线路有功容量
    dict_['branch_Qmax'] = 10.3*np.ones(dict_['branch_num']) # 线路无功容量
# %%%% 构建节点负荷信息
    load = pd.read_excel(path_load,header=0,index_col=0).values[:,1:97] # 节点负荷信息
    dict_['node_num'] = len(load) # 节点数量
    dict_['Load'] = load / S_base / 1000 # 节点负荷标幺值
    dict_['power_source'] = np.arange(1).astype(int) # 电源节点
    dict_['Uref'] = 1.05**2 # 电源节点电压
    dict_['Umax'] = 1.05**2 # 节点电压上限
    dict_['Umin'] = 0.8**2 # 节点电压下限（松弛）
    x = x.reshape(dict_['node_num'],dict_['time'])
    dict_['Price'] = x # 依于变量设置电价
# %%%% 计算特定电价下的节点负荷变化
    CA = Calculation(dict_)
    result = CA.Load()
# %%%% 计算非供电节点台区功率的不平衡度
    Us,P = CA.DOPF_Cycle(result)
    P = abs(np.array(P))
    variance = np.var(P)
    return variance

# %% 测试程序
if __name__ == '__main__':
   pass


