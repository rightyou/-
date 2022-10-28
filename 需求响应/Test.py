from matplotlib import pyplot as plt
import numpy as np
from procedure.data_process import *
from 需求响应.procedure.EVA import *
from 需求响应.procedure.ED import *
from 需求响应.procedure.Param import *
from 需求响应.procedure.DA import *
from 需求响应.procedure.PowerFlow import *
from 需求响应.procedure.EDG import *


if __name__ == '__main__':
    Param = Param()

    data_ = {
        'T': Param.T,
    }
    data_ = read_PowerFlow_data(data_, 'data/PowerFlow.xlsx')
    data_ = read_Price_data(data_, 'data/Price.xlsx')
    data_ = read_EV_data(data_, 'data/EVA.xlsx')
    data_ = read_ED_data(data_, 'data/EDBase.xlsx')
    data_ = read_EDGub_data(data_, 'data/EDGub.xlsx')
    data_ = read_EDGlb_data(data_, 'data/EDGlb.xlsx')
    data_ = read_EDGPrice_data(data_, 'data/EDGPrice.xlsx')

    PowerFlow = PowerFlow(data_)
    EVA = EVA(data_)
    ED = ED(data_)
    EDG = EDG(data_)

    dict_ = {
        'Param': Param,
        'Price': data_['Price'],
        'PowerFlow': PowerFlow,
        'EVA': EVA,
        'ED': ED,
        'EDG': EDG,
    }

    DA_EVA = DA_EVA()
    DA_EVA.SP(dict_)
    dict_['EVA'].EV_distribution(dict_)


    t = np.arange(0, 24, 1)
    plt.figure()
    for i in range(5):
        plt.subplot(2, 3, i+1)
        plt.title('BUS{}'.format(i+1))
        # plt.plot(t, EVA.EVA_ub[i], t, EVA.EVA_lb[i])
        plt.plot(t,EVA.EV_P[i])
    plt.show()
    pass
