from .MajorNetwork import *
from .data_process import *
from .Param import *
from .EDG import *



def dispatch(DN_LIST, ):
    param = Param()

    DATA = read_PowerFlow_data(param, 'data/MajorNetwork/PowerFlow.xlsx')
    DATA = read_DistributionNetwork_data(DATA, 'data/MajorNetwork/DistributionNetwork.xlsx')
    major = MAJOR(DN_LIST, DATA, param)
    DATA = read_EDG_data(param, 'data/MajorNetwork/EDG.xlsx')
    edg = EDG(DATA)

    DICT = {
        'Param': param,
        'MAJOR': major,
        'EDG': edg,
    }



    major.DC_OPF(DICT)



    return DICT