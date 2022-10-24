from matplotlib import pyplot as plt
import numpy as np
from procedure.data_process import *
from 需求响应.procedure.EVA import *
from 需求响应.procedure.Param import *


if __name__ == '__main__':
    Param = Param()

    dict_ = {
        'T': Param.T,
    }
    dict_ = read_EV_data(dict_, 'data/EVA.xlsx')




    EVA = EVA(dict_)

    t = np.arange(1, 25, 1)
    plt.figure()
    for i in range(4):
        plt.subplot(2, 2, i+1)
        plt.title('BUS{}'.format(i+1))
        plt.plot(t, EVA.EVA_up[i], t, EVA.EVA_down[i])
    plt.show()
    pass
