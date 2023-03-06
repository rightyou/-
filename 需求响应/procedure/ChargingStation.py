import numpy as np


class CS():
    def __init__(self, data_):
        '''
        CS_BUS 充电站母线节点
        CS_area 充电站道路节点
        CS_charging_pile_num 充电站内可用充电桩数量
        CS_Price 充电站电价信息
        '''
        self.CS_BUS = data_['CS_BUS']
        self.CS_num = len(self.CS_BUS)
        self.CS_area = data_['CS_area']
        self.CS_charging_pile_num = data_['CS_charging_pile_num']
        self.CS_Price = data_['CS_Price']
