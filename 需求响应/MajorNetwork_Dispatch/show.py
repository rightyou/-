from gurobipy import *
import numpy as np


# 将gurobi求解的一维tupledict转化为array
def single_var(x, w):
    d = np.zeros(w, dtype=float)
    for i in range(w):
        d[i] = x[i].getAttr("x")

    return d


# 将gurobi求解的二维tupledict转化为array
def double_var(x, u, v):
    d = np.zeros((u, v), dtype=float)
    for i in range(u):
        for j in range(v):
            d[i, j] = x[i, j].getAttr("x")

    return d
