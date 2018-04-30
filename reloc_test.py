import Settings as Set
import Initialize as Init
import Main
import csv
import time
__author__ = 'Mike'

t0 = time.time()

#######################################################################################################################
# Inputs for Simulation Runs
#######################################################################################################################

area_size_km = 10.0
area_size = area_size_km * 1000.0

# requests_per_hour = [900, 1000, 1100, 1200, 1300]
# requests_per_hour = 700

# demand_Type = ["O_Uniform_D_Uniform"]   # "O_Cluster_D_Cluster",


fleet_size = 1000

assign_interval =  30
relocate_interval = 60

# opt_methods = ["1_FCFS_longestIdle", "2_FCFS_nearestIdle",
#                "3_FCFS_smartNN",  "4_FCFS_drop_smartNN", "4a_FCFS_drop_smartNN2",
#                "5_match_idleOnly", "6_match_idlePick",
#                "7_match_idleDrop", "7_match_idleDrop2",
#                "8_match_idlePickDrop"]

opt_method = "3_FCFS_smartNN"

relocate_method = "Dandl"

xyt_string = "2x_8y_5min"

i_date = "2016-04-01"

#######################################################################################################################
# Create Files to Write Results
#######################################################################################################################

csv_results2 = open(
    '../Results/Dandl_Hyland' + '_holds' + str(assign_interval) + '_fleet'
    + str(fleet_size) + '_opt' + opt_method + '.csv', 'w')
results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"',
                             quoting=csv.QUOTE_NONNUMERIC)
results_writer2.writerow(
    ["Runs", "Sim_Length", "Hold Time",
     "Area Size", "Opt Method", "Reloc Method",  "Fleet Size",
     "Mean Wait Pick", "% Empty", "% Reassign", "Fleet Util",
     "#Served", "#inVeh", "#Assgnd", "#Unassgnd"])


#######################################################################################################################
# Loop Through Simulations
#######################################################################################################################

results_run = []
for i_run in range(0, 1):
    # generate random demand
    # Init.generate_demand(Set.t_max, a_demand_rate, q_area_size, Set.max_group_size,
    #                      p_demand_type)
    # generate fleet
    Init.generate_fleet(area_size, fleet_size, Set.veh_capacity)

    print("run #:", i_run, " area size:", area_size / 1000)
    print("fleet size:", fleet_size, " hold for:", assign_interval, " Opt Method:", opt_method)

    results = Main.main(assign_interval, relocate_interval, Set.t_max, Set.time_step,
                         opt_method, relocate_method, Set.veh_speed, i_date, True,
                         xyt_string, false_forecast_f=None)

    results_run.append(results)
    print(results)
    print(time.time() - t0)

avg = [float(sum(col)) / len(col) for col in zip(*results_run)]
results_writer2.writerow(
    [i_run, Set.t_max, assign_interval,
      area_size / 1000, opt_method, relocate_method, fleet_size,
     avg[0], avg[1] / 60.0, avg[2], avg[3],
     avg[4], avg[5], avg[6], avg[7]])

csv_results2.close()
