import numpy as np


class ED():
    def __init__(self, data_):
        self.ED_BUS = data_['ED_BUS']
        self.EDBase = data_['EDBase']
        self.ED_num = len(self.ED_BUS)
        self.ED_avg = np.mean(self.EDBase)
