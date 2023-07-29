import numpy as np


class RES():
    def __init__(self, DATA):
        self.RES_BUS = DATA['RES_BUS']
        self.RES_num = len(self.RES_BUS)
        self.P_RES = DATA['P_RES']
