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


def read__psh(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        psh = PSH(Dict, data.loc[i])
        dict[psh.BUS].append(psh)

    return dict


def read__ror(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        ror = ROR(Dict, data.loc[i])
        dict[ror.BUS].append(ror)

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


def read__distributed_pv(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        distributed_pv = DistributedPV(Dict, data.loc[i])
        dict[distributed_pv.BUS].append(distributed_pv)

    return dict


def read__hpp(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        data['Emax'] = data['E']
        data['Emin'] = 0
        hpp = HPP(Dict, data.loc[i])
        dict[hpp.BUS].append(hpp)

    return dict


def read__ac(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        data['RUmax'] = data['Pmax']
        data['RDmax'] = data['Pmax']
        data['a'] = 0
        data['b'] = 0
        data['c'] = data['Price']
        ac = AC(Dict, data.loc[i])
        dict[ac.BUS].append(ac)

    return dict


def read__ev(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        P = data.loc[i][-Dict['T']:]
        data['Pmax'] = max(P)
        data['Pmin'] = 0
        data['Emax'] = sum(P)
        data['Emin'] = 0
        data['RUmax'] = max(P)
        data['RDmax'] = max(P)
        data['eta'] = 1
        data['Lambda'] = 1
        data['a'] = 0
        data['b'] = 0
        data['c'] = 1
        ev = EV(Dict, data.loc[i])
        dict[ev.BUS].append(ev)

    return dict


def read__industrial_consumer(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        P = data.loc[i]
        data['Pmax'] = max(P)
        data['Pmin'] = 0
        data['Emax'] = sum(P)
        data['Emin'] = 0
        data['RUmax'] = max(P)
        data['RDmax'] = max(P)
        data['eta'] = 1
        data['Lambda'] = 1
        data['a'] = 0
        data['b'] = 0
        data['c'] = 1
        industrial_consumer = IndustrialConsumer(Dict, data.loc[i])
        dict[industrial_consumer.BUS].append(industrial_consumer)

    return dict


def read__dr(Dict, path):
    data = pd.read_excel(path)
    dict = {i: [] for i in range(Dict['BUS'])}
    for i in range(data.shape[0]):
        dr = DR(Dict, data.loc[i])
        dict[dr.BUS].append(dr)

    return dict

