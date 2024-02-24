import numpy as np
import pandas as pd
import copy



from .read_data import *
from .EnergyStorage import *
from .cluster import *



def energy_storage__aggregate(DICT, paths):
    Dict = copy.deepcopy(DICT)
    Dict.update({
        'n_clusters': 3,
        'types_clusters': ['ess', 'pumped_storage'],
        'para_clusters': ['eta', 'Lambda'],
        'ES__cluster': {i: [] for i in range(Dict['BUS'])},
    })


    for path in paths:
        if 'ESS' == path:
            Dict['ess'] = read__ess(Dict, paths[path])
        if 'PumpedStorage' == path:
            Dict['pumped_storage'] = read__pumped_storage(Dict, paths[path])


    #
    Dict['energy_storage'] = KmeansCluster(Dict)


    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters']):
            Dict['ES__cluster'][bus].append(ES__Cluster(Dict, bus, cluster_num))



    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters']):
            Dict['ES__cluster'][bus][cluster_num].adjustable_capability(Dict, bus, cluster_num)


    DICT.update({
        'ES__cluster': Dict['ES__cluster'],
    })

    return DICT



def generate__aggregate(DICT, paths):
    Dict = copy.deepcopy(DICT)
    Dict.update({
        'n_clusters': 3,
        'types_clusters': ['Hydroelectric', 'PV', 'ThermalPower', 'WP'],
        'para_clusters': ['eta'],
        'G__cluster': {i: [] for i in range(Dict['BUS'])},
    })

    for path in paths:
        if 'Hydroelectric' == path:
            Dict['Hydroelectric'] = read__hydroelectric(Dict, paths[path])
        if 'PV' == path:
            Dict['PV'] = read__pv(Dict, paths[path])
        if 'ThermalPower' == path:
            Dict['ThermalPower'] = read__thermal_power(Dict, paths[path])
        if 'WP' == path:
            Dict['WP'] = read__wp(Dict, paths[path])

    Dict['generate'] = KmeansCluster(Dict)

    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters']):
            Dict['G__cluster'][bus].append(G__Cluster(Dict, bus, cluster_num))



    for bus in range(Dict['BUS']):
        for cluster_num in range(Dict['n_clusters']):
            Dict['G__cluster'][bus][cluster_num].adjustable_capability(Dict, bus, cluster_num)


    DICT.update({
        'G__cluster': Dict['G__cluster'],
    })

    return DICT
