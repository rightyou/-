import numpy as np
# from pyomo.environ import *
from gurobipy import *
from gurobipy import Model
import math


class ES:
    def __init__(self, Dict, Data):
        self.id = Data.id
        self.BUS = int(Data.BUS)
        self.Pmax = Data.Pmax
        self.Pmin = Data.Pmin
        self.Emax = Data.Emax
        self.Emin = Data.Emin
        self.RUmax = Data.RUmax
        self.RDmax = Data.RDmax
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
        self.fi = None

    def para_cluster(self, paras):
        para = np.array([getattr(self, name) for name in paras])
        return para


class HPP(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class ESS(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class PSH(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class AC(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class IndustrialConsumer(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class DR(ES):
    def __init__(self, Dict, Data):
        super().__init__(Dict, Data)


class EV(ES):
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
        self.P_max = np.expand_dims(np.array([sum(m.Pmax for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_P_min = np.expand_dims(-np.eye(Dict['T']), 0).repeat(number, axis=0)
        self.P_min = np.expand_dims(-np.array([sum(m.Pmin for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_RU_max = np.expand_dims(np.eye(Dict['T']) - np.eye(Dict['T'], k=-1), 0).repeat(number, axis=0)
        self.RU_max = np.expand_dims(np.array([sum(m.RUmax for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_RD_max = np.expand_dims(-np.eye(Dict['T']) + np.eye(Dict['T'], k=-1), 0).repeat(number, axis=0)
        self.RD_max = np.expand_dims(-np.array([sum(m.RDmax for m in Dict['energy_storage'][bus][cluster_num])] * Dict['T']), 0).repeat(number, axis=0)
        self.matrix_E_max = np.array([m.matrix_E for m in Dict['energy_storage'][bus][cluster_num]])
        self.E_max = np.tile(np.array([m.Emax for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T'])
        self.matrix_E_min = -self.matrix_E_max
        self.E_min = -np.tile(np.array([m.Emin for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T'])
        self.constrained_integration__inner_approximation(Dict, bus, cluster_num)

        # 聚合资源成本函数 C = a*P**2 + b*P + c
        self.a = None
        self.b = None
        self.c = None
        self.capacity = None  # 日响应容量
        self.respond_rate_up = None  # 上调响应速度
        self.respond_rate_down = None  # 下调响应速率

    def constrained_integration__inner_approximation(self, Dict, bus, cluster_num):
        number = len(Dict['energy_storage'][bus][cluster_num])
        M = np.array([m.matrix_E for m in Dict['energy_storage'][bus][cluster_num]])
        # M = np.append(M, -M, axis=1)
        N = np.tile(np.array([m.Emax for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T'])
        # N = np.append(N, -np.tile(np.array([m.E_min for m in Dict['energy_storage'][bus][cluster_num]]).reshape([number, 1]), Dict['T']), axis=1)
        # 添加储能全天功率总和为0的约束
        # M = np.append(M, np.ones((number, 1, Dict['T'])), axis=1)
        # N = np.append(N, np.zeros((number, 1)), axis=1)

        # M = np.concatenate((self.matrix_P_max, self.matrix_P_min, self.matrix_RU_max, self.matrix_RD_max, self.matrix_E_max, self.matrix_E_min), axis=1)
        # N = np.concatenate((self.P_max, self.P_min, self.RU_max, self.RD_max, self.E_max, self.E_min), axis=1)

        M0 = np.mean(M, axis=0)
        N0 = np.array([np.mean(N, axis=0)])
        # gama = np.std(N, axis=0)
        # sigma = []
        fi = []

        for num in range(number):
            # # 内近似约束空间整合, 模型alpha总为零，需要进一步修改 ——《内近似约束空间整合的灵活性资源集群响应方法》
            # # model = ConcreteModel()
            # #
            # # def M0_initialize(model, i, j):
            # #     return M0[i, j]
            # # def N0_initialize(model, i):
            # #     return N0[i]
            # # def M_initialize(model, i, j):
            # #     return M[num, i, j]
            # # def N_initialize(model, i):
            # #     return N[num, i]
            # # model.T = Set(initialize=[i for i in range(Dict['T'])])
            # # model.U = Var(model.T, model.T, within=Reals, initialize=0, name='U')
            # # model.alpha = Var(within=Reals, initialize=0, name='alpha')
            # # model.beta = Var(model.T, within=Reals, initialize=0, name='beta')
            # # model.slackVariable = Var(model.T, within=NonNegativeReals, initialize=0)
            # # model.M0 = Param(model.T, model.T, initialize=M0_initialize)
            # # model.N0 = Param(model.T, initialize=N0_initialize)
            # # model.M = Param(model.T, model.T, initialize=M_initialize)
            # # model.N = Param(model.T, initialize=N_initialize)
            # #
            # # def c1(model, i, j):
            # #     return sum(model.U[i, k] * model.M0[k, j] for k in model.T) == model.M[i, j]
            # # def c2(model, i):
            # #     return sum(model.U[i, k] * model.N0[k] for k in model.T) + model.slackVariable[i] == model.N[i]*model.alpha + sum(model.M[i, k]*model.beta[k] for k in model.T)
            # # model.c1 = Constraint(model.T, model.T, rule=c1)
            # # model.c2 = Constraint(model.T, rule=c2)
            # #
            # # model.obj = Objective(expr=model.alpha, sense=minimize)
            # # model.write('model.lp')  # 输出模型文件
            # #
            # # opt = SolverFactory('gurobi')  # 指定求解器
            # # solution = opt.solve(model)  # 调用求解器求解
            # # solution.write()  # 输出结果
            # #
            # # sigma.append(1/value(model.alpha))
            # # fi.append(-value(model.beta[0]) / value(model.alpha))
            #
            # # U的约束应为Ui>0，但无解，所以将U改为自由变量
            # model = Model('CIIA')
            # U = model.addMVar((np.shape(M0)[0], np.shape(M0)[0]), lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='U')
            # alpha = model.addMVar((1,), vtype=GRB.CONTINUOUS, name='alpha')
            # beta = model.addMVar((np.shape(M0)[1],), lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='beta')
            # # slackVariable = model.addMVar((Dict['T']), vtype=GRB.CONTINUOUS, name='slackVariable')
            #
            # # model.addConstr(beta[0] == 0)
            # model.addConstr(U @ M0 == M[num])
            # # model.addConstr(U @ N0 + math.sqrt((1 - Dict['epsilon']) / Dict['epsilon']) * alpha * gama <= N[num] * alpha + M[num] @ beta)
            # model.addConstr(U @ N0 <= N[num] * alpha + M[num] @ beta)
            #
            # model.setObjective(alpha, GRB.MINIMIZE)
            # # model.write('out.lp')
            # model.setParam("OutputFlag", 0)
            # model.setParam('Nonconvex', 2)
            # model.setParam("MIPGap", 0)
            # model.optimize()
            #
            # # model.computeIIS()
            # # model.write('model.ilp')
            #
            # sigma.append(1 / single_var(alpha, 1))
            # fi.append(-single_var(beta, Dict['T']) / sigma[-1])
            # U_ = double_var(U, np.shape(M0)[0], np.shape(M0)[0])
            # np.all(np.linalg.eigvals(U_) > 0)
            #
            # for index in range(len(Dict['energy_storage'][bus][cluster_num])):
            #     Dict['energy_storage'][bus][cluster_num][index].sigma = sigma[-1]
            #     Dict['energy_storage'][bus][cluster_num][index].fi = fi[-1][index]

            model = Model('CIIA')
            dimension = np.shape(M0)[0]
            M_ = M[num]
            N_ = N[num]
            M0_inv = np.linalg.inv(M0)
            M_ = np.dot(M_, M0_inv)

            P = model.addMVar((dimension, dimension), vtype=GRB.CONTINUOUS, name='P')
            fi_ = model.addMVar(dimension, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='fi')
            C = model.addMVar((dimension, dimension), vtype=GRB.CONTINUOUS, name='C')
            C0 = model.addMVar((dimension, dimension), vtype=GRB.CONTINUOUS, name='C0')
            # multiplication_expression = model.addMVar(dimension, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='temp')
            temp = model.addMVar(dimension, vtype=GRB.CONTINUOUS, name='temp')
            Logarithmization = model.addMVar(dimension, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='Logarithmization')

            model.addConstr(C >= C0)
            model.addConstrs((C0[i, i:] == 0 for i in range(dimension)), name='顶点')
            for i in range(dimension):
                model.addConstr((P[i] - fi_) + C0[i] == N0, name='内近似矩阵')
                model.addConstr(M_ @ P[i] + C[i] == N_, name='原始矩阵')

            model.addConstr(temp == fi_ + N0[0], name='中间变量')
            for i in range(dimension):
                model.addGenConstrLog(temp[i], Logarithmization[i], name='log')
            # model.addConstrs((multiplication_expression[i] == (fi_[i] + N0[0, i])*multiplication_expression[i-1] for i in range(1, dimension)), name='中间变量')
            # multiplication_expression = LinExpr()
            # multiplication_expression += fi_[0] + N0[0, 0]
            # for i in range(1, dimension):
            #     multiplication_expression *= fi_[i] + N0[0, i]

            # model.setObjective(multiplication_expression[-1], GRB.MAXIMIZE)
            model.setObjective(quicksum(Logarithmization), GRB.MAXIMIZE)

            # model.write('out.lp')
            model.setParam("OutputFlag", 0)
            model.setParam('Nonconvex', 2)
            model.setParam("MIPGap", 0)
            model.optimize()

            # model.computeIIS()
            # model.write('model.ilp')

            fi.append(np.dot(M0_inv, single_var(fi_, Dict['T'])))

            for index in range(len(Dict['energy_storage'][bus][cluster_num])):
                Dict['energy_storage'][bus][cluster_num][index].fi = fi[-1][index]

        self.M0 = M0
        self.N0 = N0
        self.fi0 = np.sum(np.array(fi), 0)

    def adjustable_capability(self, Dict, bus, cluster_num):
        # 聚合资源成本函数 C = a*P**2 + b*P + c  ——《内近似约束空间整合的灵活性资源集群响应方法》
        a, b, c = 0, 0, 0
        fi = self.fi0
        for es in Dict['energy_storage'][bus][cluster_num]:
            a_i = es.a
            b_i = es.b
            c_i = es.c
            fi_i = es.fi
            a += a_i
            b += 2 * a_i * fi_i + b_i
            x = fi_i - fi
            c += a_i * x ** 2 + b_i * x + c_i
        self.a = np.array([a]*Dict['T'])
        self.b = b + a*fi
        self.c = c

        # 待修改。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。
        # 日响应容量
        self.capacity = sum(self.P_max)

        # 上调响应速度
        self.respond_rate_up = np.mean(self.RU_max)
        # 下调响应速率
        self.respond_rate_down = np.mean(self.RD_max)

        # 运行匹配率

        # 能源互补率

        # 固有建设成本

        # 单位调节成本

        # 建设周期


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
