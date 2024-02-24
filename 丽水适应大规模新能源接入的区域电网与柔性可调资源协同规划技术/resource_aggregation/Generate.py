import numpy as np
# from pyomo.environ import *
from gurobipy import *
from gurobipy import Model
import math


class G:
    def __init__(self, Dict, Data):
        self.id = Data.id
        self.BUS = int(Data.BUS)
        self.P_max = np.array([Data['P{}'.format(i)] for i in range(Dict['T'])])
        self.P_min = Data.Pmin
        self.RU_max = Data.RUmax
        self.RD_max = Data.RDmax
        self.eta = Data.eta
        self.matrix_P = np.eye(Dict['T'])
        self.matrix_R = np.eye(Dict['T']) - np.eye(Dict['T'], k=-1)
        # 成本函数 C = a*P**2 + b*P + c
        self.a = Data.a
        self.b = Data.b
        self.c = Data.c

    def para_cluster(self):
        para = np.array([self.eta])
        return para


class Hydroelectric(G):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class PV(G):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class ThermalPower(G):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class WP(G):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)



class G__Cluster:
    def __init__(self, Dict, bus, cluster_num):
        self.BUS = bus

        #  约束空间的闵可夫斯基和
        self.matrix_P_max = np.eye(Dict['T'])
        self.P_max = sum(m.P_max for m in Dict['generate'][bus][cluster_num])
        self.matrix_P_min = -np.eye(Dict['T'])
        self.P_min = np.array([sum(m.P_min for m in Dict['generate'][bus][cluster_num])] * Dict['T'])
        self.matrix_RU_max = np.eye(Dict['T']) - np.eye(Dict['T'], k=-1)
        self.RU_max = np.array([sum(m.RU_max for m in Dict['generate'][bus][cluster_num])] * Dict['T'])
        self.matrix_RD_max = -np.eye(Dict['T']) - np.eye(Dict['T'], k=-1)
        self.RD_max = -np.array([sum(m.RD_max for m in Dict['generate'][bus][cluster_num])] * Dict['T'])


        # 聚合资源成本函数 C = a*P**2 + b*P + c
        self.a = None
        self.b = None
        self.c = None
        self.operating_factor = None  # 日响应容量
        self.volatility = None  # 发电功率波动率
        self.capacity = None  # 设备利用率
        self.respond_rate_up = None  # 上调响应速度
        self.respond_rate_down = None  # 下调响应速率



    def adjustable_capability(self, Dict, bus, cluster_num):
        # 聚合资源成本函数 C = a*P**2 + b*P + c
        self.a = sum(g.a for g in Dict['generate'][bus][cluster_num])
        self.b = sum(g.b for g in Dict['generate'][bus][cluster_num])
        self.c = sum(g.c for g in Dict['generate'][bus][cluster_num])

        # 日响应容量
        self.capacity = sum(self.P_max)

        # 发电功率波动率
        self.volatility = np.var(self.P_max)

        # 设备利用率
        self.operating_factor = np.mean(self.P_max) / np.max(self.P_max)

        # 上调响应速度
        self.respond_rate_up = np.mean(self.RU_max)
        # 下调响应速率
        self.respond_rate_down = np.mean(self.RD_max)

        # 与各场景基础负荷的匹配度


