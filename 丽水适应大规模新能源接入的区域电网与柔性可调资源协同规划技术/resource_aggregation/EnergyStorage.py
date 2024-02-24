import numpy as np
# from pyomo.environ import *
from gurobipy import *
from gurobipy import Model
import math


class ES:
    def __init__(self, Dict, Data):
        self.id = Data.id
        self.BUS = int(Data.BUS)
        self.P_max = Data.Pmax
        self.P_min = Data.Pmin
        self.E_max = Data.Emax
        self.E_min = Data.Emin
        self.RU_max = Data.RUmax
        self.RD_max = Data.RDmax
        self.eta = Data.eta
        self.Lambda = Data.Lambda
        self.matrix_P = np.eye(Dict['T'])
        self.matrix_R = np.eye(Dict['T']) - np.eye(Dict['T'], k=-1)
        matrix_E = np.eye(Dict['T'])
        for i in range(1, Dict['T']):
            matrix_E = matrix_E + np.eye(Dict['T'], k=-i) * (Data.Lambda ** i)
        self.matrix_E = matrix_E * np.tril(np.ones((Dict['T'], Dict['T'])) * Data.eta)
        # 成本函数 C = a*P**2 + b*P + c
        self.a = Data.a
        self.b = Data.b
        self.c = Data.c
        self.sigma = None
        self.fi = None

    def para_cluster(self):
        para = np.array([self.eta, self.Lambda])
        return para


class ESS(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class PumpedStorage(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class ES__Cluster:
    def __init__(self, Dict, bus, cluster_num):
        # Dict['epsilon'] = 0.1
        self.BUS = bus

        #  约束空间的闵可夫斯基和
        #  matrix * (P - fi) < sigma * constr
        number = len(Dict['energy_storage'][bus][cluster_num])
        self.matrix_P_max = np.expand_dims(np.eye(Dict['T']), 0).repeat(number, axis=0)
        self.P_max = np.expand_dims(np.array([sum(m.P_max for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_P_min = np.expand_dims(-np.eye(Dict['T']), 0).repeat(number, axis=0)
        self.P_min = np.expand_dims(-np.array([sum(m.P_min for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_RU_max = np.expand_dims(np.eye(Dict['T']) - np.eye(Dict['T'], k=-1), 0).repeat(number, axis=0)
        self.RU_max = np.expand_dims(np.array([sum(m.RU_max for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_RD_max = np.expand_dims(-np.eye(Dict['T']) + np.eye(Dict['T'], k=-1), 0).repeat(number, axis=0)
        self.RD_max = np.expand_dims(-np.array([sum(m.RD_max for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_E_max = np.array([m.matrix_E for m in Dict['energy_storage'][bus][cluster_num]])
        self.E_max = np.tile(np.array([m.E_max for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T'])
        self.matrix_E_min = -self.matrix_E_max
        self.E_min = -np.tile(np.array([m.E_min for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T'])
        self.constrained_integration__inner_approximation(Dict, bus, cluster_num)

        # 聚合资源成本函数 C = a*P**2 + b*P + c
        self.a = None
        self.b = None
        self.c = None
        self.capacity = None  # 日响应容量
        self.respond_rate_up = None  # 上调响应速度
        self.respond_rate_down = None  # 下调响应速率



    def constrained_integration__inner_approximation(self, Dict, bus, cluster_num):
        # 内近似约束空间整合, 模型alpha总为零，需要进一步修改 ——《内近似约束空间整合的灵活性资源集群响应方法》
        number = len(Dict['energy_storage'][bus][cluster_num])
        M = np.array([m.matrix_E for m in Dict['energy_storage'][bus][cluster_num]])
        # M = np.append(M, -M, axis=1)
        N = np.tile(np.array([m.E_max for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T'])
        # N = np.append(N, -np.tile(np.array([m.E_min for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T']), axis=1)
        # 添加储能全天功率总和为0的约束
        # M = np.append(M, np.ones((number, 1, Dict['T'])), axis=1)
        # N = np.append(N, np.zeros((number, 1)), axis=1)

        # M = np.concatenate((self.matrix_P_max, self.matrix_P_min, self.matrix_RU_max, self.matrix_RD_max, self.matrix_E_max, self.matrix_E_min), axis=1)
        # N = np.concatenate((self.P_max, self.P_min, self.RU_max, self.RD_max, self.E_max, self.E_min), axis=1)

        M0 = np.mean(M, axis=0)
        N0 = np.mean(N, axis=0)
        # gama = np.std(N, axis=0)
        sigma = []
        fi = []

        for num in range(number):
            # model = ConcreteModel()
            #
            # def M0_initialize(model, i, j):
            #     return M0[i, j]
            # def N0_initialize(model, i):
            #     return N0[i]
            # def M_initialize(model, i, j):
            #     return M[num, i, j]
            # def N_initialize(model, i):
            #     return N[num, i]
            # model.T = Set(initialize=[i for i in range(Dict['T'])])
            # model.U = Var(model.T, model.T, within=Reals, initialize=0, name='U')
            # model.alpha = Var(within=Reals, initialize=0, name='alpha')
            # model.beta = Var(model.T, within=Reals, initialize=0, name='beta')
            # model.slackVariable = Var(model.T, within=NonNegativeReals, initialize=0)
            # model.M0 = Param(model.T, model.T, initialize=M0_initialize)
            # model.N0 = Param(model.T, initialize=N0_initialize)
            # model.M = Param(model.T, model.T, initialize=M_initialize)
            # model.N = Param(model.T, initialize=N_initialize)
            #
            # def c1(model, i, j):
            #     return sum(model.U[i, k] * model.M0[k, j] for k in model.T) == model.M[i, j]
            # def c2(model, i):
            #     return sum(model.U[i, k] * model.N0[k] for k in model.T) + model.slackVariable[i] == model.N[i]*model.alpha + sum(model.M[i, k]*model.beta[k] for k in model.T)
            # model.c1 = Constraint(model.T, model.T, rule=c1)
            # model.c2 = Constraint(model.T, rule=c2)
            #
            # model.obj = Objective(expr=model.alpha, sense=minimize)
            # model.write('model.lp')  # 输出模型文件
            #
            # opt = SolverFactory('gurobi')  # 指定求解器
            # solution = opt.solve(model)  # 调用求解器求解
            # solution.write()  # 输出结果
            #
            # sigma.append(1/value(model.alpha))
            # fi.append(-value(model.beta[0]) / value(model.alpha))

            model = Model('CIIA')
            U = model.addMVar((np.shape(M0)[0], np.shape(M0)[0]), vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name='U')
            alpha = model.addMVar((1,), vtype=GRB.CONTINUOUS, name='alpha')
            beta = model.addMVar((np.shape(M0)[1],), vtype=GRB.CONTINUOUS, name='beta')
            # slackVariable = model.addMVar((Dict['T']), vtype=GRB.CONTINUOUS, name='slackVariable')

            model.addConstr(beta[0] == 0)
            model.addConstr(U @ M0 == M[num])
            # model.addConstr(U @ N0 + math.sqrt((1 - Dict['epsilon']) / Dict['epsilon']) * alpha * gama <= N[num] * alpha + M[num] @ beta)
            model.addConstr(U @ N0 <= N[num] * alpha + M[num] @ beta)

            model.setObjective(alpha, GRB.MINIMIZE)
            # model.write('out.lp')
            model.setParam("OutputFlag", 0)
            model.setParam('Nonconvex', 2)
            model.setParam("MIPGap", 0)
            model.optimize()

            # model.computeIIS()
            # model.write('model.ilp')


            sigma.append(1/single_var(alpha, 1))
            fi.append(-single_var(beta, Dict['T']) / sigma[-1])
            U_ = double_var(U, np.shape(M0)[0], np.shape(M0)[0])
            np.all(np.linalg.eigvals(U_) > 0)

            for index in range(len(Dict['energy_storage'][bus][cluster_num])):
                Dict['energy_storage'][bus][cluster_num][index].sigma = sigma[-1]
                Dict['energy_storage'][bus][cluster_num][index].fi = fi[-1][index]

            pass


        self.M0_E = M0
        self.N0_E = N0
        self.sigma_E = sum(sigma)
        self.fi_E = sum(fi)



    def adjustable_capability(self, Dict, bus, cluster_num):
        # 聚合资源成本函数 C = a*P**2 + b*P + c  ——《内近似约束空间整合的灵活性资源集群响应方法》
        a, b, c = 0, 0, 0
        sigma, fi = self.sigma_E, self.fi_E
        fi_sigma = fi/sigma
        for es in Dict['energy_storage'][bus][cluster_num]:
            a_i = es.a
            b_i = es.b
            c_i = es.c
            sigma_i = es.sigma
            fi_i = es.fi
            a += a_i * sigma_i**2
            b += sigma_i * (2*a_i*(fi_i - sigma_i*fi_sigma) + b_i)
            x = fi_i - sigma_i*fi_sigma
            c += a_i*x**2 + b_i*x + c_i
        self.a = a / sigma**2
        self.b = b / sigma
        self.c = c

# 待修改。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。
        # 日响应容量
        self.capacity = sum(self.P_max)

        # 上调响应速度
        self.respond_rate_up = np.mean(self.RU_max)
        # 下调响应速率
        self.respond_rate_down = np.mean(self.RD_max)




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





