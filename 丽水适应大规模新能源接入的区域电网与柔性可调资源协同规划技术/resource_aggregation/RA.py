import numpy as np
import pandas as pd
import copy

from .read_data import *
from .EnergyStorage import *
from .cluster import *


def energy_storage__aggregate(DICT):
    Dict = copy.deepcopy(DICT)
    Dict.update({
        'n_clusters': {},
        'types_clusters': ['ess', 'psh', 'hpp', 'ac', 'ev', 'industrial_consumer'],
        'para_clusters': ['eta', 'Lambda', 'Pmax', 'Pmin', 'Emax', 'Emin', 'RUmax', 'RDmax'],
        'ES__cluster': {i: [] for i in range(Dict['BUS'])},
    })

    # for path in paths:
    #     if 'ESS' == path:
    #         Dict['ess'] = read__ess(Dict, paths[path])
    #     if 'PumpedStorage' == path:
    #         Dict['pumped_storage'] = read__pumped_storage(Dict, paths[path])

    #
    Dict['energy_storage'] = KmeansCluster(Dict)

    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters'][bus]):
            Dict['ES__cluster'][bus].append(ES__Cluster(Dict, bus, cluster_num))

    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters'][bus]):
            Dict['ES__cluster'][bus][cluster_num].adjustable_capability(Dict, bus, cluster_num)

    DICT.update({
        # 'ES__cluster': Dict['ES__cluster'],
        'energy_storage': Dict['energy_storage']
    })

    return DICT


def generate__aggregate(DICT):
    Dict = copy.deepcopy(DICT)
    Dict.update({
        'n_clusters': {},
        'types_clusters': ['ror', 'pv', 'wp', 'distributed_pv'],
        'para_clusters': ['eta', 'Pmin', 'RUmax', 'RDmax'],
        'G__cluster': {i: [] for i in range(Dict['BUS'])},
    })

    # for path in paths:
    #     if 'HPP' == path:
    #         Dict['HPP'] = read__hydroelectric(Dict, paths[path])
    #     if 'PV' == path:
    #         Dict['PV'] = read__pv(Dict, paths[path])
    #     if 'ThermalPower' == path:
    #         Dict['ThermalPower'] = read__thermal_power(Dict, paths[path])
    #     if 'WP' == path:
    #         Dict['WP'] = read__wp(Dict, paths[path])

    Dict['generate'] = KmeansCluster(Dict)

    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters'][bus]):
            Dict['G__cluster'][bus].append(G__Cluster(Dict, bus, cluster_num))

    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters'][bus]):
            Dict['G__cluster'][bus][cluster_num].adjustable_capability(Dict, bus, cluster_num)

    DICT.update({
        'G__cluster': Dict['G__cluster'],
        'generate': Dict['generate'],
    })

    # return DICT
