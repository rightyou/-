# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 16:35:06 2023

@author: wuyuf
"""

# %% 导入库

from pymoo.core.problem import Problem
import numpy as np
from pymoo.algorithms.moo.spea2 import SPEA2
from pymoo.factory import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
import matplotlib.pyplot as plt
import time
import pandas as pd

# %% 引入外部多目标函数
import SimpleCase as SC

# %% 导入自定义问题类
class MyProblem(Problem):
# %%%% 初始化问题参数
    def __init__(self,dict_):
        super().__init__(n_var=dict_['node_num']*dict_['time'], 
                         n_obj=dict_['n_obj'], 
                         n_constr=0, 
                         xl=np.array([dict_['Price_lb']]*(dict_['node_num']*dict_['time'])), 
                         xu=np.array([dict_['Price_ub']]*(dict_['node_num']*dict_['time'])))
# %%%% 列写评估函数
    def _evaluate(self, X, out, *args, **kwargs):
        # global mark
        # montecarlos = []
        # for i in range(len(X)):
        #     # 电动汽车运行场景生成
        #     montecarlo, eva = EVA_SG.montecarlo('data/DistributionNetwork', X[i].reshape(dict_['node_num'],dict_['time']))
        #     montecarlos.append(montecarlo)
        # mark = 0
        # f1 = np.apply_along_axis(func1, 1, X, )
        # mark = 0
        # f2 = np.apply_along_axis(func2, 1, X, )
        # out["F"] = np.column_stack([f1, f2])


        F = np.apply_along_axis(SC.func1, 1, X)
        out["F"] = F



# %% 测试程序
if __name__ == '__main__':
    start = time.time()
    SC.result_i = 0
    SC.result_P = np.zeros((5,96,8))
    SC.result_Us = np.zeros((5, 96, 8))
    SC.result_variance = np.zeros((5))

# %%%% 明确输入
    dict_ = {}
# %%%%%% 节点数量
    dict_['node_num'] = 9
# %%%%%% 时间窗口
    dict_['time'] = 96
# %%%%%% 目标数量    
    dict_['n_obj'] = 2
# %%%%%% 价格上下限
    dict_['Price_lb'] = 0.68
    dict_['Price_ub'] = 1.5
# %%%%%% 导入自定义问题
    problem = MyProblem(dict_)
# %%%%%% 调用SPEA2算法（pop_size为种群数量）
    algorithm = SPEA2(pop_size=5)
# %%%%% 创建回调函数
    callback = lambda algorithm: print(f"Generation: {algorithm.n_gen}, Best Fitness: {algorithm.opt.get('F')}")
# %%%%%% 执行优化（ngen为迭代次数）
    res = minimize(problem,
                   algorithm,
                   ('n_gen', 5),
                   seed=1,
                   verbose=False,
                   callback = callback)

    end = time.time()
    print(end-start)
# %%%%%% 绘制结果
#     plot = Scatter()
#     plot.add(problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
#     plot.add(res.F, color="red")
#     plot.show()


    plt.figure()
    plt.scatter(res.F[:,0],res.F[:,1])
    plt.show()

    Optimal_price_num = int(np.argmin((res.F / np.max(res.F, axis=0)).sum(1)))
    # Optimal_P_num = int(np.argwhere(SC.result_variance==res.F[Optimal_price_num, 0]))

    plt.figure()
    plt.plot(SC.result_P[Optimal_price_num].sum(1) * 2 * 1000)
    plt.show()

    plt.figure()
    plt.plot(SC.result_Us[Optimal_price_num]*10)
    plt.show()

    Optimal_price = res.X[Optimal_price_num,:].reshape(dict_['node_num'],dict_['time'])
    with pd.ExcelWriter('price1.xlsx') as writer:
        df = pd.DataFrame(Optimal_price)
        df.to_excel(writer, sheet_name='Sheet1', index=None)

    with pd.ExcelWriter('P1.xlsx') as writer:
        df = pd.DataFrame(SC.result_P[Optimal_price_num] * 2 * 1000)
        df.to_excel(writer, sheet_name='Sheet1', index=None)

    with pd.ExcelWriter('Us1.xlsx') as writer:
        df = pd.DataFrame(SC.result_Us[Optimal_price_num]*10)
        df.to_excel(writer, sheet_name='Sheet1', index=None)


    pass