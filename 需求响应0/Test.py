from matplotlib import pyplot as plt
from 需求响应0.procedure.DA_SP import *
from 需求响应0.procedure.DemandResponse import *
from 需求响应0.procedure.ED import *
from 需求响应0.procedure.EDG import *
from 需求响应0.procedure.EVA import *
from 需求响应0.procedure.RES import *





def data_read():
    dict_ = {'EV_up': pd.read_excel('data/EV_up.xlsx', header=0, index_col=0).values,
             'EV_down': pd.read_excel(io=r'data/EV_down.xlsx', header=0, index_col=0).values,
             'EDG_up': pd.read_excel(io=r'data/EDG_up.xlsx', header=0, index_col=0).values,
             'EDG_down': pd.read_excel(io=r'data/EDG_down.xlsx', header=0, index_col=0).values,
             'EDGPrice': pd.read_excel(io=r'data/EDGPrice.xlsx', header=0, index_col=0).values,
             'SPrice': pd.read_excel(io=r'data/SPrice.xlsx', header=0, index_col=0).values,
             'BPrice': pd.read_excel(io=r'data/BPrice.xlsx', header=0, index_col=0).values,
             'RES_up': pd.read_excel(io=r'data/RES_up.xlsx', header=0, index_col=0).values,
             'EDBase': pd.read_excel(io=r'data/EDBase.xlsx', header=0, index_col=0).values
             }
    return dict_


if __name__ == '__main__':
    dict_ = data_read()

    EVA = EVA(dict_)
    EDG = EDG(dict_)
    DR = DR(dict_)
    RES = RES(dict_)
    ED = ED(dict_)

    # dict_ = DA_initial()

    dict_ = {
        'T': 24,
        'scenario_num': 1,
        'P': 1,
        'EVA_up': EVA.EVA_up,
        'EVA_down': EVA.EVA_down,
        'EDG_up': EDG.EDG_up,
        'EDG_down': EDG.EDG_down,
        'EDGPrice': EDG.EDGPrice,
        'EDBase': ED.EDBase,
        'RES_up': RES.RES_up,
        'SPrice': DR.SPrice,
        'BPrice': DR.BPrice
    }

    DA_SP = DA_SP(dict_)
    DA_SP.Solve(dict_)

    plt.figure()
    plt.subplot(2, 3, 1)
    plt.plot(DA_SP.EDG)
    plt.title('EDG')
    plt.subplot(2, 3, 2)
    plt.plot(DA_SP.EVA[0])
    plt.title('EVA')
    plt.subplot(2, 3, 3)
    plt.plot(DA_SP.RES[0])
    plt.title('RES')
    plt.subplot(2, 3, 4)
    plt.plot(DA_SP.EBFG)
    plt.title('EBFG')
    plt.subplot(2, 3, 5)
    plt.plot(DA_SP.ESTG)
    plt.title('ESTG')
    plt.show()

    # print(dict_)
    pass
