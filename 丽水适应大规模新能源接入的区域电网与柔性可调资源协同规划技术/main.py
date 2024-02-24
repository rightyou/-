import time



from resource_aggregation import *



if __name__ == '__main__':
    start = time.time()
    DICT = {
        'T': 96,
        'BUS': 10
    }



    # 场景生成



    # 资源聚合
    energy_storage__paths = {
        'ESS': 'data/ES/ess.xlsx',
        'PumpedStorage': 'data/ES/Pumped storage.xlsx',
    }
    generate__path = {
        'Hydroelectric': 'data/generate/Hydroelectric.xlsx',
        'PV': 'data/generate/PV.xlsx',
        'ThermalPower': 'data/generate/Thermal Power.xlsx',
        'WP': 'data/generate/WP.xlsx',
    }

    RA.energy_storage__aggregate(DICT, energy_storage__paths)
    RA.generate__aggregate(DICT, generate__path)




    end = time.time()
    print(end - start)
    pass
