from scripts.experiment import *
from scripts.output_results import write_batch_experiment_summary
from datetime import date, datetime


repeat_num = 1
# household_nums = [2000, 4000, 6000, 8000, 10000]
# household_nums = [20, 40, 60, 80, 100]
household_nums = [50]
care_factor_weights = [0, 1, 5, 10, 50, 100, 500, 1000, 5000, 10000]
new_data = True
# new_data = False
type_cost_function = "piece-wise"
# type_cost_function = "linear"

algorithms_labels = dict()
algorithms_labels[k1_optimal] = dict()
algorithms_labels[k1_optimal][k2_scheduling] = k1_optimal
algorithms_labels[k1_optimal][k2_pricing] = "{}_fw".format(k1_optimal)
algorithms_labels[k1_heuristic] = dict()
algorithms_labels[k1_heuristic][k2_scheduling] = k1_heuristic
algorithms_labels[k1_heuristic][k2_pricing] = f"{k1_heuristic}_fw"

this_date = str(date.today())
this_time = str(datetime.now().time().strftime("%H-%M-%S"))
date_folder = result_folder + "{}/".format(this_date)
date_time_folder = date_folder + f"{this_time}/"

experiment_summary_dict = dict()
group_by_columns = [k0_households_no, k0_tasks_no, "algorithm", k0_penalty_weight, k0_cost_type]


def run():
    for num_household in household_nums:
        for cfw in care_factor_weights:
            for r in range(repeat_num):
                date_time_experiment_folder = date_time_folder + f"h{num_household}-t{no_tasks_min}-w{cfw}-r{r}/"

                experiment_summary = experiment(num_household, no_tasks_min, no_tasks_min + 2, cfw,
                                                new_data, type_cost_function,
                                                algorithms_labels, date_time_experiment_folder)
                for algorithm in algorithms_labels.values():
                    for v in algorithm.values():
                        experiment_summary_dict[r, num_household, cfw, v] = experiment_summary[v]

                # write batch experiment summary
                write_batch_experiment_summary(experiment_summary_dict, group_by_columns, date_time_folder, this_time)


if __name__ == '__main__':
    run()
