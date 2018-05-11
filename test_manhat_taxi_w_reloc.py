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

visualize = True

# area_size_km = 10.0
# area_size = area_size_km * 1000.0

# requests_per_hour = [900, 1000, 1100, 1200, 1300]
# requests_per_hour = 700

# demand_Type = ["O_Uniform_D_Uniform"]   # "O_Cluster_D_Cluster",


fleet_sizes = [300]

assign_intervals = [20, 40]
relocate_intervals = [20, 40]

opt_methods = [
               "3_FCFS_smartNN",  "4_FCFS_drop_smartNN",  # "4a_FCFS_drop_smartNN2",
               "5_match_idleOnly", "6_match_idlePick",
               "7_match_idleDrop", "7_match_idleDrop2",
               "8_match_idlePickDrop"]

relocate_methods = ["Dandl", "NULL"]

xyt_strings = ["2x_8y_5min", "2x_8y_60min", "4x_16y_5min", "4x_16y_60min", "16x_64y_5min", "16x_64y_60min"]

i_date = "2016-04-01"

#######################################################################################################################
# Create Files to Write Results
#######################################################################################################################

csv_results2 = open(
    '../Results/Dandl_Hyland' + '_holds' + str(len(assign_intervals)) + '_fleet'
    + str(len(fleet_sizes)) + '_opt' + str(len(opt_methods)) + '.csv', 'w')
results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"',
                             quoting=csv.QUOTE_NONNUMERIC)
results_writer2.writerow(
    ["Runs", "Sim_Length", "Assign Interval", "Relocate Interval",
     "Space-Temp Aggregation",
     "Opt Method", "Reloc Method",  "Fleet Size",
     "Mean Wait Pick", "% Empty", "% Reassign", "Fleet Util",
     "#Served", "#inVeh", "#Assgnd", "#Unassgnd"])


#######################################################################################################################
# Loop Through Simulations
#######################################################################################################################
for k_assign_int in assign_intervals:
    for r_relocat_int in relocate_intervals:
        for d_xyt_string in xyt_strings:
            for m_opt_method in opt_methods:
                for rr_relocate_method in relocate_methods:
                    for j_fleet_size in fleet_sizes:
                        results_run = []
                        for i_run in range(0, 1):
                            # generate fleet
                            Init.generate_fleet(0.0, j_fleet_size, Set.veh_capacity)

                            print("run #:", i_run, " Space_temp Aggregation:", d_xyt_string)
                            print("fleet size:", j_fleet_size, " assign int:", k_assign_int, " Opt Method:", m_opt_method)

                            results = Main.main(k_assign_int, r_relocat_int, Set.t_max, Set.time_step,
                                                m_opt_method, rr_relocate_method, Set.veh_speed, i_date, True,
                                                d_xyt_string, visualize, false_forecast_f=None)

                            results_run.append(results)
                            print(results)
                            print(time.time() - t0)

                        avg = [float(sum(col)) / len(col) for col in zip(*results_run)]
                        results_writer2.writerow(
                            [i_run, Set.t_max, k_assign_int, r_relocat_int,
                             d_xyt_string, m_opt_method, rr_relocate_method, j_fleet_size,
                             avg[0], avg[1] , avg[2], avg[3],
                             avg[4], avg[5], avg[6], avg[7]])

csv_results2.close()
