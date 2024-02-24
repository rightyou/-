from pyomo.environ import *
import numpy as np

model = ConcreteModel()
model.I = Set(initialize = [i for i in range(4)])
model.J = Set(initialize = [i for i in range(4)])
model.x = Var(model.I, model.J, within = Reals, bounds = (0,1))
model.c = Param(model.I, model.J, initialize = {(1,1):2, (2,2):3}, default = 1)
def obj_rule(model):
    return summation(model.c, model.x)
def constrs_rule1(model, i):
    return sum([model.x[i,j] for j in model.J]) == 1
def constrs_rule2(model, j):
    return sum([model.x[i,j] for i in model.I]) == 1

model.obj = Objective(rule=obj_rule, sense = minimize)
model.constrs1 = Constraint(model.I, rule = constrs_rule1)
model.constrs2 = Constraint(model.J, rule = constrs_rule2)
model.dual = Suffix(direction=Suffix.IMPORT) # 对偶变量定义
opt = SolverFactory('gurobi') # 指定 gurobi 作为求解器
# opt = SolverFactory('cplex') # 指定 cplex 作为求解器
# opt = SolverFactory('scip') # 指定 scip 作为求解器
solution = opt.solve(model) # 调用求解器求解
solution.write() # 写入求解结果
x_opt = np.array([value(model.x[i,j]) for i in model.I for j in model.J]).reshape((len(model.I), len(model.J))) # 提取最优解
obj_values = value(model.obj) # 提取目标函数
print("optimum point: \n {} ".format(x_opt))
print("optimal objective: {}".format(obj_values))
for c in model.constrs1:
    print(model.dual[model.constrs1[c]]) #遍历约束constrs1的对偶变量



# model = Model('DC_OPF')
#
# # 变量
# '''
# EDG_ 发电机
# LOAD_ 负荷
# a,b,c 发电成本参数
# _UB 发电功率上界
# phase 节点电压相角
# P_input 节点注入功率
# P_Branch 支路有功
# '''
# EDG_num = MN_DICT['EDG'].EDG_num
# EDG_BUS = MN_DICT['EDG'].EDG_BUS
# EDGPrice_a = MN_DICT['EDG'].EDGPrice_a
# EDGPrice_b = MN_DICT['EDG'].EDGPrice_b
# EDGPrice_c = MN_DICT['EDG'].EDGPrice_c
# EDG_UB = np.expand_dims(MN_DICT['EDG'].EDG_UB, axis=1).repeat(self.T, axis=1)
# EDG_P = model.addVars(EDG_num, self.T, vtype=GRB.CONTINUOUS, lb=EDG_UB, ub=0, name='EDG_P')
#
# LOAD_P = model.addVars(int(self.DistributionNetwork_num), self.T, vtype=GRB.CONTINUOUS, lb=self.distr_LO, ub=self.distr_UP, name='LOAD_P')
#
# phase = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, lb=-360, ub=360, name='phase')
# P_input = model.addVars(int(self.BUS_num), self.T, vtype=GRB.CONTINUOUS, lb=-1000000, ub=1000000, name='P_input')
# P_Branch = model.addVars(int(self.Branch_num), self.T, vtype=GRB.CONTINUOUS, lb=-1000000, ub=1000000, name='P_Branch')
#
# # 约束
# for t in range(self.T):
#     model.addConstr(phase[0, t] == 0, name='slack bus')
#
#     # model.addConstr(quicksum(P_input[i, t] for i in range(self.BUS_num)) == 0, name='power balance')
#
#     for i in range(self.BUS_num):
#         # 节点注入功率
#         model.addConstr(P_input[i, t] == quicksum(EDG_P[k, t] for k in range(EDG_num) if EDG_BUS[k] == i) +
#                         quicksum(LOAD_P[k, t] for k in range(self.DistributionNetwork_num) if self.DistributionNetwork_BUS[k] == i),
#                         name='input_P')
#
#         model.addConstr(P_input[i, t] == quicksum(
#             P_Branch[k, t] if self.Branch_BUS[k, 0] == i else -P_Branch[k, t] for k in range(self.Branch_num) if i in self.Branch_BUS[k]))
#
#     # 直流潮流约束
#     for index, [i, j] in enumerate(self.Branch_BUS):
#         model.addConstr(P_Branch[index, t] == (phase[i, t] - phase[j, t]) * self.Branch_B[i, j], name='Branch_P')
#
# # 优化目标
# model.setObjective(
#     quicksum(EDGPrice_a[i] * EDG_P[i, t] ** 2 + EDGPrice_b[i] * EDG_P[i, t] + EDGPrice_c[i] for t in range(self.T) for i in range(EDG_num)), GRB.MINIMIZE)
#
# try:
#     model.write('out.lp')
#     model.setParam("OutputFlag", 0)
#     model.setParam('Nonconvex', 2)
#     model.setParam("MIPGap", 0)
#     model.optimize()
#     self.EDG_P = double_var(EDG_P, EDG_num, self.T)
#     self.DistributionNetwork_P = double_var(LOAD_P, int(self.DistributionNetwork_num), self.T)
# except:
#     model.computeIIS()
#     model.write('model.ilp')
#     pass