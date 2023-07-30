import numpy as np


class ED():
    def __init__(self, DATA):
        self.ED_BUS = DATA['ED_BUS']
        self.EDBase = DATA['EDBase']
        self.ED_num = len(self.ED_BUS)
        self.ED_avg = np.mean(self.EDBase)
