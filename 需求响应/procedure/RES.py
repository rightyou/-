import numpy as np
from ιζ±εεΊ0.procedure.Param import *

class RES():
    def __init__(self, dict_):
        self.RES_up = dict_['RES_up'].sum(0)
        # self.RES_ = np.zeros((1, 96))
