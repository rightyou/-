import random

import numpy as np


class Car():
    def __init__(self, DATA):
        '''
        Car_C_max 电池容量
        Car_P 每公里耗电量
        Car_v 正常行驶速度
        Car_SOC_warn 电量预警SOC
        Car_P_charge 充电最大功率
        Car_area_start 初始位置
        Car_next 汽车将驶向的下一个节点的进度
        Car_T_start 初始出行时刻
        Car_SOC_start初始SOC
        Car_SOC_end充电完成SOC
        Car_area_T T时刻位置
        Car_SOC_T T时刻SOC
        Car_charge_flag 汽车接入充电桩
        Car_P_charge_lambda 汽车充电效率
        '''
        # self.Car_type = DATA['Car_type']
        self.Car_C_max = DATA['Car_C_max']
        self.Car_num = len(self.Car_C_max)
        self.Car_P_charge = DATA['Car_P_charge']
        self.Car_P_discharge = DATA['Car_P_discharge']
        self.Car_P = DATA['Car_P']
        self.Car_v = DATA['Car_v']
        self.Car_area_start = DATA['Car_area_start']
        self.Car_next = np.zeros(self.Car_num)
        self.Car_area_T = DATA['Car_area_start'].copy()
        self.Car_road_T = np.zeros(self.Car_num, dtype=int)
        self.Car_T_start = DATA['Car_T_start']
        self.Car_SOC_start = DATA['Car_SOC_start']
        self.Car_SOC_end = DATA['Car_SOC_end']
        self.Car_SOC_T = DATA['Car_SOC_start'].copy()
        self.Car_SOC_warn = DATA['Car_SOC_warn']
        self.Car_route = [[]for i in range(self.Car_num)]
        self.Car_charge_flag = np.zeros(self.Car_num,dtype=bool)
        self.Car_P_charge_lambda = DATA['P_charge_lambda']
        # self.Car_area_end = DATA['Car_area_end']
        self.Car_T_end = DATA['Car_T_end']
        self.Car_destination = np.zeros(self.Car_T_end.shape)  # 0代表没有目的地

    def destination_route_generate(self, DICT, i, t, weight):


        # Dijkstra路径寻优
        S = np.array((self.Car_area_T[i]))
        r = DICT['Road'].Road_network
        r_num = DICT['Road'].Road_num
        choice = {}
        for j in range(r_num):
            if self.Car_area_T[i] in r[j]:
                choice[tuple(r[j])] = DICT['Road'].Road_length[j] / (self.Car_v[i] / weight[tuple(r[j])])
        m = min(choice, key=choice.get)
        if m[0] in S:
            area_from = m[0]
            area_to = m[1]
        else:
            area_from = m[1]
            area_to = m[0]
        routes = {}
        while True:
            if area_to in S:
                choice.pop(m)
                m = min(choice, key=choice.get)
                if m[0] in S:
                    area_from = m[0]
                    area_to = m[1]
                else:
                    area_from = m[1]
                    area_to = m[0]
                continue
            routes[area_to] = area_from
            if self.Car_destination[i] == area_to:
                cost = choice[m]
                break
            for j in range(r_num):
                if area_to in r[j]:
                    choice[tuple(r[j])] = DICT['Road'].Road_length[j] / (self.Car_v[i] / weight[tuple(r[j])])
            S = np.append(area_to, S)
            choice.pop(m)
            m = min(choice, key=choice.get)
            if m[0] in S:
                area_from = m[0]
                area_to = m[1]
            else:
                area_from = m[1]
                area_to = m[0]

        # 路径获取
        r_ = np.array((min(area_from, area_to), max(area_from, area_to)))
        route = np.where((r == r_).all(1))[0]
        while area_from != self.Car_area_T[i]:
            area_to = area_from
            area_from = routes[area_to]
            r_ = np.array((min(area_from, area_to), max(area_from, area_to)))
            route = np.append(np.where((r == r_).all(1))[0], route, 0)


        return route, cost

    def charge_route_generate(self, dict_, i, t, weight):
        '''
        w1 充电电价权重
        w2 路线成本权重（包含耗电和时间成本）
        '''

        # for j in range(len(DICT['Road'].Road_network)):
            # if (self.Car_area_T[i] in DICT['Road'].Road_network[j]) and (self.Car_next[i, 0] in DICT['Road'].Road_network[j]):
            #     DICT['Road'].Road_charge[j, t] += 1

        cost, w1, w2 = float('inf'), 1, 2
        power = self.Car_C_max[i] * (0.9 - self.Car_SOC_T[i])
        for j in range(dict_['CS'].CS_num):
            self.Car_destination[i] = dict_['CS'].CS_area[j]
            price = dict_['CS'].CS_Price[j, t//120]
            route_, r_cost_ = Taxi.destination_route_generate(self, dict_, i, t, weight)
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

    def __init__(self, DATA):
        super().__init__(DATA)

    def behavior(self, DATA, DICT, t):
        t_ = DICT['Param'].TT / DICT['Param'].T
        # 更新全路段行车效率
        weight = {}
        for j in range(DICT['Road'].Road_num):
            beta = DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][0] + \
                   DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][1] * (
                           DICT['Road'].Road_flow[j, t] / DICT['Road'].Road_capacity[j]) ** \
                   DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][2]
            x = tuple(DICT['Road'].Road_network[j])
            weight[x] = 1 + (DICT['Road'].Road_flow[j,t] / DICT['Road'].Road_capacity[j]) ** beta
        for i in range(self.Car_num):
            if t//t_ < self.Car_T_start[i]:
                continue
            if t//t_ == self.Car_T_start[i]:
                self.Car_charge_flag[i] = 0

            if t//t_ > self.Car_T_end[i] and self.Car_area_T[i] == self.Car_area_start[i]:
                if not self.Car_charge_flag[i]:
                    DATA['EV_BUS'] = np.append(DATA['EV_BUS'], DICT['area'].area_BUS[self.Car_area_T[i]])
                    DATA['EV_T_in'] = np.append(DATA['EV_T_in'], t // t_)
                    DATA['EV_T_out'] = np.append(DATA['EV_T_out'], self.Car_T_start[i] if t//t_ == 0 else self.Car_T_start[i] + DICT['Param'].T)
                    DATA['EV_SOC_in'] = np.append(DATA['EV_SOC_in'], self.Car_SOC_T[i])
                    DATA['EV_SOC_out'] = np.append(DATA['EV_SOC_out'], self.Car_SOC_end[i])
                    DATA['EV_C_max'] = np.append(DATA['EV_C_max'], self.Car_C_max[i])
                    DATA['EV_P_dischar_max'] = np.append(DATA['EV_P_dischar_max'], self.Car_P_discharge[i] * DATA['TT'] / DATA['T'])
                    DATA['EV_P_char_max'] = np.append(DATA['EV_P_char_max'], self.Car_P_charge[i] * DATA['TT'] / DATA['T'])
                    DATA['EV_lambda_char'] = np.append(DATA['EV_lambda_char'], self.Car_P_charge_lambda[i])
                    self.Car_charge_flag[i] = 1
                continue

            if t//t_ > self.Car_T_end[i] and self.Car_destination[i] == 0:
                self.Car_destination[i] = self.Car_area_start[i]
                self.Car_route[i], _ = Taxi.destination_route_generate(self, DICT, i, t, weight)
                self.Car_road_T[i] = self.Car_route[i][0]
                DICT['Road'].Road_flow[self.Car_road_T[i], t] += 1


            # 评估充电需求,充电站充电
            if self.Car_charge_flag[i]:
                self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
                if self.Car_SOC_T[i] >= 0.9:
                    self.Car_charge_flag[i] = False
                continue
            if self.Car_SOC_T[i] <= self.Car_SOC_warn[i]:
                if self.Car_area_T[i] in DICT['CS'].CS_area:
                    self.Car_charge_flag[i] = True
                    DATA['EV_BUS'] = np.append(DATA['EV_BUS'], DICT['area'].area_BUS[self.Car_area_T[i]])
                    DATA['EV_T_in'] = np.append(DATA['EV_T_in'], t // t_)
                    DATA['EV_T_out'] = np.append(DATA['EV_T_out'], t//t_ + (self.Car_SOC_end[i]-self.Car_SOC_T[i])*self.Car_C_max[i]//self.Car_P_charge[i])


                    DATA['EV_SOC_in'] = np.append(DATA['EV_SOC_in'], self.Car_SOC_T[i])
                    DATA['EV_SOC_out'] = np.append(DATA['EV_SOC_out'], self.Car_SOC_end[i])
                    DATA['EV_C_max'] = np.append(DATA['EV_C_max'], self.Car_C_max[i])
                    DATA['EV_P_dischar_max'] = np.append(DATA['EV_P_dischar_max'], self.Car_P_discharge[i] * DATA['TT'] / DATA['T'])
                    DATA['EV_P_char_max'] = np.append(DATA['EV_P_char_max'], self.Car_P_charge[i] * DATA['TT'] / DATA['T'])
                    DATA['EV_lambda_char'] = np.append(DATA['EV_lambda_char'], self.Car_P_charge_lambda[i])
                    self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
                    continue

                # distance = 0
                # for n in self.Car_route[i]:
                #     for j in range(len(DICT['Road'].Road_network)):
                #         if n is DICT['Road'].Road_network[j]:
                #             distance += DICT['Road'].Road_length[j]
                # if self.Car_destination[i] == 0 or self.Car_SOC_T[i] - self.Car_P[i] * distance <= self.Car_SOC_baseline[i]:
                if self.Car_destination[i] == 0:
                    self.Car_route[i] = Taxi.charge_route_generate(self, DICT, i, t, weight)
                    self.Car_road_T[i] = self.Car_route[i][0]
                    DICT['Road'].Road_flow[self.Car_road_T[i], t] += 1

            # 目的地选取
            if self.Car_destination[i] == 0:
                Taxi.destination_generate(self, DICT, i)
                self.Car_route[i],_ = Taxi.destination_route_generate(self, DICT, i, t, weight)
                self.Car_road_T[i] = self.Car_route[i][0]
                DICT['Road'].Road_flow[self.Car_road_T[i], t] += 1


            # # 状态更新
            # self.Car_area_T[i] = ...
            j = self.Car_road_T[i]
            beta = DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][0] + \
                   DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][1] * (
                           DICT['Road'].Road_flow[j, t] / DICT['Road'].Road_capacity[j]) ** \
                   DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][2]
            speed = self.Car_v[i] / (1 + (DICT['Road'].Road_flow[j, t] / DICT['Road'].Road_capacity[j]) ** beta)
            self.Car_SOC_T[i] -= speed * self.Car_P[i] / self.Car_C_max[i]
            self.Car_next[i] += speed / DICT['Road'].Road_length[j]

            if self.Car_next[i] > 1:
                DICT['Road'].Road_flow[self.Car_road_T[i], t] -= 1
                self.Car_area_T[i] = sum(DICT['Road'].Road_network[self.Car_road_T[i]]) - self.Car_area_T[i]
                self.Car_route[i] = np.delete(self.Car_route[i],0,0)
                if len(self.Car_route[i]) == 0:
                    self.Car_destination[i] = 0
                    continue
                self.Car_road_T[i] = self.Car_route[i][0]
                self.Car_next[i] = 0
                DICT['Road'].Road_flow[self.Car_road_T[i], t] += 1



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

    def __init__(self, DATA):
        super().__init__(DATA)
        self.Car_area_end = DATA['Car_area_end']

    def behavior(self, DATA, DICT, t):
        t_ = DICT['Param'].TT / DICT['Param'].T
        # 更新全路段行车效率
        weight = {}
        for j in range(DICT['Road'].Road_num):
            beta = DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][0] + \
                   DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][1] * (
                           DICT['Road'].Road_flow[j, t] / DICT['Road'].Road_capacity[j]) ** \
                   DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][2]
            x = tuple(DICT['Road'].Road_network[j])
            weight[x] = 1 + (DICT['Road'].Road_flow[j,t] / DICT['Road'].Road_capacity[j]) ** beta
        for i in range(self.Car_num):

            if t/t_ == self.Car_T_start[i]:
                self.Car_SOC_T[i] = self.Car_SOC_end[i]
                self.Car_charge_flag[i] = False
                self.Car_destination[i] = self.Car_area_end[i]
                self.Car_route[i], _ = PrivateCar.destination_route_generate(self, DICT, i, t, weight)
                self.Car_road_T[i] = self.Car_route[i][0]
                DICT['Road'].Road_flow[self.Car_road_T[i], t] += 1

            if t/t_ == self.Car_T_end[i]:
                self.Car_SOC_T[i] = self.Car_SOC_end[i]
                self.Car_charge_flag[i] = False
                self.Car_destination[i] = self.Car_area_start[i]
                self.Car_route[i], _ = PrivateCar.destination_route_generate(self, DICT, i, t, weight)
                self.Car_road_T[i] = self.Car_route[i][0]
                DICT['Road'].Road_flow[self.Car_road_T[i], t] += 1

            # # 评估充电需求,充电站充电
            # if self.Car_charge_flag[i]:
            #     self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
            #     if self.Car_SOC_T[i] >= 0.9:
            #         self.Car_charge_flag[i] = False
            #     continue
            # if self.Car_SOC_T[i] <= self.Car_SOC_warn[i]:
            #     if self.Car_area_T[i] in DICT['CS'].CS_area:
            #         self.Car_charge_flag[i] = True
            #         self.Car_SOC_T[i] = self.Car_SOC_T[i] + self.Car_P_charge[i]/self.Car_C_max[i]
            #         continue
            #
            #     # distance = 0
            #     # for n in self.Car_route[i]:
            #     #     for j in range(len(DICT['Road'].Road_network)):
            #     #         if n is DICT['Road'].Road_network[j]:
            #     #             distance += DICT['Road'].Road_length[j]
            #     # if self.Car_destination[i] == 0 or self.Car_SOC_T[i] - self.Car_P[i] * distance <= self.Car_SOC_baseline[i]:
            #     if self.Car_destination[i] == 0:
            #         self.Car_route[i] = Taxi.charge_route_generate(self, DICT, i, t)
            #         self.Car_next[i, 0] = np.sum(self.Car_route[i][0]) - self.Car_area_T[i]

            # 状态更新
            if self.Car_charge_flag[i]:
                continue
            elif self.Car_destination[i] != 0:
                j = self.Car_road_T[i]
                beta = DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][0] + \
                       DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][1] * (
                               DICT['Road'].Road_flow[j, t] / DICT['Road'].Road_capacity[j]) ** \
                       DICT['Road'].a_b_n[DICT['Road'].Road_grade[j] - 1][2]
                speed = self.Car_v[i] / (1 + (DICT['Road'].Road_flow[j, t] / DICT['Road'].Road_capacity[j]) ** beta)
                self.Car_SOC_T[i] -= speed * self.Car_P[i] / self.Car_C_max[i]
                self.Car_next[i] += speed / DICT['Road'].Road_length[j]

                if self.Car_next[i] > 1:
                    DICT['Road'].Road_flow[self.Car_road_T[i], t] -= 1
                    self.Car_area_T[i] = sum(DICT['Road'].Road_network[self.Car_road_T[i]]) - self.Car_area_T[i]
                    self.Car_route[i] = np.delete(self.Car_route[i], 0, 0)
                    if len(self.Car_route[i]) == 0:
                        self.Car_destination[i] = 0
                        continue
                    self.Car_road_T[i] = self.Car_route[i][0]
                    self.Car_next[i] = 0
                    DICT['Road'].Road_flow[self.Car_road_T[i], t] += 1



            #  进入电动汽车需求响应充电模式
            else:
                DATA['EV_BUS'] = np.append(DATA['EV_BUS'], DICT['area'].area_BUS[self.Car_area_T[i]])
                DATA['EV_T_in'] = np.append(DATA['EV_T_in'], t//t_)

                if self.Car_area_T[i] == self.Car_area_end[i]:
                    T_out = self.Car_T_end[i]
                else:
                    if t//t_ == 0:
                        T_out = self.Car_T_start[i]
                    else:
                        T_out = self.Car_T_start[i] + DICT['Param'].T
                DATA['EV_T_out'] = np.append(DATA['EV_T_out'], T_out)

                DATA['EV_SOC_in'] = np.append(DATA['EV_SOC_in'], self.Car_SOC_T[i])
                DATA['EV_SOC_out'] = np.append(DATA['EV_SOC_out'], self.Car_SOC_end[i])
                DATA['EV_C_max'] = np.append(DATA['EV_C_max'], self.Car_C_max[i])
                DATA['EV_P_dischar_max'] = np.append(DATA['EV_P_dischar_max'], self.Car_P_discharge[i] * DATA['TT'] / DATA['T'])
                DATA['EV_P_char_max'] = np.append(DATA['EV_P_char_max'], self.Car_P_charge[i] * DATA['TT'] / DATA['T'])
                DATA['EV_lambda_char'] = np.append(DATA['EV_lambda_char'], self.Car_P_charge_lambda[i])
                self.Car_charge_flag[i] = True

