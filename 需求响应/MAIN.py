from EVA_SecneGeneration import *
from DistributionNetwork_Aggregator import *
from MajorNetwork_Dispatch import *



if __name__ == '__main__':
    DN_LIST = []

    for i in range(3):
        montecarlo = EVA_SG.montecarlo('data/DistributionNetwork{}'.format(i + 1))
        dn = DN_A.aggregate('data/DistributionNetwork{}'.format(i + 1), montecarlo)
        DN_LIST.append(dn)


    MN_DICT = MN_D.dispatch(DN_LIST)


    for i in range(MN_DICT['MAJOR'].DistributionNetwork_num):
        DN_LIST[i]['DISTR'].DistributionNetwork_DA(DN_LIST[i], MN_DICT['MAJOR'].DistributionNetwork_P[i])



    pass

