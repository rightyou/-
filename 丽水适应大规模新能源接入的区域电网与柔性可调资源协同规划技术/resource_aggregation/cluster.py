import numpy as np
import pandas as pd
from sklearn.cluster import KMeans



def KmeansCluster(Dict):
    # Kmeans++方法，很蠢，聚类K取值越大，轮廓系数越优 ————《基于指标加权 K‐means++算法的分布式光伏功率波动平抑控制方法》
    clusters = {}
    for bus in range(Dict['BUS']):
        # 归一化处理
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
        X = (np.max(X, 0)-X)/(np.max(X, 0)-np.min(X, 0))

        # 轮廓系数
        S = {}
        for n_clusters in range(3, 10):
            cluster = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
            y_pred = cluster.labels_  # 获取训练后对象的每个样本的标签
            centtrod = cluster.cluster_centers_

            Si = []
            matrix = [np.array(X[y_pred == i]) for i in range(n_clusters)]
            for i in range(sum(num)):
                matrix_i = np.array(X.iloc[i, :])
                b = np.inf
                for j in range(n_clusters):
                    if j == y_pred[i]:
                        a = np.mean(np.sum(((matrix_i - matrix[j])**2), 1))
                    else:
                        k = np.mean(np.sum(((matrix_i - matrix[j])**2), 1))
                        if b > k: b = k
                Si.append((b - a) / max(b, a))
            S[n_clusters] = np.mean(Si)
        Dict['n_clusters'][bus] = max(S, key=lambda x: S[x])

        cluster = KMeans(n_clusters=Dict['n_clusters'][bus], random_state=0).fit(X)
        y_pred = cluster.labels_  # 获取训练后对象的每个样本的标签
        centtrod = cluster.cluster_centers_

        clusters[bus] = [[] for i in range(Dict['n_clusters'][bus])]
        n = 0
        for types in Dict['types_clusters']:
            for i in range(len(Dict[types][bus])):
                clusters[bus][y_pred[i+n]].append(Dict[types][bus][i])
            n += i

    return clusters



    pass
