import numpy as np
import pandas as pd
from sklearn.cluster import KMeans



def KmeansCluster(Dict):
    clusters = {bus: [[] for i in range(Dict['n_clusters'])] for bus in range(Dict['BUS'])}
    for bus in range(Dict['BUS']):
        num = [len(Dict[types][bus]) for types in Dict['types_clusters']]
        flag = 0
        for types in Dict['types_clusters']:
            X_ = np.zeros([len(Dict[types][bus]), len(Dict['para_clusters'])])
            for i in range(len(Dict[types][bus])):
                X_[i] = Dict[types][bus][i].para_cluster()
            if flag == 0:
                X = X_
                flag = 1
                continue
            X = np.append(X, X_, axis=0)

        X = pd.DataFrame(X)
        cluster = KMeans(n_clusters=Dict['n_clusters'], random_state=0).fit(X)
        y_pred = cluster.labels_  # 获取训练后对象的每个样本的标签
        centtrod = cluster.cluster_centers_

        n = 0
        for types in Dict['types_clusters']:
            for i in range(len(Dict[types][bus])):
                clusters[bus][y_pred[i+n]].append(Dict[types][bus][i])
            n += i

    return clusters



    pass
