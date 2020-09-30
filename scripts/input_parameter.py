# time related parameters
no_intervals = 144
no_periods = 48
no_intervals_periods = int(no_intervals / no_periods)

# household related parameters
new_households = True
new_households = False
no_households = 100
no_tasks = 5
max_demand_multiplier = no_tasks
care_f_max = 10
care_f_weight = 10

# pricing related parameters
pricing_table_weight = 1.0
# cost_function_type = "linear"
cost_function_type = "piece-wise"
zero_digit = 2

# solver related parameters
var_selection = "smallest"
val_choice = "indomain_min"
model_type = "pre"
solver_type = "cp"

# external file related parameters
# from os import getcwd
# parent_folder = getcwd() + "/"
# if "multiple" not in folder_current:
#     parent_folder += "multiple/"
parent_folder = ""
file_cp_pre = parent_folder + 'models/Household-cp-pre.mzn'
file_cp_ini = parent_folder + 'models/Household-cp.mzn'
file_pricing_table = parent_folder + 'data/pricing_table_0.csv'
file_household_area_folder = parent_folder + 'data/'
file_probability = parent_folder + 'data/probability.csv'
file_demand_list = parent_folder + 'data/demands_list.csv'
output_folder = parent_folder + "results/"

# summary related parameters
k0_summary = "summary"
k1_penalty_weight = "penalty_weight"
k1_households_no = "no_households"
k1_tasks_no = "no_tasks"
k1_cost_type = "cost_function_type"

# demand related parameters
k0_starts = "start_times"
k0_demand = "demands"
k0_demand_max = "max_demand"
k0_demand_total = "total_demand"
k0_par = "PAR"
# step size
k0_step = "step_size"
# objective related parameters
k0_cost = "cost"
k0_penalty = "inconvenient"
k0_obj = "objective"
# pricing related parameters
k0_prices = "prices"
k0_price_levels = "price_levels"
k0_demand_table = "demand_levels"
# run time related
k0_time = "reschedule_time"

# k1_interval = "interval"
# k1_period = "period"
k1_optimal = "optimal"
k1_heuristic = "heuristic"
k2_scheduling = "scheduling"
k2_pricing = "pricing"

