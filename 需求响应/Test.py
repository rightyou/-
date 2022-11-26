from matplotlib import pyplot as plt
import numpy as np
import networkx as nx

from procedure.data_process import *
from 需求响应.procedure.EVA import *
from 需求响应.procedure.ED import *
from 需求响应.procedure.Param import *
from 需求响应.procedure.DA import *
from 需求响应.procedure.PowerFlow import *
from 需求响应.procedure.EDG import *
from 需求响应.procedure.Road_network import *
from 需求响应.procedure.Car import *


if __name__ == '__main__':
    Param = Param()

    data_ = {
        'T': Param.T,
        'TT': Param.TT
    }
    data_ = read_PowerFlow_data(data_, 'data/PowerFlow.xlsx')
    data_ = read_Price_data(data_, 'data/Price.xlsx')
    data_ = read_EV_data(data_, 'data/EVA.xlsx')
    data_ = read_ED_data(data_, 'data/EDBase.xlsx')
    data_ = read_EDGub_data(data_, 'data/EDGub.xlsx')
    data_ = read_EDGlb_data(data_, 'data/EDGlb.xlsx')
    data_ = read_EDGPrice_data(data_, 'data/EDGPrice.xlsx')
    data_ = read_Road_data(data_, 'data/Road.xlsx')
    data_ = read_Taxi_data(data_, 'data/Taxi_example.xlsx')

    PowerFlow = PowerFlow(data_)
    EVA = EVA(data_)
    ED = ED(data_)
    EDG = EDG(data_)
    Road = Road(data_)
    Taxi = Taxi(data_)

    dict_ = {
        'Param': Param,
        'Price': data_['Price'],
        'PowerFlow': PowerFlow,
        'EVA': EVA,
        'ED': ED,
        'EDG': EDG,
        'Road': Road,
        'Taxi': Taxi,
    }

    for t in range(dict_['Param'].TT):
        Taxi.behavior(dict_, t)

    # DA_EVA = DA_EVA()
    # DA_EVA.SP(dict_)
    # dict_['EVA'].EV_distribution(dict_)


    # G = nx.Graph()
    # for node in range(1, 30):
    #     G.add_node(str(node))
    # for i in range(29):
    #     for j in range(i):
    #         if Road.road_network[i, j] != 0:
    #             G.add_edge(str(i + 1), str(j + 1), length=Road.road_network[i, j])
    # nx.draw(G, with_labels=True, node_color='y')
    # plt.show()


    # t = np.arange(0, 24, 1)
    # plt.figure()
    # for i in range(5):
    #     plt.subplot(2, 3, i+1)
    #     plt.title('NUM{}'.format(i+1))
    #     # plt.plot(t, EVA.EVA_ub[i], t, EVA.EVA_lb[i])
    #     plt.plot(t,EVA.EV_P[i])
    # plt.show()

    pass
