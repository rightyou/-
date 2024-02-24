import pandas as pd


from .EnergyStorage import *
from .Generate import *



def read__ess(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        ess = ESS(Dict, data.loc[i])
        dict[ess.BUS].append(ess)

    return dict


def read__pumped_storage(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        pumped_storage = PumpedStorage(Dict, data.loc[i])
        dict[pumped_storage.BUS].append(pumped_storage)

    return dict


def read__hydroelectric(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        hydroelectric = Hydroelectric(Dict, data.loc[i])
        dict[hydroelectric.BUS].append(hydroelectric)

    return dict


def read__pv(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        pv = PV(Dict, data.loc[i])
        dict[pv.BUS].append(pv)

    return dict


def read__thermal_power(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        thermal_power = ThermalPower(Dict, data.loc[i])
        dict[thermal_power.BUS].append(thermal_power)

    return dict


def read__wp(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        wp = WP(Dict, data.loc[i])
        dict[wp.BUS].append(wp)

    return dict

