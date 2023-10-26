import numpy as np


class Area():
    def __init__(self, DATA):
        '''
        area 道路节点
        BUS 电网节点
        '''
        self.area_BUS = dict(zip(DATA['area'], DATA['BUS']))
        self.destination_probability = DATA['destination_probability']
