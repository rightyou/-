import random

import 需求响应.procedure.data_process
import numpy as np


class Car():
    def __init__(self, data_):
        '''
        Car_C_max 电池容量
        Car_P 每公里耗电量
        Car_v 正常行驶速度
        Car_SOC_warn 电量预警SOC
        Car_SOC_baseline 电量SOC底线
        Car_P_charge 充电最大功率
        Car_area_start 初始位置
        Car_next 汽车将驶向的下一个节点以及进度
        Car_T_start 初始出行时刻
        Car_SOC_start初始SOC
        Car_area_T T时刻位置
        Car_SOC_T T时刻SOC
        Car_charge_flag 汽车接入充电桩
        '''
        # self.Car_type = data_['Car_type']
        self.Car_C_max = data_['Car_C_max']
        self.Car_P_charge = data_['Car_P_charge']
        self.Car_P = data_['Car_P']
        self.Car_v = data_['Car_v']
        self.Car_area_start = data_['Car_area_start']
        self.Car_next = np.zeros((len(self.Car_area_start), 2))
        self.Car_area_T = data_['Car_area_start']
        self.Car_T_start = data_['Car_T_start']
        self.Car_SOC_start = data_['Car_SOC_start']
        self.Car_SOC_T = data_['Car_SOC_start']
        self.Car_SOC_warn = data_['Car_SOC_warn']
        self.Car_SOC_baseline = data_['Car_SOC_baseline']
        self.Car_route = [[]for i in range(len(self.Car_area_start))]
        self.Car_charge_flag = np.zeros((len(self.Car_area_start)),dtype=bool)
        # self.Car_area_end = data_['Car_area_end']
        self.Car_T_end = data_['Car_T_end']
        self.Car_destination = np.zeros(self.Car_T_end.shape)  # 0代表没有目的地

    def destination_route_generate(self, dict_, i, t):
        # 更新全路段行车效率
        weight = {}
        for j in range(len(dict_['Road'].Road_network)):
            beta = dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][0] + \
                   dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][1] * (
                               dict_['Road'].Road_flow[j,t] / dict_['Road'].Road_capacity[j]) ** \
                   dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][2]
            x = tuple(dict_['Road'].Road_network[j])
            weight[x] = dict_['Road'].Road_length[j] / (
                        self.Car_v[i] / (1 + (dict_['Road'].Road_flow[j,t] / dict_['Road'].Road_capacity[j]) ** beta))

        # Dijkstra路径寻优
        routes = np.zeros((1,2))
        choice = {}
        for j in weight.copy():
            if self.Car_area_T[i] in j:
                choice[j] = weight.pop(j)
        while self.Car_destination[i] not in routes:
            for m in choice:
                if choice[m] == min(choice.values()):
                    routes = np.append(routes, np.array([m]), 0)
                    for j in weight.copy():
                        if m[0] in j or m[1] in j:
                            choice[j] = weight.pop(j) + choice[m]
                    cost = choice.pop(m)
                    break

        # 路径获取
        route = np.array([routes[-1]])
        while self.Car_area_T[i] not in route[0]:
            for m in routes:
                if route[0,0] in m or route[0,1] in m:
                    route = np.append(np.array([m]), route, 0)
                    break

        return route, cost

    def charge_route_generate(self, dict_, i, t):
        '''
        w1 充电电价权重
        w2 路线成本权重（包含耗电和时间成本）
        '''

        # for j in range(len(dict_['Road'].Road_network)):
            # if (self.Car_area_T[i] in dict_['Road'].Road_network[j]) and (self.Car_next[i, 0] in dict_['Road'].Road_network[j]):
            #     dict_['Road'].Road_charge[j, t] += 1

        cost, w1, w2 = float('inf'), 1, 2
        power = self.Car_C_max[i] * (0.9 - self.Car_SOC_T[i])
        for j in range(len(dict_['CS'].CS_BUS)):
            self.Car_destination[i] = dict_['CS'].CS_area[j]
            price = dict_['CS'].CS_Price[j, t//120]
            route_, r_cost_ = Taxi.destination_route_generate(self, dict_, i, t)
            cost_ = w1*price*power + w2*r_cost_
            if cost_ < cost:
                cost = cost_
                route = route_
                m = j
        self.Car_destination[i] = dict_['CS'].CS_area[m]
        return route

class Taxi(Car):
    '''
    behave 汽车行驶行为
    destination_generate 生成目的地
    destination_route_generate 目的地路径规划
    charge_route_generate 充电路径规划
    '''

    def __init__(self, data_):
        super().__init__(data_)

    def behavior(self, dict_, t):
        for i in range(len(self.Car_P)):
            if t//120 < self.Car_T_start[i]:
                continue

            if t//120 > self.Car_T_end[i] and self.Car_area_T[i] == self.Car_area_start[i]:
                continue

            if t//120 > self.Car_T_end[i] and self.Car_destination[i] == 0:
                self.Car_destination[i] = self.Car_area_start[i]
                self.Car_route[i], _ = Taxi.destination_route_generate(self, dict_, i, t)
                self.Car_next[i, 0] = np.sum(self.Car_route[i][0]) - self.Car_area_T[i]

            # 评估充电需求,充电站充电
            if self.Car_charge_flag[i]:
                self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
                if self.Car_SOC_T[i] >= 0.9:
                    self.Car_charge_flag[i] = False
                continue
            if self.Car_SOC_T[i] <= self.Car_SOC_warn[i]:
                if self.Car_area_T[i] in dict_['CS'].CS_area:
                    self.Car_charge_flag[i] = True
                    self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
                    continue

                # distance = 0
                # for n in self.Car_route[i]:
                #     for j in range(len(dict_['Road'].Road_network)):
                #         if n is dict_['Road'].Road_network[j]:
                #             distance += dict_['Road'].Road_length[j]
                # if self.Car_destination[i] == 0 or self.Car_SOC_T[i] - self.Car_P[i] * distance <= self.Car_SOC_baseline[i]:
                if self.Car_destination[i] == 0:
                    self.Car_route[i] = Taxi.charge_route_generate(self, dict_, i, t)
                    self.Car_next[i, 0] = np.sum(self.Car_route[i][0]) - self.Car_area_T[i]

            # 目的地选取
            if self.Car_destination[i] == 0:
                Taxi.destination_generate(self, dict_, i)
                self.Car_route[i],_ = Taxi.destination_route_generate(self, dict_, i, t)
                self.Car_next[i,0] = np.sum(self.Car_route[i][0]) - self.Car_area_T[i]

            # # 状态更新
            # self.Car_area_T[i] = ...
            for j in range(len(dict_['Road'].Road_network)):
                if (self.Car_area_T[i] in dict_['Road'].Road_network[j]) and (self.Car_next[i, 0] in dict_['Road'].Road_network[j]):
                    dict_['Road'].Road_flow[j, t] += 1
                    break
            for j in range(len(dict_['Road'].Road_network)):
                if (self.Car_area_T[i] in dict_['Road'].Road_network[j]) and (self.Car_next[i, 0] in dict_['Road'].Road_network[j]):
                    beta = dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][0] + \
                       dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][1] * (
                               dict_['Road'].Road_flow[j, t] / dict_['Road'].Road_capacity[j]) ** \
                       dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][2]
                    speed = self.Car_v[i] / (1 + (dict_['Road'].Road_flow[j,t] / dict_['Road'].Road_capacity[j]) ** beta)
                    self.Car_SOC_T[i] -= speed * self.Car_P[i]/self.Car_C_max[i]
                    for k in range(len(dict_['Road'].Road_network)):
                        if (self.Car_area_T[i] in dict_['Road'].Road_network[k]) and (self.Car_next[i, 0] in dict_['Road'].Road_network[k]):
                            self.Car_next[i,1] += speed*dict_['Param'].TT / dict_['Road'].Road_length[k]
                            break
                    break
            if self.Car_next[i,1] > 1:
                self.Car_area_T[i] = self.Car_next[i,0]
                self.Car_route[i] = np.delete(self.Car_route[i],0,0)
                if len(self.Car_route[i]) == 0:
                    self.Car_destination[i] = 0
                    continue
                self.Car_next[i,0] = np.sum(self.Car_route[i][0]) - self.Car_next[i,0]
                self.Car_next[i,1] = 0



    def destination_generate(self, dict_, i):
        while True:
            self.Car_destination[i] = random.randint(1, dict_['Road'].area_num)
            if self.Car_destination[i] != self.Car_area_T[i]:
                break




class PrivateCar(Car):
    '''
    behave 汽车行驶行为
    destination_route_generate 目的地路径规划
    charge_route_generate 充电路径规划
    '''

    def __init__(self, data_):
        super().__init__(data_)
        self.Car_area_end = data_['Car_area_end']

    def behavior(self, dict_, t):
        for i in range(len(self.Car_P)):

            if t//120 == self.Car_T_start[i]:
                self.Car_destination[i] = self.Car_area_end[i]
                self.Car_route[i], _ = Taxi.destination_route_generate(self, dict_, i, t)
            if t//120 == self.Car_T_end[i]:
                self.Car_destination[i] = self.Car_area_start[i]
                self.Car_route[i], _ = Taxi.destination_route_generate(self, dict_, i, t)

            # # 评估充电需求,充电站充电
            # if self.Car_charge_flag[i]:
            #     self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
            #     if self.Car_SOC_T[i] >= 0.9:
            #         self.Car_charge_flag[i] = False
            #     continue
            # if self.Car_SOC_T[i] <= self.Car_SOC_warn[i]:
            #     if self.Car_area_T[i] in dict_['CS'].CS_area:
            #         self.Car_charge_flag[i] = True
            #         self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
            #         continue
            #
            #     # distance = 0
            #     # for n in self.Car_route[i]:
            #     #     for j in range(len(dict_['Road'].Road_network)):
            #     #         if n is dict_['Road'].Road_network[j]:
            #     #             distance += dict_['Road'].Road_length[j]
            #     # if self.Car_destination[i] == 0 or self.Car_SOC_T[i] - self.Car_P[i] * distance <= self.Car_SOC_baseline[i]:
            #     if self.Car_destination[i] == 0:
            #         self.Car_route[i] = Taxi.charge_route_generate(self, dict_, i, t)
            #         self.Car_next[i, 0] = np.sum(self.Car_route[i][0]) - self.Car_area_T[i]

            # 状态更新
            if self.Car_destination[i] != 0:
                for j in range(len(dict_['Road'].Road_network)):
                    if (self.Car_area_T[i] in dict_['Road'].Road_network[j]) and (self.Car_next[i, 0] in dict_['Road'].Road_network[j]):
                        dict_['Road'].Road_flow[j, t] += 1
                        break
                for j in range(len(dict_['Road'].Road_network)):
                    if (self.Car_area_T[i] in dict_['Road'].Road_network[j]) and (self.Car_next[i, 0] in dict_['Road'].Road_network[j]):
                        beta = dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][0] + \
                           dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][1] * (
                                   dict_['Road'].Road_flow[j, t] / dict_['Road'].Road_capacity[j]) ** \
                           dict_['Road'].a_b_n[dict_['Road'].Road_grade[j] - 1][2]
                        speed = self.Car_v[i] / (1 + (dict_['Road'].Road_flow[j,t] / dict_['Road'].Road_capacity[j]) ** beta)
                        self.Car_SOC_T[i] -= speed * self.Car_P[i]/self.Car_C_max[i]
                        for k in range(len(dict_['Road'].Road_network)):
                            if (self.Car_area_T[i] in dict_['Road'].Road_network[k]) and (self.Car_next[i, 0] in dict_['Road'].Road_network[k]):
                                self.Car_next[i,1] += speed*dict_['Param'].TT / dict_['Road'].Road_length[k]
                                break
                        break
                if self.Car_next[i,1] > 1:
                    self.Car_area_T[i] = self.Car_next[i,0]
                    self.Car_route[i] = np.delete(self.Car_route[i],0,0)
                    if len(self.Car_route[i]) == 0:
                        self.Car_destination[i] = 0
                        continue
                    self.Car_next[i,0] = np.sum(self.Car_route[i][0]) - self.Car_next[i,0]
                    self.Car_next[i,1] = 0

            #  进入电动汽车需求相应充电模式
            else:
                pass
