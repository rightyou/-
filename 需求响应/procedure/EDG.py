import numpy as np


class EDG():
    def __init__(self, DATA):
        self.EDG_BUS = DATA['EDG_BUS']
        self.EDG_num = len(self.EDG_BUS)
        self.EDG_UB = DATA['EDG_UB']
        # self.EDG_lb = data_['EDG_lb']
        self.EDGPrice_a = DATA['EDGPrice_a']
        self.EDGPrice_b = DATA['EDGPrice_b']
        self.EDGPrice_c = DATA['EDGPrice_c']

