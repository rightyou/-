import numpy as np
# from pyomo.environ import *
from gurobipy import *
from gurobipy import Model
import math


class G:
    def __init__(self, Dict, Data):
        self.id = Data.id
        self.BUS = int(Data.BUS)
        self.P = np.array([Data['P{}'.format(i)] for i in range(Dict['T'])])
        self.Pmax = Data.Pmax
        self.Pmin = Data.Pmin
        self.RUmax = Data.RUmax
        self.RDmax = Data.RDmax
        self.eta = Data.eta
        self.matrix_P = np.eye(Dict['T'])
        self.matrix_R = np.eye(Dict['T']) - np.eye(Dict['T'], k=-1)
        # 成本函数 C = a*P**2 + b*P + c
        self.a = Data.a
        self.b = Data.b
        self.c = Data.c

    def para_cluster(self, paras):
        para = np.array([getattr(self, name) for name in paras])
        return para


class ROR(G):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class PV(G):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class DistributedPV(G):
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
        self.P_max = sum(m.Pmax for m in Dict['generate'][bus][cluster_num])
        self.matrix_P_min = -np.eye(Dict['T'])
        self.P_min = np.array([sum(m.Pmin for m in Dict['generate'][bus][cluster_num])] * Dict['T'])
        self.matrix_RU_max = np.eye(Dict['T']) - np.eye(Dict['T'], k=-1)
        self.RU_max = np.array([sum(m.RUmax for m in Dict['generate'][bus][cluster_num])] * Dict['T'])
        self.matrix_RD_max = -np.eye(Dict['T']) - np.eye(Dict['T'], k=-1)
        self.RD_max = -np.array([sum(m.RDmax for m in Dict['generate'][bus][cluster_num])] * Dict['T'])
        self.P = np.sum((m.P for m in Dict['generate'][bus][cluster_num]), 1)


        # 聚合资源成本函数 C = a*P**2 + b*P + c
        self.a = None
        self.b = None
        self.c = None
        self.capacity = None  # 日响应容量
        self.volatility = None  # 发电功率波动率
        self.operating_hours = None  # 设备利用率
        self.respond_rate_up = None  # 上调响应速度
        self.respond_rate_down = None  # 下调响应速率



    def adjustable_capability(self, Dict, bus, cluster_num):
        # 聚合资源成本函数 C = a*P**2 + b*P + c
        self.a = sum(g.a for g in Dict['generate'][bus][cluster_num])
        self.b = sum(g.b for g in Dict['generate'][bus][cluster_num])
        self.c = sum(g.c for g in Dict['generate'][bus][cluster_num])

        # 日响应容量
        self.capacity = np.sum(self.P)

        # 发电功率波动率
        self.volatility = np.var(self.P/np.max(self.P))

        # 设备利用小时数
        self.operating_hours = np.sum(self.P) / self.P_max / (Dict['T'] / 24)

        # 上调响应速度
        self.respond_rate_up = np.mean(self.RU_max)
        # 下调响应速率
        self.respond_rate_down = np.mean(self.RD_max)

        # 源荷匹配率
        ED = np.array(
            [250, 262.5, 275, 287.5, 300, 275, 250, 225, 200, 237.5, 275, 312.5, 350, 362.5, 375, 387.5, 400, 387.5, 375, 362.5, 350, 450, 550, 650, 750, 775, 800, 825, 850, 912.5, 975, 1037.5, 1100,
             1150, 1200, 1250, 1300, 1275, 1250, 1225, 1200, 1225, 1250, 1275, 1300, 1287.5, 1275, 1262.5, 1250, 1262.5, 1275, 1287.5, 1300, 1312.5, 1325, 1337.5, 1350, 1325, 1300, 1275, 1250, 1162.5,
             1075, 987.5, 900, 850, 800, 750, 700, 625, 550, 475, 400, 450, 500, 550, 600, 600, 600, 600, 600, 550, 500, 450, 400, 375, 350, 325, 300, 275, 250, 225, 200, 212.5, 225, 237.5
             ])
        self.source_load_match = 1/np.sqrt(np.sum((self.P/max(self.P) - ED/max(ED))**2))

        # 能源互补率
        total_G = np.sum(m.P for m in Dict['G__cluster'][self.BUS])
        except_G = total_G - self.P
        total_G = total_G / np.max(total_G)
        except_G = except_G / np.max(except_G)
        self.energy_complementary = (np.max(except_G)-np.min(except_G)) / (np.max(total_G)-np.min(total_G))

        # 固有建设成本
        self.inherent_cost = self.a * self.P_max

        # 单位调节成本
        self.adjust_cost = self.c

        # 建设周期
