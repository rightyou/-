import numpy as np
import pandas as pd
import math


class EVA():
    def __init__(self, dict_):
        self.EV_BUS = dict_['EV_BUS']
        self.EV_T_in = dict_['EV_T_in']
        self.EV_T_out = dict_['EV_T_out']
        self.EV_SOC_in = dict_['EV_SOC_in']
        self.EV_SOC_out = dict_['EV_SOC_out']
        self.EV_C_max = dict_['EV_C_max']
        self.EV_P_char_max = dict_['EV_P_char_max']
        self.EV_lambda_char = dict_['EV_lambda_char']
        self.EVA_BUS = np.unique(self.EV_BUS)

        EVA_up = np.zeros((len(self.EVA_BUS),dict_['T']))
        EVA_down = np.zeros((len(self.EVA_BUS), dict_['T']))
        EVA_P_char_max = np.zeros((len(self.EVA_BUS), dict_['T']))
        for i in range(len(self.EV_BUS)):
            P = self.EV_lambda_char[i]*self.EV_P_char_max[i]
            EVA_P_char_max[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]:self.EV_T_out[i]] += P
            delta_T = math.ceil(self.EV_C_max[i]*(self.EV_SOC_out[i]-self.EV_SOC_in[i])/P)
            if self.EV_T_out[i]-self.EV_T_in[i] < delta_T:
                for j in range(self.EV_T_out[i]-self.EV_T_in[i]):
                    EVA_up[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]+j:self.EV_T_out[i]] += P  # 实际时间与索引序号差一
                EVA_down[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]:self.EV_T_out[i]] = EVA_up[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]:self.EV_T_out[i]]
            else:
                for j in range(delta_T):
                    EVA_up[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i]+j:self.EV_T_in[i]+delta_T] += P
                    EVA_up[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_in[i] + delta_T:self.EV_T_out[i]] += P
                    EVA_down[int(np.argwhere(self.EVA_BUS == self.EV_BUS[i])[0]), self.EV_T_out[i]-1:self.EV_T_out[i]-j-2:-1] += P
        self.EVA_up = EVA_up
        self.EVA_down = EVA_down
        self.EVA_P_char_max = EVA_P_char_max






        pass