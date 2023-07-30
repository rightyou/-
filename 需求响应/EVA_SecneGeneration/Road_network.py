import numpy as np




class Road():
    def __init__(self, DATA, param):
        '''
        area_num 节点数量
        Road_network 路网连接拓扑
        Road_length 道路长度
        Road_grade 道路等级
        Road_capacity 道路通行能力
        Road_flow 道路流量
        Road_charge 道路充电需求
        a_b_n 道路等级对应参数
        '''
        self.area_num = DATA['area_num']
        self.Road_network = DATA['Road_network']
        self.Road_num = len(self.Road_network)
        self.Road_length = DATA['Road_length']
        self.Road_grade = DATA['Road_grade']
        self.Road_capacity = DATA['Road_capacity']
        self.Road_flow = np.zeros((self.Road_num, param.TT))
        self.Road_charge = np.zeros((self.Road_num, param.TT))
        self.a_b_n = np.array([[1.726,3.15,3.],[2.076,2.87,3.]])
