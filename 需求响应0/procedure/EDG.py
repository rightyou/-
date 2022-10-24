import numpy as np


class EDG():
    def __init__(self, dict_):
        self.EDG_up = dict_['EDG_up']
        self.EDG_down = dict_['EDG_down']
        self.EDGPrice = dict_['EDGPrice']
        # self.EDG_ = np.zeros((1, 9))
