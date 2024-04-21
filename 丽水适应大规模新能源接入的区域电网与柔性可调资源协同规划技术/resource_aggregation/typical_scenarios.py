import numpy as np
from sklearn.cluster import DBSCAN



class TypicalScenario:
    def __init__(self, Dict):
        self.type = None
        self.para = None
        self.para_weight = None
        self.classify = {}
        self.utility = {}
        self.eps = None



    def utility_classify(self, DICT):
        classify = {}
        utility = {}
        for bus in range(DICT['BUS']):
            value = []
            for type in self.type:
                for cluster in DICT[type][bus]:
                    temp = np.array([m.para_cluster(self.para) for m in cluster])
                    value.append(np.mean(temp, 0))
            value = np.array(value)
            value = np.sum(value / np.max(value, 0) * self.para_weight, 1)
            value = np.array([value])

            # 创建DBSCAN对象，设置半径和最小样本数
            dbscan = DBSCAN(eps=self.eps, min_samples=1)
            # 进行聚类
            y_pred = dbscan.fit_predict(value.T)

            classify[bus] = y_pred
            utility[bus] = value
        self.classify = classify
        self.utility = utility


class Conflict_PV_HPP(TypicalScenario):
    def __init__(self):
        super(Conflict_PV_HPP, self).__init__(self)
        self.eps = 0.05
        self.type = ['energy_storage', 'generate']
        self.para = ['eta', 'Pmin', 'RUmax', 'RDmax']
        self.para_weight = np.array([1, 10, 3, 3])


class Summer(TypicalScenario):
    def __init__(self):
        super(Summer, self).__init__(self)
        self.eps = 0.5
        self.type = ['energy_storage']
        self.para = ['eta', 'Pmin', 'RUmax', 'RDmax', 'Emax']
        self.para_weight = np.array([1, 7, 1, 5, 10])

