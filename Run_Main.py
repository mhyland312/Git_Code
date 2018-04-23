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

area_size_miles = [8.0, 16.0]
area_size = [x * 5280.0 for x in area_size_miles]

# requests_per_hour = [900, 1000, 1100, 1200, 1300]
requests_per_hour = [1000]

demand_Type = ["O_Cluster_D_Cluster", "O_Uniform_D_Uniform" ]

fleet_size1 = [j for j in range(120, 151, 10)]
fleet_size2 = [j for j in range(175, 251, 25)]
fleet_size = fleet_size1 + fleet_size2

hold_for = [10]

opt_methods = ["1_FCFS_longestIdle", "2_FCFS_nearestIdle",
                    "3_FCFS_smartNN", "4_FCFS_drop_smartNN", "4a_FCFS_drop_smartNN2",
                    "5_match_idleOnly",
                    "6_match_idlePick", "7_match_idleDrop",
                    "8_match_idlePickDrop"]


#######################################################################################################################
# Create Files to Write Results
#######################################################################################################################

csv_results2 = open(
    '../Results_Rev2/BigResults_20miles' + '_holds' + str(len(hold_for)) + '_fleet'
    + str(len(fleet_size)) + '_opt' + str(len(opt_methods)) + '.csv', 'w')
results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"',
                             quoting=csv.QUOTE_NONNUMERIC)
results_writer2.writerow(
    ["Runs", "Sim_Length", "Hold Time", "Requests Per Hour",
     "Demand Type", "Area Size", "Opt Method",  "Fleet Size",
     "% Reassign",  "Mean Wait Pick", "% Empty", "Fleet Util",
     "#Served", "#inVeh", "#Assgnd", "#Unassgnd"])

#######################################################################################################################
# Loop Through Simulations
#######################################################################################################################


for a_demand_rate in requests_per_hour:
    for k_hold_for in hold_for:
        for p_demand_type in demand_Type: #hel
            for q_area_size in area_size:
                for m_opt_method in opt_methods:
                    for j_fleet_size in fleet_size:
                        jj_fleet_size = j_fleet_size + int(((q_area_size / 5280.0) - 4.0) * 25)

                        results_run = []
                        for i_run in range(0, 15):
                            # generate random demand
                            Init.generate_Demand(Set.T_max, a_demand_rate, q_area_size, Set.max_groupSize,
                                                p_demand_type)
                            # generate fleet
                            Init.generate_Fleet(q_area_size, jj_fleet_size, Set.veh_capacity)

                            print("run #:", i_run, " demand rate:", a_demand_rate, " demand type:", p_demand_type,
                                  " area size:", q_area_size / 5280)
                            print("fleet size:", jj_fleet_size, " hold for:", k_hold_for, " Opt Method:", m_opt_method)
                            results = Main.main(k_hold_for, Set.T_max, Set.time_step, m_opt_method, Set.veh_speed, 0, False)
                            results_run.append(results)
                            print(results)
                            print(time.time() - t0)

                        avg = [float(sum(col)) / len(col) for col in zip(*results_run)]
                        results_writer2.writerow(
                            [i_run, Set.T_max, k_hold_for, a_demand_rate,
                             p_demand_type, q_area_size/5280, m_opt_method, jj_fleet_size,
                             avg[0], avg[1] / 60.0, avg[2], avg[3],
                             avg[4], avg[5], avg[6], avg[7]])

csv_results2.close()
