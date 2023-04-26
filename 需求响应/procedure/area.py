import numpy as np


class Area():
    def __init__(self, data_):
        '''
        area 道路节点
        BUS 电网节点
        '''
        self.area_BUS = dict(zip(data_['area'], data_['BUS']))
