import numpy as np
import pandas as pd
from EVA import *


def data_create():
    dict_ = {}
    dict_['EV_down'] = pd.read_excel('data/1.xlsx',header=0,index_col=0).values
    dict_['EV_up'] = pd.read_excel('data/2.xlsx', header=0, index_col=0).values
    return dict_


if __name__ == '__main__':
    dict_ = data_create()
    EVA = EVA(dict_)
    EVA_DOWN_UP = EVA.aggregator()
    pass
