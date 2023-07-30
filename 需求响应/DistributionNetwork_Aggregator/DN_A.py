from .DistributionNetwork import *
from .Param import *
from .data_process import *
from .RES import *
from .PowerFlow import *
from .ED import *



def aggregate(path, montecarlo):
    param = Param()

    DATA = read_PowerFlow_data(param, '{}/PowerFlow.xlsx'.format(path))
    powerflow = PowerFlow(DATA)
    DATA = read_ED_data(param, '{}/EDBase.xlsx'.format(path))
    ed = ED(DATA)
    DATA = read_RES_data(param, '{}/RES.xlsx'.format(path))
    res = RES(DATA)

    DICT = {
        'Param': param,
        'PowerFlow': powerflow,
        'ED': ed,
        'RES': res,
    }

    # 配电网可调能力边界聚合模型
    distr = DISTR(montecarlo)
    distr.AdjustableBoundaryAggregation(DICT)
    DICT['DISTR'] = distr

    return DICT