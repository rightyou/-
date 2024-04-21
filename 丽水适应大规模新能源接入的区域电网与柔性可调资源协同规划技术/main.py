import time


from resource_aggregation import (RA, typical_scenarios, EnergyStorage, Generate, read_data)


if __name__ == '__main__':
    start = time.time()
    DICT = {
        'T': 96,
        'BUS': 1,
    }

    # 电池储能
    DICT['ess'] = read_data.read__ess(DICT, 'data/ES/ESS.xlsx')
    # 抽水蓄能
    DICT['psh'] = read_data.read__psh(DICT, 'data/ES/PSH.xlsx')
    # 库容电站
    DICT['hpp'] = read_data.read__hpp(DICT, 'data/generate/HPP.xlsx')
    # 光伏
    DICT['pv'] = read_data.read__pv(DICT, 'data/generate/PV.xlsx')
    # 风机
    DICT['wp'] = read_data.read__wp(DICT, 'data/generate/WP.xlsx')
    # 分布式光伏
    DICT['distributed_pv'] = read_data.read__distributed_pv(DICT, 'data/generate/DistributedPV.xlsx')
    # 径流电站
    DICT['ror'] = read_data.read__ror(DICT, 'data/generate/ROR.xlsx')
    # 空调
    DICT['ac'] = read_data.read__ac(DICT, 'data/load/AC.xlsx')
    # 电动汽车
    DICT['ev'] = read_data.read__ev(DICT, 'data/load/EV.xlsx')
    # 工业大用户
    DICT['industrial_consumer'] = read_data.read__industrial_consumer(DICT, 'data/load/industrial consumer.xlsx')
    # # 需求响应用户
    # DICT['dr'] = read_data.read__dr(DICT, 'data/load/DR.xlsx')

    # 场景生成



    # 资源聚合
    RA.energy_storage__aggregate(DICT)
    RA.generate__aggregate(DICT)

    conflict__pv_hpp = typical_scenarios.Conflict_PV_HPP()
    conflict__pv_hpp.utility_classify(DICT)

    summer = typical_scenarios.Summer()
    summer.utility_classify(DICT)

    # # 多维评估体系
    # DICT.update({
    #     'ES__cluster': {i: [] for i in range(DICT['BUS'])},
    #     'G__cluster': {i: [] for i in range(DICT['BUS'])},
    # })
    # for bus in range(DICT['BUS']):
    #     for cluster_num in range(DICT['n_clusters']):
    #         DICT['ES__cluster'][bus].append(EnergyStorage.ES__Cluster(DICT, bus, cluster_num))
    #
    # # for bus in range(DICT['BUS']):
    # #     for cluster_num in range(DICT['n_clusters']):
    #         DICT['ES__cluster'][bus][cluster_num].adjustable_capability(DICT, bus, cluster_num)
    #
    # # for bus in range(DICT['BUS']):
    # #     for cluster_num in range(DICT['n_clusters']):
    #         DICT['G__cluster'][bus].append(Generate.G__Cluster(DICT, bus, cluster_num))
    #
    # # for bus in range(DICT['BUS']):
    # #     for cluster_num in range(DICT['n_clusters']):
    #         DICT['G__cluster'][bus][cluster_num].adjustable_capability(DICT, bus, cluster_num)




    end = time.time()
    print(end - start)
    pass
