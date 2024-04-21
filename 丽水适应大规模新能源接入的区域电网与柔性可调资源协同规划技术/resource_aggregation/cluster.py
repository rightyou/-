import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN




def KmeansCluster(Dict):
    # Kmeans++方法，很蠢，聚类K取值越大，轮廓系数越优 ————《基于指标加权 K‐means++算法的分布式光伏功率波动平抑控制方法》
    # 将轮廓系数更换为DB指数进行计算,聚类K取值越小越优。。。
    # DBSCAN密度聚类算法
    clusters = {}
    for bus in range(Dict['BUS']):
        # 归一化处理
        num = [len(Dict[types][bus]) for types in Dict['types_clusters']]
        flag = 0
        for types in Dict['types_clusters']:
            X_ = np.zeros([len(Dict[types][bus]), len(Dict['para_clusters'])])
            for i in range(len(Dict[types][bus])):
                X_[i] = Dict[types][bus][i].para_cluster(Dict['para_clusters'])
            if flag == 0:
                X = X_
                flag = 1
                continue
            X = np.append(X, X_, axis=0)
        X = pd.DataFrame(X)
        X = (np.max(X, 0)-X)/(np.max(X, 0)-np.min(X, 0))
        X = np.nan_to_num(X)

        # # 轮廓系数
        # S = {}
        # for n_clusters in range(3, 10):
        #     cluster = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
        #     y_pred = cluster.labels_  # 获取训练后对象的每个样本的标签
        #     centtrod = cluster.cluster_centers_
        #
        #     Si = []
        #     matrix = [np.array(X[y_pred == i]) for i in range(n_clusters)]
        #     for i in range(sum(num)):
        #         matrix_i = np.array(X.iloc[i, :])
        #         inter_dist = np.inf
        #         for j in range(n_clusters):
        #             if j == y_pred[i]:
        #                 intra_dist = np.mean(np.sum(((matrix_i - matrix[j])**2), 1))
        #             else:
        #                 temporary = np.mean(np.sum(((matrix_i - matrix[j])**2), 1))
        #                 if inter_dist > temporary:
        #                     inter_dist = temporary
        #         Si.append((inter_dist - intra_dist) / max(inter_dist, intra_dist))
        #     S[n_clusters] = np.mean(Si)
        # Dict['n_clusters'][bus] = max(S, key=lambda x: S[x])

        # # DB指数
        # DBI = {}
        # for n_clusters in range(3, 10):
        #     cluster = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
        #     y_pred = cluster.labels_  # 获取训练后对象的每个样本的标签
        #     centtrod = cluster.cluster_centers_
        #
        #     intra_dist = {}
        #     matrix = [np.array(X[y_pred == i]) for i in range(n_clusters)]
        #     for i in range(len(matrix)):
        #         temp = 0
        #         for j in range(len(matrix[i])):
        #             temp += np.sum(np.sum(((matrix[i][j] - matrix[i]) ** 2), 1))
        #         intra_dist[i] = 2 * temp / len(matrix[i]) / (len(matrix[i]) - 1)
        #     dist = 0
        #     for i in range(n_clusters):
        #         for j in range(i+1, n_clusters):
        #             tempo = (intra_dist[i] + intra_dist[j]) / np.sum(((centtrod[i] - centtrod[j]) ** 2))
        #             if tempo > dist:
        #                 dist = tempo
        #     DBI[n_clusters] = dist / n_clusters
        # Dict['n_clusters'][bus] = max(DBI, key=lambda x: DBI[x])


        # cluster = KMeans(n_clusters=Dict['n_clusters'][bus], random_state=0).fit(X)
        # y_pred = cluster.labels_  # 获取训练后对象的每个样本的标签
        # centtrod = cluster.cluster_centers_

        # 创建DBSCAN对象，设置半径和最小样本数
        dbscan = DBSCAN(eps=0.3, min_samples=1)

        # 进行聚类
        y_pred = dbscan.fit_predict(X)

        Dict['n_clusters'][bus] = np.max(y_pred)+1

        clusters[bus] = [[] for i in range(Dict['n_clusters'][bus])]
        n = 0
        for types in Dict['types_clusters']:
            for i in range(len(Dict[types][bus])):
                clusters[bus][y_pred[i+n]].append(Dict[types][bus][i])
            n += i + 1

    return clusters



    pass
