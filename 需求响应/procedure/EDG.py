import numpy as np


class EDG():
    def __init__(self, data_):
        self.EDG_BUS = data_['EDG_BUS']
        self.EDG_ub = data_['EDG_ub']
        self.EDG_lb = data_['EDG_lb']
        self.EDGPrice = data_['EDGPrice']
