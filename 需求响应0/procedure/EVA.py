import numpy as np
import pandas as pd


class EVA():
    def __init__(self, dict_):
        self.EV_up = dict_['EV_up']
        self.EV_down = dict_['EV_down']
        self.EVA_up = self.EV_up.sum(0)
        self.EVA_down = dict_['EV_down'].sum(0)
        # self.EVA_ = np.zeros((1, 9))

    # def aggregator(self):
    #     self.EVA_up = self.EV_up.sum(0)
    #     self.EVA_down = self.EV_down.sum(0)




