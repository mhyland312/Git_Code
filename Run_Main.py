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

area_size_miles = [12.0]
area_size = [x * 5280.0 for x in area_size_miles]

# requests_per_hour = [900, 1000, 1100, 1200, 1300]
requests_per_hour = [1000]

demand_Type = ["O_Uniform_D_Uniform"]

fleet_size1 = [j for j in range(150, 171, 10)]
fleet_size2 = [j for j in range(175, 251, 25)]
fleet_size = [150] #fleet_size1 + fleet_size2

hold_for = [10]

opt_methods = [ "FCFS_smartNN", "FCFS_drop_smartNN",
               "match_idleOnly",  "match_idleDrop"]
            #"FCFS_longestIdle", "FCFS_nearestIdle","match_idlePick", , "match_idlePickDrop"

#######################################################################################################################
# Create Files to Write Results
#######################################################################################################################

csv_results2 = open(
    '../Results_Rev2/BigResults_20miles' + '_holds' + str(len(hold_for)) + '_fleet'
    + str(len(fleet_size)) + '_opt' + str(len(opt_methods)) + '.csv', 'w')
results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"',
                             quoting=csv.QUOTE_NONNUMERIC)
results_writer2.writerow(
    ["Run#", "Simulation Length", "Requests Per Hour", "Demand Type",
     "Area Size", "Opt Method", "Hold Time", "Fleet Size",
     "% Reassign",  "Mean Wait Pick", "% Empty", "Fleet Util",
     "#Served", "#inVeh", "#Assgnd", "#Unassgnd"])

#######################################################################################################################
# Loop Through Simulations
#######################################################################################################################

for i_run in range(0, 1):
    for a_demand_rate in requests_per_hour:
        for p_demand_type in demand_Type:
            for q_area_size in area_size:
                # generate random demand
                Init.generate_Demand(Set.T_max, a_demand_rate, q_area_size, Set.max_groupSize, p_demand_type)
                for j_fleet_size in fleet_size:
                    jj_fleet_size = j_fleet_size + int(((q_area_size / 5280.0) - 4.0) * 30)
                    # generate fleet
                    Init.generate_Fleet(q_area_size, jj_fleet_size, Set.veh_capacity)
                    for k_hold_for in hold_for:
                        for m_opt_method in opt_methods:
                            print("run #:", i_run, " demand rate:", a_demand_rate, " demand type:", p_demand_type,
                                  " area size:", q_area_size / 5280)
                            print("fleet size:", jj_fleet_size, " hold for:", k_hold_for, " Opt Method:", m_opt_method)
                            results = Main.main(k_hold_for, Set.T_max, Set.time_step, m_opt_method, Set.veh_speed, 0, False)
                            print(results)
                            results_writer2.writerow(
                                [i_run, Set.T_max, a_demand_rate, p_demand_type, q_area_size / 5280, m_opt_method,
                                 k_hold_for, jj_fleet_size, results])
                            print(time.time() - t0)

csv_results2.close()
