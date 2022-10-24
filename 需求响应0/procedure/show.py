from gurobipy import *
import numpy as np


def single_var(x, w):
    d = np.zeros(w, dtype=float)
    for i in range(w):
        d[i] = x[i].getAttr("x")

    return d


def double_var(x, u, v):
    d = np.zeros((u, v), dtype=float)
    for i in range(u):
        for j in range(v):
            d[i, j] = x[i, j].getAttr("x")

    return d
