# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 17:29:05 2022

@author: wuyuf
"""

import numpy as np

# %% 函数功能及输入输出
'''
     （1）功能解释：
     本函数旨在将gurobi求解的一维tupledict转化为array
     （2）输入
     w-变量，
     x-维度
     （3）输出
     d-array数组
'''

def single_var(x, w):
    d = np.zeros(w, dtype=float)
    for i in range(w):
        d[i] = x[i].getAttr("x")
        
    return d

def double_var(x, w, v):
    d = np.zeros((w, v), dtype=float)
    for i in range(w):
        for j in range(v):
            d[i, j] = x[i, j].getAttr("x")
    return d