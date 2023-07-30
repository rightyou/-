import numpy as np
import pandas as pd
import math


class PowerFlow():
    def __init__(self,data_):
        self.BUS_num = max(np.ravel(data_['Branch_BUS']))+1  # 节点从0开始
        self.Branch_BUS = data_['Branch_BUS']
        self.Branch_R = data_['Branch_R']
        self.Branch_X = data_['Branch_X']
        self.Branch_B = data_['Branch_B']
        self.Branch_num = len(self.Branch_B)
