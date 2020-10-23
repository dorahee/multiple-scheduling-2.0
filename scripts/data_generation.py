import pickle
from numpy import genfromtxt
import random as r
import numpy as np
from numpy import sqrt, pi, random
import os
from more_itertools import grouper
from scripts.input_parameter import *
from scripts.cfunctions import average
from pandas import read_csv
from pathlib import Path
from json import dumps


def read_data(f_cp_pre, f_cp_ini, f_pricing_table, demand_level_scale, zero_digit):
    models = dict()
    models["cp"] = dict()
    models["cp"]["pre"] = f_cp_pre
    models["cp"]["init"] = f_cp_ini

    solvers = dict()
    solvers["cp"] = "gecode"

    csv_table = read_csv(f_pricing_table, header=None)
    num_levels = len(csv_table.index)
    csv_table.loc[num_levels + 1] = [csv_table[0].values[-1] * 10] + [demand_level_scale * 1.1 for _ in range(no_periods)]

    pricing_table = dict()
    pricing_table[k0_price_levels] = list(csv_table[0].values)
    pricing_table[k0_demand_table] = dict()
    pricing_table[k0_demand_table] = \
        {period:
            {level:
                round(csv_table[period + 1].values[level] * demand_level_scale, -zero_digit)
             for level in range(len(csv_table[period + 1]))}
         for period in range(no_periods)}
    # with open(f_pricing_table, 'r') as csvfile:
    #     csvreader = reader(csvfile, delimiter=',', quotechar='|')
    #
    #     for i_row, row in enumerate(csvreader):
    #         # a row - the price and the demands of all periods at one level.
    #         pricing_table_row = list(map(float, row))
    #         # a col - the demand at one level of a period
    #         for i_col, col in enumerate(pricing_table_row[1:]):
    #             if i_col not in pricing_table[k0_demand_table]:
    #                 pricing_table[k0_demand_table][i_col] = dict()
    #             pricing_table[k0_demand_table][i_col][i_row] = round(col * demand_level_scale, -zero_digit)

    return models, solvers, pricing_table


def task_generation(num_intervals, num_periods, num_intervals_periods, mode_value, l_demands, p_d_short, cf_max):
    # generation - demand
    demand = r.choice(l_demands)
    demand = int(demand * 1000)

    # generation - duration
    duration = max(1, int(random.rayleigh(mode_value, 1)[0]))

    # generation - preferred start time
    p_start = max(int(np.random.choice(a=num_periods, size=1, p=p_d_short)[0]) * num_intervals_periods
                  + r.randint(-num_intervals_periods + 1, num_intervals_periods), 0)
    p_start = min(p_start, num_intervals - 1)

    # generation - earliest starting time
    # e_start = r.randint(-duration + 1, p_start)
    e_start = 0

    # generation - latest finish time
    # l_finish = r.randint(p_start + duration, num_intervals - 1 + duration)
    l_finish = num_intervals - 1 + duration

    # generation - care factor
    # care_f = int(r.choice([i for i in range(1, cf_max + 1)]))
    care_f = r.randint(1, cf_max + 1)

    return demand, duration, p_start, e_start, l_finish, care_f


def household_generation(num_intervals, num_periods, num_intervals_periods, num_tasks_min, num_tasks_max, p_d,
                         max_demand_mul, cf_max, f_demand_list):
    p_d_short = [int(p) for p in p_d[0]]
    sum_t = sum(p_d_short)
    p_d_short = [p / sum_t for p in p_d_short]

    l_demands = genfromtxt(f_demand_list, delimiter=',', dtype="float")

    # I meant mean value is 40 minutes
    mean_value = 40.0 / (24.0 * 60.0 / num_intervals)
    mode_value = sqrt(2 / pi) * mean_value

    # task details
    preferred_starts = []
    earliest_starts = []
    latest_ends = []
    durations = []
    demands = []
    care_factors = []
    aggregated_loads = [0] * num_intervals

    # tasks in the household
    num_tasks = r.randint(num_tasks_min, num_tasks_max)
    for counter_j in range(num_tasks):
        demand, duration, p_start, e_start, l_finish, care_f \
            = task_generation(num_intervals, num_periods, num_intervals_periods,
                              mode_value, l_demands, p_d_short, cf_max)
        demands.append(demand)
        durations.append(duration)
        preferred_starts.append(p_start)
        earliest_starts.append(e_start)
        latest_ends.append(l_finish)
        care_factors.append(care_f)
        # add this task demand to the household demand
        for d in range(duration):
            aggregated_loads[(p_start + d) % num_intervals] += demand
    # set the household demand limit
    maximum_demand = max(demands) * max_demand_mul

    # precedence among tasks
    precedors = dict()
    no_precedences = 0
    succ_delays = dict()

    def retrieve_precedes(list0):
        list3 = []
        for l in list0:
            if l in precedors:
                list2 = precedors[l]
                retrieved_list = retrieve_precedes(list2)
                list3.extend(retrieved_list)
            else:
                list3.append(l)
        return list3

    def add_precedes(task, previous, delay):
        if task not in precedors:
            precedors[task] = [previous]
            succ_delays[task] = [delay]
        else:
            precedors[task].append(previous)
            succ_delays[task].append(delay)

    for t in range(int(num_tasks / 2), num_tasks):
        if r.choice([True, False]):
            previous_tasks = list(range(t))
            r.shuffle(previous_tasks)
            for prev in previous_tasks:
                if preferred_starts[prev] + durations[prev] - 1 < preferred_starts[t] \
                        and earliest_starts[prev] + durations[prev] < latest_ends[t] - durations[t] + 1:

                    if prev not in precedors:
                        # feasible delay
                        succeding_delay = num_intervals - 1
                        add_precedes(t, prev, succeding_delay)
                        no_precedences += 1
                        break
                    else:
                        # find all precedors of this previous task
                        precs_prev = retrieve_precedes([prev])
                        precs_prev.append(prev)

                        precs_prev_duration = sum([durations[x] for x in precs_prev])
                        latest_pstart = preferred_starts[precs_prev[0]]
                        latest_estart = earliest_starts[precs_prev[0]]

                        if latest_pstart + precs_prev_duration - 1 < preferred_starts[t] \
                                and latest_estart + precs_prev_duration < latest_ends[t] - durations[t] + 1:
                            succeding_delay = num_intervals - 1
                            add_precedes(t, prev, succeding_delay)
                            no_precedences += 1
                            break

    # print(" --- Household made ---")

    return preferred_starts, earliest_starts, latest_ends, durations, demands, care_factors, \
        no_precedences, precedors, succ_delays, maximum_demand, aggregated_loads


def area_generation(num_intervals, num_periods, num_intervals_periods, data_folder, exp_folder,
                    num_households, num_tasks_min, num_tasks_max, cf_weight, cf_max, max_d_multiplier,
                    f_probability, f_demand_list, algorithms_labels):
    probability = genfromtxt(f_probability, delimiter=',', dtype="float")

    households = dict()
    area_demand_profile = [0] * num_intervals

    # household_folder = exp_folder + "households/"
    # path_h_folder = Path(household_folder)
    # if not path_h_folder.exists():
    #     path_h_folder.mkdir(mode=0o777, parents=True, exist_ok=False)

    for h in range(num_households):
        preferred_starts, earliest_starts, latest_ends, durations, demands, care_factors, \
        num_precedences, precedors, succ_delays, max_demand, household_profile \
            = household_generation(num_intervals, num_periods, num_intervals_periods, num_tasks_min, num_tasks_max,
                                   probability, max_d_multiplier, cf_max, f_demand_list)

        household_key = h
        households[household_key] = dict()

        households[household_key][k0_household_key] = household_key
        households[household_key]["demands"] = demands
        households[household_key]["durs"] = durations
        households[household_key]["ests"] = earliest_starts
        households[household_key]["lfts"] = latest_ends
        households[household_key]["psts"] = preferred_starts
        households[household_key]["cfs"] = [cf * cf_weight for cf in care_factors]
        households[household_key]["precs"] = precedors
        households[household_key]["succ_delays"] = succ_delays
        households[household_key]["no_prec"] = num_precedences
        households[household_key]["care_factor_weight"] = cf_weight

        households[household_key]["demand"] = dict()
        households[household_key]["demand"]["preferred"] = household_profile
        households[household_key]["demand"]["max"] = max(household_profile)
        households[household_key]["demand"]["limit"] = max(household_profile)

        households[household_key][k0_starts] = dict()
        households[household_key][k0_cost] = dict()
        households[household_key][k0_penalty] = dict()
        households[household_key][k0_obj] = dict()

        for k in algorithms_labels.keys():
            households[household_key][k0_starts][k] = dict()
            # households[household_key][k0_starts][k1_optimal_scheduling] = dict()

            households[household_key][k0_starts][k][0] = preferred_starts
            # households[household_key][k0_starts][k1_optimal_scheduling][0] = preferred_starts

        area_demand_profile = [x + y for x, y in zip(household_profile, area_demand_profile)]

        # write this household data to a file
        # with open(household_folder + "household{}.json".format(household_key), 'w+') as f:
        #     f.write(dumps(households[household_key], indent=1))
        # f.close()


    area_demand_profile2 = [sum(x) for x in grouper(area_demand_profile, num_intervals_periods)]
    max_demand = max(area_demand_profile2)
    total_demand = sum(area_demand_profile2)
    par = round(max_demand / average(area_demand_profile2), 2)
    area = dict()
    for k1, v1 in algorithms_labels.items():
        for v2 in v1.values():
            area[v2] = dict()
            area[v2][k0_demand] = dict()
            area[v2][k0_demand_max] = dict()
            area[v2][k0_demand_total] = dict()
            area[v2][k0_par] = dict()
            area[v2][k0_penalty] = dict()

            area[v2][k0_demand][0] = area_demand_profile2
            area[v2][k0_demand_max][0] = max_demand
            area[v2][k0_demand_total][0] = total_demand
            area[v2][k0_par][0] = par
            area[v2][k0_penalty][0] = 0

    # write household data and area data into files
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    with open(data_folder + "households" + '.pkl', 'wb+') as f:
        pickle.dump(households, f, pickle.HIGHEST_PROTOCOL)
    f.close()

    with open(data_folder + "area" + '.pkl', 'wb+') as f:
        pickle.dump(area, f, pickle.HIGHEST_PROTOCOL)
    f.close()

    return households, area


def area_read(data_folder):
    with open(data_folder + "households" + '.pkl', 'rb') as f:
        households = pickle.load(f)
    f.close()

    with open(data_folder + "area" + '.pkl', 'rb') as f:
        area = pickle.load(f)
    f.close()

    return households, area
